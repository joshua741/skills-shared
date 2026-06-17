---
name: video-report
description: Use when the user wants to transcribe, summarize, or analyze a video (YouTube/web URL or local file) into a detailed report. Sends the whole video to Google Gemini 2.5, saves a structured report into Business_Brain/raw, and ingests it into the wiki.
---

# video-report

Turn a video into a detailed structured report using Gemini 2.5's native video
understanding, save it to the Business_Brain `raw/` folder, and ingest it into the wiki.

## Queue rule (CRITICAL — never run videos in parallel)

When the user gives **multiple** videos, process them **strictly one at a time, in order**:
run the engine for video 1 → fully ingest it into the wiki → only then start video 2, and
so on. Treat the list as a FIFO queue. NEVER fire multiple `gemini_video.py` calls in
parallel — Gemini's free tier caps input tokens per minute (≈250k for Flash), and parallel
30-min videos blow that limit instantly, returning HTTP 429 and silently dropping videos.
Sequential processing keeps every video under the limit. The engine also auto-retries 429s
and dropped connections with backoff, but the queue discipline is the primary safeguard.

If a video still fails after the engine's internal retries, report which one failed and
re-run just that one — do not skip it.

## Steps

1. Take the video source(s) from the user (YouTube/web URL or local video file path).
   If given several, build the queue and handle them one at a time per the Queue rule above.
2. Run the engine:
   ```
   python "C:\Users\joshu\.claude\skills\video-report\gemini_video.py" "<SOURCE>"
   ```
   - Default model is **Gemini 2.5 Flash** (works on the free tier, fast, accurate).
   - Add `--pro` for Gemini 2.5 Pro (max accuracy). Pro requires billing enabled on the
     API key's Google Cloud project — it is unavailable on the free tier (quota 0).
   - Clip a time window with `--start-sec N` and/or `--end-sec N` (seconds) to analyze
     only part of a video — e.g. `--start-sec 0 --end-sec 240` for the first 4 minutes.
     Works for YouTube, web URLs, and local files. Omit both to process the whole video.
   - The command prints the saved report path on stdout. Capture it.
3. Read the saved report and give the user a 3-5 line summary of what the video covered.
4. **Wiki ingest** (per Business_Brain CLAUDE.md rules): the report now lives in `raw/`,
   so ingest it.
   - Create/refresh a `source` page in `wiki/` for this report.
   - **Embed the FULL transcript verbatim into the wiki — do not drop any information.**
     The `source` page must contain the complete report (summary, key takeaways, frameworks,
     the entire timestamped transcript, quotes, on-screen visuals, action items), copied
     verbatim from the `raw/` file — not just a short summary or a pointer. The wiki must
     hold the full context inline so a separate session reading only the wiki has everything.
   - Create or update any entity / project / concept / person pages it touches; link with
     wikilinks.
   - Update `wiki/index.md`, append a line to `wiki/log.md`, update `wiki/.last-ingest`.
   - **Auto-ingest relevant videos without asking.** If a video is clearly relevant to
     Joshua's business/life, ingest it automatically (no confirmation needed). Only pause to
     ask when a video is clearly off-topic (e.g. a generic unrelated tutorial) — then confirm
     before polluting the wiki.

## Notes
- The Gemini key is read from `C:\Users\joshu\.claude\.gemini_key` (never printed/committed).
- YouTube URLs are sent directly to Gemini. Non-YouTube URLs and local files are
  downloaded/uploaded via the Files API automatically.
- The live vault is `C:\Users\joshu\Documents\Business_Brain` (the larger, active copy).
- If the engine exits with an error, surface it to the user; nothing is saved on failure.

## YouTube education crawler (weekly)

`yt_crawler.py` searches YouTube weekly for business-relevant videos and writes a
review-queue digest to `Business_Brain/review-queue/YYYY-MM-DD.md`. It NEVER ingests
automatically — it only searches, scores (title/description text only), and shortlists.

- **Topics:** `crawler_topics.txt` (editable, one search query per line; `#` comments).
- **Dedup ledger:** `crawler_seen.json` (every surfaced video ID, so nothing resurfaces).
- **Schedule:** weekly via the `WIH-YouTube-Crawler` Windows scheduled task (Mon 06:00).
- **Cost:** scoring is text-only (pennies); only Joshua-approved videos get transcribed.
- Run manually: `python "C:\Users\joshu\.claude\skills\video-report\yt_crawler.py"`
  (optional `--top-n N`, `--days N`).

**Verbs:**
- **"scan for new videos"** → run `yt_crawler.py`, then show the digest contents.
- **"ingest items N,N,..."** → for each chosen item, run `gemini_video.py` on its URL
  (segment long ones per the Queue rule above), then mark it `ingested` in
  `crawler_seen.json`. Mark the unchosen items `rejected` so they never resurface.
