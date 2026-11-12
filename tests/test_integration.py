"""Regression tests for the English adaptation and language/reference handoff."""
import contextlib
import copy
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build_prompt
import check_story
import gate
import run_shot


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.story = json.loads((ROOT / "examples/story.example.json").read_text())

    def save(self):
        (self.project / "story.json").write_text(json.dumps(self.story))

    def test_english_example_validates(self):
        errors, warnings = check_story.check(self.project, files=False, story=self.story)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_reference_numbers_follow_each_shots_upload_order(self):
        self.save()
        prompt, media = build_prompt.build(self.project, "S4", reference_tags=True)
        self.assertIn('@image1 says hoarsely: "Where did you get this watch?"', prompt)
        self.assertIn("@image2 answers", prompt)
        self.assertIn("Extend @video1", prompt)
        self.assertIn("@audio1", prompt)
        self.assertEqual(Path(media["ref_images"][0]).name, "char_chen.png")
        self.assertEqual(media["duration"], 24)

    def test_api_labels_do_not_leak_web_tags(self):
        self.save()
        prompt, _ = build_prompt.build(self.project, "S4")
        self.assertIn("Image 1 says hoarsely", prompt)
        self.assertNotIn("@image", prompt)

    def test_tagalog_dialogue_is_preserved_in_english_prompt(self):
        self.story["dialogue_language"] = "Tagalog"
        self.story["shots"][0]["dialogue"][0]["text"] = "Pa, puwede bang dito muna ako?"
        self.save()
        prompt, _ = build_prompt.build(self.project, "S1", True)
        self.assertIn("Dialogue in Tagalog", prompt)
        self.assertIn('"Pa, puwede bang dito muna ako?"', prompt)
        self.assertIn("Current state:", prompt)

    def test_latin_timing_counts_words_not_letters(self):
        shot = {"dialogue": [{"text": "Pa, puwede bang dito muna ako?"}]}
        self.assertAlmostEqual(check_story.speech_seconds(shot, {"speech_words_per_second": 2}), 3)
        shot["speech_words_per_second"] = 3
        self.assertAlmostEqual(check_story.speech_seconds(shot), 2)

    def test_invalid_speech_rate_is_rejected(self):
        for bad in (0, -1, True, "fast"):
            story = copy.deepcopy(self.story)
            story["speech_words_per_second"] = bad
            errors, _ = check_story.check(self.project, files=False, story=story)
            self.assertTrue(any("speech_words_per_second" in e for e in errors))

    def test_lastframe_has_no_reference_media_or_web_tags(self):
        shot = self.story["shots"][1]
        shot["link"] = "lastframe"
        shot["start_state_actual"] = "The rider holds the wrapped watch."
        self.save()
        prompt, media = build_prompt.build(self.project, "S2", True)
        self.assertEqual(media["ref_images"], [])
        self.assertEqual(media["ref_audios"], [])
        self.assertNotIn("@image", prompt)
        self.assertNotIn("@audio", prompt)
        self.assertIn("first frame", prompt)

    def test_actual_end_state_overrides_planned_state(self):
        self.story["shots"][0]["start_state_actual"] = "Ana holds the unlit lantern."
        self.save()
        prompt, _ = build_prompt.build(self.project, "S1")
        self.assertIn("Current state: Ana holds the unlit lantern. Maintain", prompt)

    def test_no_dialogue_does_not_invent_speech(self):
        self.save()
        prompt, _ = build_prompt.build(self.project, "S3")
        self.assertIn("No dialogue.", prompt)
        self.assertNotIn("Dialogue in", prompt)

    def test_dialogue_matching_handles_case_and_accents(self):
        ratio, _ = run_shot.best_ratio("Pa, nandito na ako!", "PA NANDITO NA AKO")
        self.assertEqual(ratio, 1)
        self.assertEqual(run_shot.norm("Café!"), "café")

    def test_committed_sources_have_no_untranslated_cjk_prose(self):
        paths = [*ROOT.glob("*.md"), *ROOT.glob("tools/*.py"), *ROOT.glob("tests/*.py"),
                 *ROOT.glob("docs/*.md"), *ROOT.glob("examples/*"), *ROOT.glob("skill-src/**/*")]
        for path in paths:
            if path.is_file() and path.suffix != ".pyc":
                self.assertIsNone(re.search(r"[\u4e00-\u9fff]", path.read_text()), str(path))


if __name__ == "__main__":
    unittest.main()
