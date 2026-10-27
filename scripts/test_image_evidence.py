#!/usr/bin/env python3
"""Exercise saved-call binding and native crop verification without generation."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from PIL import Image

from image_evidence import check_evidence, collect_evidence, write_evidence
from natural_direction import digest, write_bundle


ROOT = Path(__file__).resolve().parents[1]


class ImageEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="lightbox-image-evidence-tests-")).resolve()
        print(f"Retained evidence fixtures: {cls.root}")

    def setUp(self):
        self.base = self.root / self._testMethodName
        self.base.mkdir()
        self.first, self.second = self.base / 'source one.png', self.base / 'source two.png'
        Image.new('RGB', (20, 16), '#112233').save(self.first)
        Image.new('RGB', (20, 16), '#aabbcc').save(self.second)
        self.direction = self.base / 'direction.md'
        self.direction.write_text(f'## 参考图片\n\n![主体](<{self.first}>)\n![材料](<{self.second}>)\n\n## 成像说明\n\nImage 1 provides identity. Image 2 supplies the surface reference. Keep the specified opening readable.\n')
        self.bundle = self.base / 'compiled'
        write_bundle(self.direction, self.bundle)
        job = json.loads((self.bundle / 'image-job.json').read_text())
        self.arguments = {**job, 'transparent_background': False}
        self.call = self.base / 'tool-call.json'
        self.save_call()
        self.image = self.base / 'native.png'
        native = Image.new('RGB', (32, 24))
        native.putdata([(x * 7, y * 9, (x + y) * 4) for y in range(24) for x in range(32)])
        native.save(self.image)
        self.crop = self.base / 'native-detail.png'
        self.box = [5, 4, 21, 18]
        native.crop(tuple(self.box)).save(self.crop, compress_level=0)
        self.index = self.base / 'details.json'
        self.entries = [{'source': 'native.png', 'path': 'native-detail.png', 'box_xyxy_half_open': self.box}]
        self.save_index()
        self.review = self.base / 'review.md'
        self.review.write_text('## 核心观察\n\n| 检查位置 | 实际所见 | 应有结果 | 结论 |\n|---|---|---|---|\n| 全图 | 轮廓可辨 | 保持轮廓 | PASS |\n| 材料边缘 | 需要进一步观察 | 层序清楚 | UNVERIFIED |\n')
        self.execution = self.base / 'execution.md'
        self.execution.write_text('Fixture execution attachment; no image tool was called.\n')
        self.output = self.base / 'evidence.json'

    def save_call(self):
        self.call.write_text(json.dumps({'tool': 'image_gen.imagegen', 'arguments': self.arguments}))

    def save_index(self):
        self.index.write_text(json.dumps(self.entries))

    def collect(self):
        return collect_evidence(self.bundle, self.call, self.image, self.review, self.index, self.execution)

    def capture(self):
        return write_evidence(self.bundle, self.call, self.image, self.review, self.output, self.index, self.execution)

    def test_saved_call_and_exact_crop_keep_pending_visual_state(self):
        self.capture()
        result = check_evidence(self.output)
        self.assertEqual(result['recorded_visual_status'], 'UNVERIFIED')
        self.assertEqual(result['native_crops_checked'], 1)
        self.assertFalse(result['visual_quality_checked'])
        self.assertFalse(result['generation_authenticity_checked'])
        self.assertFalse(result['user_acceptance_checked'])

    def test_raw_argument_object_is_supported(self):
        self.call.write_text(json.dumps(self.arguments))
        self.assertTrue(self.collect()['checks']['tool_arguments_match_compiled_job'])

    def test_concept_call_can_omit_reference_arguments(self):
        self.direction.write_text('## 参考图片\n\nOriginal concept.\n\n## 成像说明\n\nA complete original ceramic vessel.\n')
        self.bundle = self.base / 'concept'
        write_bundle(self.direction, self.bundle)
        self.arguments = json.loads((self.bundle / 'image-job.json').read_text())
        self.save_call()
        self.assertTrue(self.collect()['checks']['tool_arguments_match_compiled_job'])

    def test_crop_check_is_explicitly_optional(self):
        result = collect_evidence(self.bundle, self.call, self.image, self.review)
        self.assertIsNone(result['checks']['native_crops_match'])
        self.assertEqual(result['details']['crops'], [])

    def test_missing_pillow_has_an_actionable_error(self):
        original_import = __import__
        def without_pillow(name, *args, **kwargs):
            if name == 'PIL':
                raise ImportError('fixture runtime has no Pillow')
            return original_import(name, *args, **kwargs)
        with patch('builtins.__import__', side_effect=without_pillow):
            with self.assertRaisesRegex(ValueError, 'runtime with Pillow'):
                self.collect()

    def test_wrong_prompt_stops_before_creating_receipt(self):
        self.arguments['prompt'] = 'A different subject and direction.'
        self.save_call()
        with self.assertRaisesRegex(ValueError, 'prompt differs'):
            self.capture()
        self.assertFalse(self.output.exists())

    def test_reference_order_and_conversation_mapping_are_checked(self):
        self.arguments['referenced_image_paths'].reverse()
        self.save_call()
        with self.assertRaisesRegex(ValueError, 'references differ'):
            self.collect()
        self.arguments['referenced_image_paths'].reverse()
        self.arguments['num_last_images_to_include'] = 1
        self.save_call()
        with self.assertRaisesRegex(ValueError, 'own mapping'):
            self.collect()

    def test_native_replacement_is_detected_even_at_the_same_size(self):
        self.capture()
        Image.new('RGB', (32, 24), '#000000').save(self.image)
        with self.assertRaisesRegex(ValueError, 'file changed'):
            check_evidence(self.output)

    def test_review_and_execution_edits_are_detected(self):
        self.capture()
        self.review.write_text(self.review.read_text() + '\nAdditional observation.\n')
        with self.assertRaisesRegex(ValueError, 'file changed'):
            check_evidence(self.output)
        self.review.write_text(self.review.read_text().replace('\nAdditional observation.\n', ''))
        self.execution.write_text('A different execution attachment.\n')
        with self.assertRaisesRegex(ValueError, 'file changed'):
            check_evidence(self.output)

    def test_execution_metadata_binds_native_copy_and_original_tool_file(self):
        original = self.base / 'tool-output.png'
        original.write_bytes(self.image.read_bytes())
        self.execution = self.base / 'execution.json'
        self.execution.write_text(json.dumps({'workspace_copy': {'path': str(self.image), 'sha256': digest(self.image.read_bytes()),
                                                                'dimensions': [32, 24]},
                                              'native_tool_path': str(original), 'review_record': str(self.review)}))
        result = self.collect()
        self.assertTrue(result['checks']['execution_copy_matches'])
        self.assertTrue(result['checks']['native_tool_copy_matches'])

    def test_execution_metadata_rejects_wrong_image_and_review(self):
        self.execution = self.base / 'execution.json'
        for copy, review in (({'path': str(self.first), 'sha256': digest(self.image.read_bytes())}, str(self.review)),
                            ({'path': str(self.image), 'sha256': '0' * 64}, str(self.review)),
                            ({'path': str(self.image), 'sha256': digest(self.image.read_bytes())}, str(self.direction))):
            self.execution.write_text(json.dumps({'workspace_copy': copy, 'review_record': review}))
            with self.subTest(copy=copy, review=review), self.assertRaises(ValueError):
                self.collect()

    def test_execution_start_time_and_standard_visual_summary_are_checked(self):
        self.execution = self.base / 'execution.json'
        self.call.write_text(json.dumps({'arguments': self.arguments, 'started_at': '2026-10-23 10:00 UTC'}))
        copy = {'path': str(self.image), 'sha256': digest(self.image.read_bytes())}
        for extra in ({'started_at': '2026-10-23 11:00 UTC'}, {'visual_review': 'PASS'}):
            self.execution.write_text(json.dumps({'workspace_copy': copy, **extra}))
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.collect()

    def test_changed_reference_is_detected(self):
        self.capture()
        Image.new('RGB', (20, 16), '#556677').save(self.first)
        with self.assertRaisesRegex(ValueError, 'file changed'):
            check_evidence(self.output)

    def test_reencoded_crop_can_match_pixels_before_capture(self):
        with Image.open(self.crop) as crop:
            crop.save(self.base / 'reencoded.png', compress_level=9)
        self.entries[0]['path'] = 'reencoded.png'
        self.save_index()
        self.assertTrue(self.collect()['checks']['native_crops_match'])

    def test_altered_and_resized_crops_are_rejected(self):
        Image.new('RGB', (16, 14), '#112233').save(self.crop)
        with self.assertRaisesRegex(ValueError, 'pixels differ'):
            self.collect()
        with Image.open(self.image) as image:
            image.crop(tuple(self.box)).resize((8, 7)).save(self.crop)
        with self.assertRaisesRegex(ValueError, 'pixels differ'):
            self.collect()

    def test_coordinates_use_integer_half_open_in_image_bounds(self):
        for box in ([-1, 4, 21, 18], [5, 4, 33, 18], [5, 4, 5, 18], [5.0, 4, 21, 18], [True, 4, 21, 18]):
            with self.subTest(box=box):
                self.entries[0]['box_xyxy_half_open'] = box
                self.save_index()
                with self.assertRaisesRegex(ValueError, 'coordinates'):
                    self.collect()

    def test_other_source_entries_are_counted_separately(self):
        self.entries.append({'source': 'source one.png', 'path': 'other-detail.png', 'box_xyxy_half_open': [0, 0, 1, 1]})
        self.save_index()
        result = self.collect()
        self.assertEqual(result['details']['other_source_entries'], 1)
        self.assertEqual(len(result['details']['crops']), 1)

    def test_index_requires_at_least_one_crop_from_current_image(self):
        self.entries[0]['source'] = 'source one.png'
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'no crops bound'):
            self.collect()

    def test_index_fingerprint_and_dimensions_must_agree(self):
        self.entries[0]['sha256'] = '0' * 64
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'fingerprint differs'):
            self.collect()
        self.entries[0].pop('sha256')
        self.entries[0]['size'] = [17, 14]
        self.save_index()
        with self.assertRaisesRegex(ValueError, 'dimensions differ'):
            self.collect()

    def test_receipt_inventory_must_keep_all_bound_files(self):
        self.capture()
        result = json.loads(self.output.read_text())
        result['files'].pop()
        self.output.write_text(json.dumps(result))
        with self.assertRaisesRegex(ValueError, 'inventory or recorded interpretation'):
            check_evidence(self.output)

    def test_existing_evidence_record_is_preserved(self):
        self.capture()
        before = self.output.read_bytes()
        with self.assertRaises(FileExistsError):
            self.capture()
        self.assertEqual(self.output.read_bytes(), before)

    def test_invalid_raster_is_rejected(self):
        self.image.write_text('This is a text file, not raster data.')
        with self.assertRaisesRegex(ValueError, 'cannot decode image'):
            self.collect()

    def test_cli_receipt_can_be_rechecked(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/lightbox.py'), 'evidence', str(self.bundle),
                                 '--call', str(self.call), '--image', str(self.image), '--review', str(self.review),
                                 '--detail-index', str(self.index), '--output', str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/lightbox.py'), 'check-evidence', str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['recorded_visual_status'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main(verbosity=2)
