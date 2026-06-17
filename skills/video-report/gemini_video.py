#!/usr/bin/env python3
"""video-report engine: send a video to Gemini 2.5 and write a structured report
into the Business_Brain raw/ folder. Stdlib-only (urllib/json/subprocess)."""
from __future__ import annotations

import argparse
import http.client
import json
import re
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

KEY_FILE = Path.home() / ".claude" / ".gemini_key"
DEFAULT_OUT_DIR = Path.home() / "Documents" / "Business_Brain" / "raw"
API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MODEL_PRO = "gemini-2.5-pro"
MODEL_FLASH = "gemini-2.5-flash"

# Media resolution controls how many tokens each video frame costs. LOW (~64 tokens/frame)
# keeps long videos under the free-tier 250k-tokens/minute input cap; the spoken-word
# transcript is unaffected by resolution (audio is tokenized separately). Default LOW so
# videos of any length ingest reliably on the free tier. Override with --high-res.
MEDIA_RESOLUTION = "MEDIA_RESOLUTION_LOW"


def _gen_config() -> dict:
    return {
        "temperature": 0.2,
        "maxOutputTokens": 65536,
        "mediaResolution": MEDIA_RESOLUTION,
    }


YOUTUBE_RE = re.compile(r"(youtube\.com/watch|youtu\.be/|youtube\.com/shorts/)", re.I)


def detect_source(source: str) -> str:
    """Return 'youtube', 'url', or 'file'."""
    if YOUTUBE_RE.search(source):
        return "youtube"
    if source.lower().startswith(("http://", "https://")):
        return "url"
    return "file"


def slugify(text: str, max_len: int = 60) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text


def report_filename(today_iso: str, slug: str) -> str:
    return f"clip-{today_iso}-{slug}.md"


def build_frontmatter(slug: str, filename: str, today_iso: str) -> str:
    return (
        "---\n"
        f"name: clip-{slug}\n"
        "type: source\n"
        "tags: [video, transcript]\n"
        "status: complete\n"
        f"sources: [{filename}]\n"
        f"updated: {today_iso}\n"
        "---\n"
    )


def write_report(out_dir: Path, filename: str, frontmatter: str, body: str) -> Path:
    """Write the report. Refuse to write an empty/thin body (would poison wiki ingest)."""
    if not body or not body.strip():
        raise ValueError("Refusing to write an empty report body.")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    path.write_text(frontmatter + "\n" + body.rstrip() + "\n", encoding="utf-8")
    return path


def load_key() -> str:
    if not KEY_FILE.exists():
        sys.exit(f"ERROR: Gemini key file not found at {KEY_FILE}. "
                 f"Create it containing only your API key.")
    key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        sys.exit(f"ERROR: Gemini key file {KEY_FILE} is empty.")
    return key


def get_metadata(source: str) -> dict:
    """Return {'title': str, 'duration': 'HH:MM:SS'} via yt-dlp --print, no download.
    Falls back to a generic title if yt-dlp can't read the source (e.g. local file)."""
    try:
        out = subprocess.run(
            ["yt-dlp", "--no-warnings", "--print", "%(title)s", "--print",
             "%(duration>%H:%M:%S)s", source],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60,
        )
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        if out.returncode == 0 and len(lines) >= 2:
            return {"title": lines[0].strip(), "duration": lines[1].strip()}
    except Exception:
        pass
    name = Path(source).stem if detect_source(source) == "file" else "video"
    return {"title": name or "video", "duration": "unknown"}


REPORT_PROMPT = """You are analyzing an entire video. Produce a detailed, accurate
markdown report with EXACTLY these sections and headers, in this order. Do not add a
top-level title (it is added separately). Be faithful to what is actually said and shown
— do not invent content.

## Summary
2-3 paragraphs covering what the video is about and its main thrust.

## Key Takeaways
- Bullet list of the most important, reusable points.

## Frameworks / SOPs
- Any named framework, process, model, or step-by-step method mentioned. Give the name
  and explain how it works. If none, write "None mentioned."

## Timestamped Transcript
A faithful transcript of the spoken content, segmented with [MM:SS] (or [HH:MM:SS] for
videos over an hour) timestamps roughly every 15-60 seconds or at each topic shift.

## Notable Quotes
- "Verbatim quote" — [MM:SS]

## On-screen Text & Visuals
- Significant on-screen text, slides, charts, demos, or visual actions, with timestamps.

## Action Items
- Concrete, actionable next steps implied by the content. If none, write "None."
"""


def _retry_delay_from_body(body: str, default: float) -> float:
    """Parse Gemini's 'Please retry in 59.5s' hint; fall back to default."""
    m = re.search(r"retry in ([\d.]+)s", body)
    if m:
        try:
            return float(m.group(1)) + 2.0  # small cushion
        except ValueError:
            pass
    return default


