#!/usr/bin/env python3
"""Exercise the natural-language transport and review interface, without generation."""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from natural_direction import check_bundle, compile_file, compile_markdown, validate_markdown_review, write_bundle


ROOT = Path(__file__).resolve().parents[1]
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a5d8AAAAASUVORK5CYII=")


class NaturalDirectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retain compiler fixtures; this suite never removes files.
        cls.evidence_root = Path(tempfile.mkdtemp(prefix="lightbox-natural-tests-")).resolve()
        print(f"Retained interface fixtures: {cls.evidence_root}")

    def setUp(self):
        self.base = self.evidence_root / self._testMethodName
        self.base.mkdir()
        self.first = self.base / "主体 图片.png"
        self.second = self.base / "reference.png"
        self.first.write_bytes(PNG)
        self.second.write_bytes(PNG)
        self.prompt = "Create a complete 16:9 overhead study. Image 1 supplies the finite subject. Image 2 supplies reflected lighting. Keep the paper and its image on one shared plane."
        self.text = f"# 本轮方向\n\n## 参考图片\n\n![主体](<{self.first.name}>)\n![拍法]({self.second.name})\n\n## 成像说明\n\n{self.prompt}\n\n## 工作记录\n\nInternal selection notes and user review remain here.\n"

    def compile(self, text=None):
        return compile_markdown(text or self.text, self.base)

    def test_order_and_literal_prompt_are_transported_together(self):
        job, evidence, _ = self.compile()
        self.assertEqual(job["prompt"], self.prompt)
        self.assertEqual(job["referenced_image_paths"], [str(self.first), str(self.second)])
        self.assertEqual([item["image_number"] for item in evidence["inputs"]], [1, 2])

    def test_operator_notes_stay_outside_actual_prompt(self):
        job, _, _ = self.compile()
        self.assertNotIn("Internal selection notes", job["prompt"])

    def test_relative_and_spaced_paths_become_replayable_absolute_paths(self):
        job, _, normalized = self.compile()
        replay, _, _ = compile_markdown(normalized, self.evidence_root)
        self.assertEqual(replay, job)

    def test_reference_order_follows_authored_image_list(self):
        swapped = self.text.replace(f"![主体](<{self.first.name}>)\n![拍法]({self.second.name})", f"![拍法]({self.second.name})\n![主体](<{self.first.name}>)")
        job, _, _ = self.compile(swapped)
        self.assertEqual(job["referenced_image_paths"], [str(self.second), str(self.first)])
        self.assertEqual(job["prompt"], self.prompt)

    def test_concept_omits_reference_argument(self):
        job, evidence, _ = self.compile("## 参考图片\n\n纯文字概念。\n\n## 成像说明\n\nCreate a finite ceramic model on a milky table.")
        self.assertEqual(set(job), {"prompt"})
        self.assertEqual(evidence["inputs"], [])

    def test_english_headings_preserve_subordinate_prompt_sections(self):
        text = self.text.replace("参考图片", "Reference images").replace("成像说明", "Image instructions")
        text = text.replace(self.prompt, self.prompt + "\n\n### Visible details\n\nThe fiber height crosses the ink boundary.")
        self.assertIn("### Visible details", self.compile(text)[0]["prompt"])

    def test_missing_image_fails_before_bundle_creation(self):
        direction = self.base / "direction.md"
        direction.write_text(self.text.replace(self.second.name, "missing.png"))
        output = self.base / "job-v1"
        with self.assertRaises(ValueError):
            write_bundle(direction, output)
        self.assertFalse(output.exists())

    def test_remote_reference_is_not_downloaded(self):
        with self.assertRaises(ValueError):
            self.compile(self.text.replace(self.second.name, "https://example.invalid/source.png"))

    def test_duplicate_file_does_not_create_ambiguous_roles(self):
        with self.assertRaises(ValueError):
            self.compile(self.text.replace(f"]({self.second.name})", f"](<{self.first.name}>)"))

    def test_missing_unused_and_out_of_range_numbers_fail(self):
        for prompt in (self.prompt.replace("Image 2", "Reference"), self.prompt + " Image 3 is another source.", self.prompt.replace("Image 1", "Image 0")):
            with self.subTest(prompt=prompt), self.assertRaises(ValueError):
                self.compile(self.text.replace(self.prompt, prompt))

    def test_both_language_sections_cannot_compete(self):
        with self.assertRaises(ValueError):
            self.compile(self.text + "\n## Image instructions\n\nAnother prompt.\n")

    def test_fenced_sample_paths_do_not_become_actual_references(self):
        with self.assertRaises(ValueError):
            self.compile(self.text.replace("## 参考图片\n", "## 参考图片\n```markdown\n"))

    def test_bundle_retains_prompt_sources_and_compilation_state(self):
        direction = self.base / "direction.md"
        direction.write_text(self.text)
        output = self.base / "job-v1"
        write_bundle(direction, output)
        self.assertTrue(check_bundle(output)["bundle_consistent"])
        self.assertEqual((output / "actual-prompt.txt").read_text(), self.prompt)
        evidence = json.loads((output / "compilation.json").read_text())
        self.assertEqual(evidence["image_generation"], "NOT_RUN")
        self.assertEqual(evidence["visual_review"], "UNVERIFIED")

    def test_existing_version_is_preserved(self):
        direction = self.base / "direction.md"
        direction.write_text(self.text)
        output = self.base / "job-v1"
        write_bundle(direction, output)
        before = (output / "image-job.json").read_bytes()
        with self.assertRaises(FileExistsError):
            write_bundle(direction, output)
        self.assertEqual((output / "image-job.json").read_bytes(), before)

    def test_changed_reference_bytes_are_detected(self):
        direction = self.base / "direction.md"
        direction.write_text(self.text)
        output = self.base / "job-v1"
        write_bundle(direction, output)
        self.first.write_bytes(PNG + b"changed fixture")
        with self.assertRaises(ValueError):
            check_bundle(output)

    def test_prompt_or_direction_edits_are_detected(self):
        direction = self.base / "direction.md"
        direction.write_text(self.text)
        output = self.base / "job-v1"
        write_bundle(direction, output)
        (output / "actual-prompt.txt").write_text("Another prompt")
        with self.assertRaises(ValueError):
            check_bundle(output)

    def test_cli_migration_keeps_existing_print_job_identical(self):
        original = ROOT / "assets/print-direction.example.json"
        direction = self.base / "migrated.md"
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/lightbox.py"), "migrate", str(original), "--output", str(direction)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        legacy = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/build_image_job.py"), str(original)], capture_output=True, text=True)
        self.assertEqual(compile_file(direction)[0], json.loads(legacy.stdout))


