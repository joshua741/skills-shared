import unittest
from pathlib import Path
import gemini_video as gv


class TestPureHelpers(unittest.TestCase):
    def test_detect_source_youtube_watch(self):
        self.assertEqual(gv.detect_source("https://www.youtube.com/watch?v=abc123"), "youtube")

    def test_detect_source_youtube_short(self):
        self.assertEqual(gv.detect_source("https://youtu.be/abc123"), "youtube")

    def test_detect_source_other_url(self):
        self.assertEqual(gv.detect_source("https://example.com/video.mp4"), "url")

    def test_detect_source_local_file(self):
        self.assertEqual(gv.detect_source(r"C:\videos\clip.mp4"), "file")

    def test_slugify_basic(self):
        self.assertEqual(gv.slugify("Alex Hormozi: How to Scale!"), "alex-hormozi-how-to-scale")

    def test_slugify_collapses_and_trims(self):
        self.assertEqual(gv.slugify("  Multiple   Spaces -- here  "), "multiple-spaces-here")

    def test_slugify_truncates_long(self):
        out = gv.slugify("word " * 50)
        self.assertLessEqual(len(out), 60)
        self.assertFalse(out.endswith("-"))

    def test_report_filename(self):
        self.assertEqual(
            gv.report_filename("2026-06-02", "my-video"),
            "clip-2026-06-02-my-video.md",
        )

    def test_build_frontmatter_contains_fields(self):
        fm = gv.build_frontmatter(slug="my-video", filename="clip-2026-06-02-my-video.md",
                                   today_iso="2026-06-02")
        self.assertIn("name: clip-my-video", fm)
        self.assertIn("type: source", fm)
        self.assertIn("updated: 2026-06-02", fm)
        self.assertIn("sources: [clip-2026-06-02-my-video.md]", fm)
        self.assertTrue(fm.startswith("---\n"))
        self.assertTrue(fm.rstrip().endswith("---"))

    def test_write_report_creates_file(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            path = gv.write_report(Path(d), "clip-2026-06-02-x.md", "FRONT\n", "# Body\n")
            self.assertTrue(path.exists())
            content = path.read_text(encoding="utf-8")
            self.assertIn("FRONT", content)
            self.assertIn("# Body", content)

    def test_write_report_refuses_empty_body(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                gv.write_report(Path(d), "clip-2026-06-02-x.md", "FRONT\n", "   ")


if __name__ == "__main__":
    unittest.main()