def _post_json(url: str, payload: dict, timeout: int = 600,
               max_attempts: int = 5) -> dict:
    """POST JSON with retries. Survives transient rate limits (HTTP 429),
    server errors (500/503), and dropped connections (RemoteDisconnected) with
    exponential backoff so videos are never silently dropped."""
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(1, max_attempts + 1):
        req = urllib.request.Request(url, data=data,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            retryable = e.code in (429, 500, 502, 503, 504)
            if retryable and attempt < max_attempts:
                delay = _retry_delay_from_body(body, default=min(60.0, 5 * 2 ** (attempt - 1)))
                print(f"[video-report] HTTP {e.code} (attempt {attempt}/{max_attempts}); "
                      f"waiting {delay:.0f}s then retrying...", file=sys.stderr)
                time.sleep(delay)
                continue
            raise RuntimeError(f"Gemini API HTTP {e.code}: {body[:500]}") from e
        except (urllib.error.URLError, http.client.HTTPException, ConnectionError,
                TimeoutError) as e:
            if attempt < max_attempts:
                delay = min(60.0, 5 * 2 ** (attempt - 1))
                print(f"[video-report] connection error ({type(e).__name__}: {e}); "
                      f"attempt {attempt}/{max_attempts}, waiting {delay:.0f}s...",
                      file=sys.stderr)
                time.sleep(delay)
                continue
            raise RuntimeError(f"Gemini API connection failed after "
                               f"{max_attempts} attempts: {e}") from e
    raise RuntimeError("Gemini API: exhausted all retry attempts.")


def _extract_text(resp: dict) -> str:
    try:
        parts = resp["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            _log_empty_reason(resp)
        return text
    except (KeyError, IndexError):
        _log_empty_reason(resp)
        return ""


def _log_empty_reason(resp: dict) -> None:
    """When Gemini returns no text, surface WHY (finishReason / safety / prompt block)
    so empty reports can be diagnosed instead of guessed at."""
    try:
        cand = (resp.get("candidates") or [{}])[0]
        reason = cand.get("finishReason", "?")
        safety = cand.get("safetyRatings")
        pf = resp.get("promptFeedback")
        msg = f"[video-report] empty response — finishReason={reason}"
        if pf:
            msg += f" promptFeedback={json.dumps(pf)[:200]}"
        if safety:
            blocked = [s for s in safety if s.get("blocked")]
            if blocked:
                msg += f" blockedSafety={json.dumps(blocked)[:200]}"
        print(msg, file=sys.stderr)
    except Exception:
        print(f"[video-report] empty response (unparseable): {json.dumps(resp)[:300]}",
              file=sys.stderr)


def _video_part(file_data: dict, start_sec: int | None, end_sec: int | None) -> dict:
    """Build a video part, optionally clipped to a [start, end] second window."""
    part = {"fileData": file_data}
    if start_sec is not None or end_sec is not None:
        vm: dict = {}
        if start_sec is not None:
            vm["startOffset"] = f"{start_sec}s"
        if end_sec is not None:
            vm["endOffset"] = f"{end_sec}s"
        part["videoMetadata"] = vm
    return part


def generate_from_youtube(key: str, model: str, url: str,
                          start_sec: int | None = None,
                          end_sec: int | None = None) -> str:
    endpoint = f"{API_BASE}/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": REPORT_PROMPT},
                _video_part({"fileUri": url}, start_sec, end_sec),
            ]
        }],
        "generationConfig": _gen_config(),
    }
    return _extract_text(_post_json(endpoint, payload))


def download_video(url: str, work_dir: Path) -> Path:
    work_dir.mkdir(parents=True, exist_ok=True)
    out_tmpl = str(work_dir / "video.%(ext)s")
    subprocess.run(["yt-dlp", "-f", "mp4/best", "-o", out_tmpl, url],
                   check=True, timeout=1800)
    files = list(work_dir.glob("video.*"))
    if not files:
        raise RuntimeError("yt-dlp produced no output file.")
    return files[0]


