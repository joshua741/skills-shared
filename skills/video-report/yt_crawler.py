#!/usr/bin/env python3
"""YouTube education crawler: weekly search → dedup → score → review-queue digest.
Stdlib-only except the yt-dlp CLI. Never ingests/transcribes automatically."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import gemini_video as gv  # reuse load_key, _post_json, API_BASE, MODEL_FLASH

SKILL_DIR = Path(__file__).resolve().parent
TOPICS_FILE = SKILL_DIR / "crawler_topics.txt"
LEDGER_FILE = SKILL_DIR / "crawler_seen.json"
QUEUE_DIR = Path.home() / "Documents" / "Business_Brain" / "review-queue"
RAW_DIR = Path.home() / "Documents" / "Business_Brain" / "raw"
DEFAULT_TOP_N = 10
DEFAULT_DAYS = 7
MIN_SEC = 180          # skip < 3 min (no upper bound: long videos segmented at ingest)
PER_QUERY = 12         # ytsearch ranks by relevance (often older), so cast a wider net to
                       # catch last-7-days uploads — but full extraction is slow, so 12 is
                       # the balance between recency yield and staying under the timeout


def load_topics(path: Path) -> list[str]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as e:  # missing/unreadable file must never crash a scheduled run
        print(f"[crawler] could not read topics file {path}: {e}", file=sys.stderr)
        return []
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            out.append(s)
    return out


_YT_ID_RE = re.compile(r"(?:youtube\.com/watch\?[^\s]*\bv=|youtu\.be/|youtube\.com/shorts/)"
                       r"([A-Za-z0-9_-]{11})")


def extract_video_id(url: str) -> str | None:
    """Pull the 11-char YouTube video ID from a watch/shorts/youtu.be URL, else None."""
    m = _YT_ID_RE.search(url or "")
    return m.group(1) if m else None


def ingested_video_ids(raw_dir: Path) -> set:
    """Scan already-ingested raw transcript files for YouTube video IDs so the crawler
    never re-surfaces a video that's already in the wiki. Missing dir → empty set."""
    ids = set()
    d = Path(raw_dir)
    if not d.exists():
        return ids
    for md in d.glob("*.md"):
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in _YT_ID_RE.finditer(text):
            ids.add(m.group(1))
    return ids


def load_ledger(path: Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}  # corrupt/missing → treat as empty (spec: not catastrophic)


def save_ledger(path: Path, ledger: dict) -> None:
    Path(path).write_text(json.dumps(ledger, indent=2), encoding="utf-8")


def dedup(candidates: list[dict], ledger: dict) -> list[dict]:
    return [c for c in candidates if c["id"] not in ledger]


def mark_seen(ledger: dict, candidates: list[dict], status: str, today_iso: str) -> None:
    for c in candidates:
        ledger[c["id"]] = {"status": status, "title": c.get("title", ""),
                           "date": today_iso}


def parse_ytdlp_json(lines: list[str]) -> list[dict]:
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        out.append({
            "id": d.get("id", ""),
            "title": d.get("title", ""),
            "channel": d.get("channel") or d.get("uploader", ""),
            "duration": d.get("duration"),
            "upload_date": d.get("upload_date", ""),
            "description": (d.get("description") or "")[:1000],
            "url": d.get("webpage_url") or f"https://www.youtube.com/watch?v={d.get('id','')}",
        })
    return out


def filter_duration(candidates: list[dict], min_sec: int,
                    max_sec: int | None = None) -> list[dict]:
    out = []
    for c in candidates:
        dur = c.get("duration")
        if dur is None:
            out.append(c)            # unknown duration: keep
        elif dur < min_sec:
            continue                 # too short: drop
        elif max_sec is not None and dur > max_sec:
            continue                 # over cap (only enforced when max_sec set)
        else:
            out.append(c)            # long videos kept; segmented at ingest
    return out


