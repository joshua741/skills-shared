import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import yt_crawler as yc


class TestTopics(unittest.TestCase):
    def test_load_topics_skips_comments_and_blanks(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "topics.txt"
            p.write_text("# comment\nwholesale\n\n  subject to  \n# another\n", encoding="utf-8")
            self.assertEqual(yc.load_topics(p), ["wholesale", "subject to"])


class TestLedger(unittest.TestCase):
    def test_load_missing_ledger_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(yc.load_ledger(Path(d) / "nope.json"), {})

    def test_save_then_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "seen.json"
            yc.save_ledger(p, {"abc": {"status": "seen"}})
            self.assertEqual(yc.load_ledger(p), {"abc": {"status": "seen"}})

    def test_dedup_drops_seen_ids(self):
        ledger = {"seen1": {"status": "seen"}}
        cands = [{"id": "seen1"}, {"id": "new1"}]
        self.assertEqual(yc.dedup(cands, ledger), [{"id": "new1"}])

    def test_mark_seen_sets_status(self):
        ledger = {}
        yc.mark_seen(ledger, [{"id": "x", "title": "T"}], "seen", "2026-06-03")
        self.assertEqual(ledger["x"]["status"], "seen")
        self.assertEqual(ledger["x"]["title"], "T")
        self.assertEqual(ledger["x"]["date"], "2026-06-03")


class TestParseAndFilter(unittest.TestCase):
    def test_parse_ytdlp_jsonlines(self):
        lines = [
            json.dumps({"id": "a", "title": "T1", "channel": "C1",
                        "duration": 600, "upload_date": "20260601",
                        "description": "d", "webpage_url": "https://y/a"}),
            "",  # blank line ignored
            json.dumps({"id": "b", "title": "T2", "channel": "C2",
                        "duration": 60, "upload_date": "20260602",
                        "description": "d2", "webpage_url": "https://y/b"}),
        ]
        out = yc.parse_ytdlp_json(lines)
        self.assertEqual(len(out), 2)
        self.assertEqual(out[0]["id"], "a")
        self.assertEqual(out[0]["url"], "https://y/a")

    def test_filter_by_duration_drops_too_short(self):
        cands = [{"id": "a", "duration": 600}, {"id": "b", "duration": 60}]
        out = yc.filter_duration(cands, min_sec=180, max_sec=5400)
        self.assertEqual([c["id"] for c in out], ["a"])

    def test_filter_keeps_missing_duration(self):
        # live streams / unknown duration: keep, let relevance decide
        cands = [{"id": "a", "duration": None}]
        self.assertEqual(len(yc.filter_duration(cands, 180, 5400)), 1)

    def test_filter_keeps_long_video_when_no_max(self):
        # >90 min videos must still reach the digest (segmented at ingest);
        # only the short ones get dropped when max_sec is None.
        cands = [{"id": "long", "duration": 7200}, {"id": "short", "duration": 60}]
        out = yc.filter_duration(cands, min_sec=180)
        self.assertEqual([c["id"] for c in out], ["long"])


class TestRecency(unittest.TestCase):
    def test_filter_recent_keeps_recent_drops_old_keeps_none(self):
        cands = [
            {"id": "recent", "upload_date": "20260601"},
            {"id": "old", "upload_date": "20250101"},
            {"id": "unknown", "upload_date": None},
        ]
        out = yc.filter_recent(cands, days=7, today_iso="2026-06-03")
        self.assertEqual({c["id"] for c in out}, {"recent", "unknown"})


class TestSearch(unittest.TestCase):
    def test_run_search_builds_correct_ytdlp_args_and_parses(self):
        fake = json.dumps({"id": "a", "title": "T", "channel": "C",
                           "duration": 600, "upload_date": "20260601",
                           "description": "d", "webpage_url": "https://y/a"})
        completed = mock.Mock(returncode=0, stdout=fake + "\n")
        with mock.patch("yt_crawler.subprocess.run", return_value=completed) as m:
            out = yc.run_search("wholesale", n=5, days=7)
        args = m.call_args[0][0]
        self.assertIn("ytsearch5:wholesale", args)
        self.assertTrue(any("--dateafter" in a for a in args))
        self.assertEqual(out[0]["id"], "a")

    def test_run_search_returns_empty_on_failure(self):
        with mock.patch("yt_crawler.subprocess.run",
                        side_effect=Exception("boom")):
            self.assertEqual(yc.run_search("x", 5, 7), [])


class TestScoring(unittest.TestCase):
    def test_build_score_prompt_includes_title_and_topics(self):
        cand = {"title": "Wholesaling 101", "channel": "C", "description": "learn"}
        p = yc.build_score_prompt(cand, ["wholesale", "subject to"])
        self.assertIn("Wholesaling 101", p)
        self.assertIn("wholesale", p)

    def test_parse_score_reads_json(self):
        score, why = yc.parse_score('{"score": 8, "why": "directly on wholesale"}')
        self.assertEqual(score, 8)
        self.assertEqual(why, "directly on wholesale")

    def test_parse_score_handles_fenced_json(self):
        score, why = yc.parse_score('```json\n{"score": 3, "why": "tangential"}\n```')
        self.assertEqual(score, 3)

    def test_parse_score_bad_input_returns_zero(self):
        score, why = yc.parse_score("not json at all")
        self.assertEqual(score, 0)
        self.assertIn("unscored", why.lower())

    def test_parse_score_clamps_out_of_range(self):
        self.assertEqual(yc.parse_score('{"score": 99, "why": "x"}')[0], 10)
        self.assertEqual(yc.parse_score('{"score": -5, "why": "x"}')[0], 0)


class TestRankAndDigest(unittest.TestCase):
    def test_rank_top_sorts_by_score_desc_and_caps(self):
        cands = [{"id": "a", "score": 3}, {"id": "b", "score": 9},
                 {"id": "c", "score": 7}]
        out = yc.rank_top(cands, 2)
        self.assertEqual([c["id"] for c in out], ["b", "c"])

    def test_render_digest_contains_items_and_checkboxes(self):
        items = [{"id": "a", "title": "Wholesaling 101", "channel": "C1",
                  "duration": 600, "url": "https://y/a", "score": 9,
                  "why": "on point"}]
        md = yc.render_digest("2026-06-03", items)
        self.assertIn("# Video Review Queue — 2026-06-03", md)
        self.assertIn("- [ ]", md)
        self.assertIn("Wholesaling 101", md)
        self.assertIn("https://y/a", md)
        self.assertIn("9/10", md)

    def test_render_digest_empty_week(self):
        md = yc.render_digest("2026-06-03", [])
        self.assertIn("No new matches", md)

    def test_digest_filename(self):
        self.assertEqual(yc.digest_filename("2026-06-03"), "2026-06-03.md")


class TestRunCrawl(unittest.TestCase):
    def test_run_crawl_writes_digest_and_updates_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            topics = Path(d) / "topics.txt"; topics.write_text("wholesale\n", encoding="utf-8")
            ledger = Path(d) / "seen.json"
            qdir = Path(d) / "queue"
            cand = {"id": "vid1", "title": "Wholesaling 101", "channel": "C",
                    "duration": 600, "upload_date": "20260601",
                    "description": "d", "url": "https://y/vid1"}
            with mock.patch("yt_crawler.run_search", return_value=[cand]), \
                 mock.patch("yt_crawler.score_candidate", return_value=(9, "on point")), \
                 mock.patch("yt_crawler.gv.load_key", return_value="k"):
                path = yc.run_crawl(topics_file=topics, ledger_file=ledger,
                                    queue_dir=qdir, today_iso="2026-06-03",
                                    top_n=10, days=7, raw_dir=Path(d) / "no_raw")
            self.assertTrue(Path(path).exists())
            self.assertIn("Wholesaling 101", Path(path).read_text(encoding="utf-8"))
            self.assertEqual(yc.load_ledger(ledger)["vid1"]["status"], "seen")

    def test_run_crawl_skips_already_seen(self):
        with tempfile.TemporaryDirectory() as d:
            topics = Path(d) / "topics.txt"; topics.write_text("wholesale\n", encoding="utf-8")
            ledger = Path(d) / "seen.json"
            yc.save_ledger(ledger, {"vid1": {"status": "ingested"}})
            qdir = Path(d) / "queue"
            cand = {"id": "vid1", "title": "Old", "channel": "C", "duration": 600,
                    "upload_date": "20260601", "description": "d", "url": "https://y/vid1"}
            with mock.patch("yt_crawler.run_search", return_value=[cand]), \
                 mock.patch("yt_crawler.score_candidate", return_value=(9, "x")) as sc, \
                 mock.patch("yt_crawler.gv.load_key", return_value="k"):
                path = yc.run_crawl(topics_file=topics, ledger_file=ledger,
                                    queue_dir=qdir, today_iso="2026-06-03", top_n=10, days=7)
            sc.assert_not_called()  # deduped before scoring
            self.assertIn("No new matches", Path(path).read_text(encoding="utf-8"))

    def test_run_crawl_missing_topics_file_writes_empty_digest(self):
        with tempfile.TemporaryDirectory() as d:
            topics = Path(d) / "does_not_exist.txt"  # never created
            ledger = Path(d) / "seen.json"
            qdir = Path(d) / "queue"
            path = yc.run_crawl(topics_file=topics, ledger_file=ledger,
                                queue_dir=qdir, today_iso="2026-06-03",
                                top_n=10, days=7)
            self.assertTrue(Path(path).exists())
            self.assertIn("No new matches", Path(path).read_text(encoding="utf-8"))


class TestLoadTopicsGuard(unittest.TestCase):
    def test_load_topics_missing_file_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(yc.load_topics(Path(d) / "nope.txt"), [])


class TestIngestedDedup(unittest.TestCase):
    def test_extract_video_id_variants(self):
        self.assertEqual(yc.extract_video_id("https://www.youtube.com/watch?v=0WDkwMxj13s"), "0WDkwMxj13s")
        self.assertEqual(yc.extract_video_id("https://www.youtube.com/watch?v=0WDkwMxj13s&t=10s"), "0WDkwMxj13s")
        self.assertEqual(yc.extract_video_id("https://youtu.be/0WDkwMxj13s"), "0WDkwMxj13s")
        self.assertEqual(yc.extract_video_id("https://www.youtube.com/shorts/0WDkwMxj13s"), "0WDkwMxj13s")
        self.assertIsNone(yc.extract_video_id("https://example.com/not-youtube"))

    def test_ingested_video_ids_scans_raw_files(self):
        with tempfile.TemporaryDirectory() as d:
            raw = Path(d) / "raw"; raw.mkdir()
            (raw / "clip-a.md").write_text(
                "**Source:** https://www.youtube.com/watch?v=0WDkwMxj13s   **Duration:** 28:57\n",
                encoding="utf-8")
            (raw / "clip-b.md").write_text("no url here", encoding="utf-8")
            self.assertEqual(yc.ingested_video_ids(raw), {"0WDkwMxj13s"})

    def test_ingested_video_ids_missing_dir_returns_empty(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(yc.ingested_video_ids(Path(d) / "nope"), set())

    def test_run_crawl_skips_already_ingested_video(self):
        with tempfile.TemporaryDirectory() as d:
            topics = Path(d) / "topics.txt"; topics.write_text("wholesale\n", encoding="utf-8")
            ledger = Path(d) / "seen.json"
            qdir = Path(d) / "queue"
            raw = Path(d) / "raw"; raw.mkdir()
            (raw / "clip-x.md").write_text(
                "**Source:** https://www.youtube.com/watch?v=already1234\n", encoding="utf-8")
            cand = {"id": "already1234", "title": "Dup", "channel": "C", "duration": 600,
                    "upload_date": "20260601", "description": "d", "url": "https://y/already1234"}
            with mock.patch("yt_crawler.run_search", return_value=[cand]), \
                 mock.patch("yt_crawler.score_candidate", return_value=(9, "x")) as sc, \
                 mock.patch("yt_crawler.gv.load_key", return_value="k"):
                path = yc.run_crawl(topics_file=topics, ledger_file=ledger, queue_dir=qdir,
                                    today_iso="2026-06-03", top_n=10, days=7, raw_dir=raw)
            sc.assert_not_called()  # already in raw/ → excluded before scoring
            self.assertIn("No new matches", Path(path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