def _upload_file(key: str, path: Path) -> dict:
    """Resumable upload via the Files API. Returns the file resource dict."""
    num_bytes = path.stat().st_size
    mime = "video/mp4"
    # Resumable uploads MUST initiate against the /upload/ endpoint, not the
    # regular /v1beta/files endpoint -- otherwise no X-Goog-Upload-URL is returned.
    upload_base = API_BASE.replace("/v1beta", "/upload/v1beta")
    start = urllib.request.Request(
        f"{upload_base}/files?key={key}",
        data=json.dumps({"file": {"display_name": path.name}}).encode(),
        headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(num_bytes),
            "X-Goog-Upload-Header-Content-Type": mime,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(start, timeout=120) as resp:
        upload_url = resp.headers["X-Goog-Upload-URL"]
    if not upload_url:
        raise RuntimeError(
            "Files API did not return an X-Goog-Upload-URL (resumable upload init failed)."
        )
    upload = urllib.request.Request(
        upload_url, data=path.read_bytes(),
        headers={
            "Content-Length": str(num_bytes),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize",
        },
    )
    with urllib.request.urlopen(upload, timeout=1800) as resp:
        return json.loads(resp.read().decode())["file"]


def _wait_active(key: str, file_name: str, timeout: int = 600) -> dict:
    deadline = 0
    while deadline < timeout:
        with urllib.request.urlopen(
            f"{API_BASE}/{file_name}?key={key}", timeout=60
        ) as resp:
            info = json.loads(resp.read().decode())
        state = info.get("state")
        if state == "ACTIVE":
            return info
        if state == "FAILED":
            raise RuntimeError("Gemini file processing FAILED.")
        time.sleep(5)
        deadline += 5
    raise RuntimeError("Timed out waiting for Gemini to process the uploaded file.")


def generate_from_upload(key: str, model: str, file_uri: str, mime: str,
                         start_sec: int | None = None,
                         end_sec: int | None = None) -> str:
    endpoint = f"{API_BASE}/models/{model}:generateContent?key={key}"
    payload = {
        "contents": [{
            "parts": [
                {"text": REPORT_PROMPT},
                _video_part({"mimeType": mime, "fileUri": file_uri}, start_sec, end_sec),
            ]
        }],
        "generationConfig": _gen_config(),
    }
    return _extract_text(_post_json(endpoint, payload))


def build_report_body(title: str, source: str, duration: str, sections: str) -> str:
    return (f"# {title}\n"
            f"**Source:** {source}   **Duration:** {duration}\n\n"
            f"{sections.strip()}\n")


def _generate_with_retry(key: str, model: str, source: str, kind: str,
                         start_sec: int | None = None,
                         end_sec: int | None = None) -> str:
    """Generate report sections, retry once on the same model if output is thin."""
    def _run():
        if kind == "youtube":
            return generate_from_youtube(key, model, source, start_sec, end_sec)
        # url or file -> download (url) or use path (file), upload, generate
        from tempfile import mkdtemp
        work = Path(mkdtemp(prefix="video-report-"))
        local = download_video(source, work) if kind == "url" else Path(source)
        f = _upload_file(key, local)
        _wait_active(key, f["name"])
        return generate_from_upload(key, model, f["uri"], f.get("mimeType", "video/mp4"),
                                    start_sec, end_sec)

    text = _run()
    if len(text.strip()) < 200:
        text = _run()  # one retry
    return text


def main() -> int:
    ap = argparse.ArgumentParser(prog="video-report",
                                 description="Send a video to Gemini 2.5 and write a "
                                             "structured report into Business_Brain/raw.")
    ap.add_argument("source", help="YouTube/web URL or local video file path")
    ap.add_argument("--pro", action="store_true",
                    help="Use Gemini 2.5 Pro (max accuracy). Requires billing enabled "
                         "on the API key's project; Pro is unavailable on the free tier.")
    ap.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR),
                    help="Output dir (default: Business_Brain/raw).")
    ap.add_argument("--start-sec", type=int, default=None,
                    help="Clip start offset in seconds (analyze only from here).")
    ap.add_argument("--end-sec", type=int, default=None,
                    help="Clip end offset in seconds (analyze only up to here).")
    ap.add_argument("--high-res", action="store_true",
                    help="Use high media resolution (more tokens per frame, better "
                         "on-screen-text fidelity). May exceed the free-tier 250k "
                         "tokens/min cap on long videos. Default is low res.")
    ap.add_argument("--out-name", default=None,
                    help="Override the output slug (e.g. 'hieu-process-part1'). Use for "
                         "segmenting a long video into clips without filename collisions. "
                         "The file becomes clip-<date>-<out-name>.md.")
    args = ap.parse_args()

    global MEDIA_RESOLUTION
    if args.high_res:
        MEDIA_RESOLUTION = "MEDIA_RESOLUTION_HIGH"

    key = load_key()
    model = MODEL_PRO if args.pro else MODEL_FLASH
    kind = detect_source(args.source)
    print(f"[video-report] source kind: {kind} | model: {model}", file=sys.stderr)

    meta = get_metadata(args.source)
    print(f"[video-report] {meta['title']} ({meta['duration']})", file=sys.stderr)

    if args.start_sec is not None or args.end_sec is not None:
        print(f"[video-report] clip window: {args.start_sec}s -> {args.end_sec}s",
              file=sys.stderr)
    sections = _generate_with_retry(key, model, args.source, kind,
                                    args.start_sec, args.end_sec)
    if len(sections.strip()) < 200:
        sys.exit("ERROR: Gemini returned a thin/empty report after retry. Nothing saved.")

    today = date.today().isoformat()
    slug = slugify(args.out_name) if args.out_name else slugify(meta["title"])
    filename = report_filename(today, slug)
    body = build_report_body(meta["title"], args.source, meta["duration"], sections)
    frontmatter = build_frontmatter(slug, filename, today)
    path = write_report(Path(args.out_dir), filename, frontmatter, body)

    print(str(path))  # stdout = the saved path, for the skill to pick up
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