def filter_recent(candidates: list[dict], days: int, today_iso: str) -> list[dict]:
    """Keep candidates uploaded within `days` of today_iso. Belt-and-suspenders for
    --dateafter (which yt-dlp ignores under --flat-playlist). upload_date is a
    YYYYMMDD string; keep falsy/missing dates rather than over-dropping unknowns."""
    today = date.fromisoformat(today_iso)
    cutoff = (today - timedelta(days=days)).strftime("%Y%m%d")
    out = []
    for c in candidates:
        ud = c.get("upload_date")
        if not ud:
            out.append(c)            # unknown upload date: keep
        elif str(ud) >= cutoff:
            out.append(c)
    return out


def _dateafter(days: int) -> str:
    # yt-dlp accepts relative dates like "today-7days"
    return f"today-{days}days"


def run_search(query: str, n: int, days: int) -> list[dict]:
    """Search YouTube via yt-dlp (no API key). Returns parsed candidates, or [] on error."""
    # No --flat-playlist: yt-dlp ignores --dateafter and drops upload_date/duration/
    # description under flat mode. Full extraction returns real metadata and honors
    # --dateafter (code-side filter_recent is the belt-and-suspenders backup).
    args = [
        "yt-dlp", "--no-warnings", "--ignore-errors", "--dump-json",
        "--dateafter", _dateafter(days),
        f"ytsearch{n}:{query}",
    ]
    try:
        # Full extraction (per-video) is slow; 300s gives headroom for n~12 results.
        # On timeout/error the whole query degrades to [] (one topic lost, run continues).
        completed = subprocess.run(args, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=300)
    except Exception as e:  # one bad query never kills the run
        print(f"[crawler] search failed for {query!r}: {e}", file=sys.stderr)
        return []
    if completed.returncode != 0:
        print(f"[crawler] yt-dlp rc={completed.returncode} for {query!r}", file=sys.stderr)
        return []
    return parse_ytdlp_json(completed.stdout.splitlines())


SCORE_SYSTEM = """You score how relevant a YouTube video is to a real-estate
investor/operator's business: wholesaling, creative financing (subject-to, seller
finance, rent-to-own), raising private/transactional capital, GoHighLevel + AI
automation for real estate, and running a commercial cleaning business.
Return ONLY JSON: {"score": <0-10 integer>, "why": "<one short sentence>"}.
10 = directly actionable for this business; 0 = unrelated."""


def build_score_prompt(candidate: dict, topics: list[str]) -> str:
    return (f"{SCORE_SYSTEM}\n\nBusiness topics: {', '.join(topics)}\n\n"
            f"VIDEO:\nTitle: {candidate.get('title','')}\n"
            f"Channel: {candidate.get('channel','')}\n"
            f"Description: {candidate.get('description','')[:600]}\n")


def parse_score(text: str) -> tuple[int, str]:
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            d = json.loads(m.group(0))
            score = max(0, min(10, int(d.get("score", 0))))  # clamp 0–10
            return score, str(d.get("why", "")).strip() or "no reason given"
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    return 0, "unscored (could not parse model response)"


def score_candidate(key: str, candidate: dict, topics: list[str]) -> tuple[int, str]:
    """Score one candidate via Gemini Flash (title/desc only). Degrades to (0,...) on error."""
    endpoint = f"{gv.API_BASE}/models/{gv.MODEL_FLASH}:generateContent?key={key}"
    # thinkingBudget=0 disables Flash's thinking tokens so the small output budget isn't
    # consumed before any JSON is emitted (a thinking model + tiny maxOutputTokens returns
    # empty text). Scoring is a simple classification — no thinking needed.
    payload = {"contents": [{"parts": [{"text": build_score_prompt(candidate, topics)}]}],
               "generationConfig": {"temperature": 0.0, "maxOutputTokens": 512,
                                    "thinkingConfig": {"thinkingBudget": 0}}}
    try:
        resp = gv._post_json(endpoint, payload, timeout=60, max_attempts=3)
        return parse_score(gv._extract_text(resp))
    except Exception as e:
        print(f"[crawler] scoring failed for {candidate.get('id')}: {e}", file=sys.stderr)
        return 0, "unscored (API error)"