class NaturalReviewTests(unittest.TestCase):
    def record(self, statuses):
        rows = "\n".join(f"| 区域 {index} | 已有实际观察记录 | 对应核心要求 | {status} |" for index, status in enumerate(statuses, 1))
        return "## 核心观察\n\n| 检查位置 | 实际所见 | 应有结果 | 结论 |\n|---|---|---|---|\n" + rows

    def test_core_results_determine_overall_and_keep_acceptance_separate(self):
        for statuses, expected in ((["通过"], "PASS"), (["通过", "待确认"], "UNVERIFIED"), (["待确认", "需要修正"], "REVISE")):
            with self.subTest(statuses=statuses):
                result = validate_markdown_review(self.record(statuses))
                self.assertEqual(result["overall_status"], expected)
                self.assertFalse(result["user_acceptance_checked"])
                self.assertFalse(result["visual_quality_checked"])

    def test_conflicting_declared_summary_fails(self):
        with self.assertRaises(ValueError):
            validate_markdown_review(self.record(["需要修正"]) + "\n\n总体：通过\n")

    def test_invalid_status_incomplete_observation_and_separator_fail(self):
        for text in (self.record(["满意"]), self.record(["PASS"]).replace("已有实际观察记录", ""), self.record(["PASS"]).replace("|---|---|---|---|", "|---|---|---|")):
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate_markdown_review(text)

    def test_optional_comments_do_not_change_core_results(self):
        result = validate_markdown_review(self.record(["UNVERIFIED"]) + "\n\n## 其他观察\n\n| 装饰 | 清楚 | 可选 | PASS |\n")
        self.assertEqual(result["overall_status"], "UNVERIFIED")
        self.assertEqual(result["core_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