def rank_top(candidates: list[dict], n: int) -> list[dict]:
    return sorted(candidates, key=lambda c: c.get("score", 0), reverse=True)[:n]


def _fmt_duration(sec) -> str:
    if not sec:
        return "?"
    sec = int(sec)
    return f"{sec//60}:{sec%60:02d}"


def digest_filename(today_iso: str) -> str:
    return f"{today_iso}.md"


def render_digest(today_iso: str, items: list[dict]) -> str:
    head = (f"# Video Review Queue — {today_iso}\n\n"
            f"Check the ones to keep, then tell Claude `ingest items N,N,...` "
            f"(or `scan for new videos` to refresh).\n\n")
    if not items:
        return head + "No new matches this week.\n"
    rows = []
    for i, c in enumerate(items, 1):
        rows.append(
            f"- [ ] **{i}. {c.get('title','')}** — {c.get('channel','')} "
            f"({_fmt_duration(c.get('duration'))}) — **{c.get('score',0)}/10** "
            f"— {c.get('why','')}\n      {c.get('url','')}\n"
        )
    return head + "".join(rows)


def run_crawl(topics_file: Path, ledger_file: Path, queue_dir: Path,
              today_iso: str, top_n: int = DEFAULT_TOP_N, days: int = DEFAULT_DAYS,
              raw_dir: Path | None = None) -> Path:
    topics = load_topics(topics_file)
    ledger = load_ledger(ledger_file)

    # 0. no topics (missing/empty/unreadable file): write an empty digest, never crash
    if not topics:
        queue_dir.mkdir(parents=True, exist_ok=True)
        out = queue_dir / digest_filename(today_iso)
        out.write_text(render_digest(today_iso, []), encoding="utf-8")
        return out

    # 1. search every topic, collect candidates. Seed the within-run dedup set with video
    #    IDs already ingested into raw/ so the crawler never re-surfaces wiki content.
    seen_ids = ingested_video_ids(RAW_DIR if raw_dir is None else raw_dir)
    raw = []
    for q in topics:
        for c in run_search(q, PER_QUERY, days):
            if c["id"] and c["id"] not in seen_ids:
                seen_ids.add(c["id"]); raw.append(c)

    # 2. duration filter (no upper bound — long videos segmented at ingest) +
    #    recency filter (code-side backup for --dateafter) + dedup vs ledger
    recent = filter_recent(filter_duration(raw, MIN_SEC), days, today_iso)
    fresh = dedup(recent, ledger)

    # 3. score only fresh candidates
    if fresh:
        key = gv.load_key()
        for c in fresh:
            c["score"], c["why"] = score_candidate(key, c, topics)

    # 4. rank + render digest
    top = rank_top(fresh, top_n)
    queue_dir.mkdir(parents=True, exist_ok=True)
    out = queue_dir / digest_filename(today_iso)
    out.write_text(render_digest(today_iso, top), encoding="utf-8")

    # 5. mark every fresh candidate seen so it never resurfaces; persist ledger
    mark_seen(ledger, fresh, "seen", today_iso)
    save_ledger(ledger_file, ledger)

    # 6. append to rolling log
    log = queue_dir / "log.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"- [{today_iso}] scanned {len(topics)} topics, "
                f"{len(fresh)} new, {len(top)} shortlisted\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(prog="yt-crawler",
                                 description="Weekly YouTube education crawler → review queue.")
    ap.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS)
    args = ap.parse_args()
    today = date.today().isoformat()
    path = run_crawl(TOPICS_FILE, LEDGER_FILE, QUEUE_DIR, today, args.top_n, args.days)
    print(str(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
