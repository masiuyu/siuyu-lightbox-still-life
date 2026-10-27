#!/usr/bin/env python3
"""Check framing calculations and CLI behavior; retain every written fixture."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from framing_plan import analyze_plan, framing_report


ROOT = Path(__file__).resolve().parents[1]


def plan():
    return {"dimension_basis": "design_assumption", "unit": "mm", "output_px": [1600, 900],
            "view_size": [400, 225], "margin": 10,
            "items": [{"id": "paper", "center": [0, 0], "size": [100, 80]}],
            "details": [{"id": "line", "width": 0.2}]}


class FramingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="lightbox-framing-tests-")).resolve()
        print(f"Retained framing fixtures: {cls.root}")

    def setUp(self):
        self.base = self.root / self._testMethodName
        self.base.mkdir()

    def save(self, value=None):
        path = self.base / "plan.json"
        path.write_text(json.dumps(value if value is not None else plan()))
        return path

    def test_axis_aligned_edges_and_pixel_allocation(self):
        result = analyze_plan(plan())
        self.assertEqual(result["items"][0]["bounds_xyxy"], [-50, -40, 50, 40])
        self.assertEqual(result["items"][0]["edge_clearance"], {"left": 150, "right": 150, "top": 72.5, "bottom": 72.5})
        self.assertEqual(result["details"][0]["span_px_in_current_view"], 0.8)
        self.assertTrue(result["all_planned_margins_met"])
        self.assertFalse(result["visual_readability_evaluated"])
        self.assertFalse(result["dimension_basis_verified"])

    def test_right_angle_and_negative_angle_swap_dimensions(self):
        for angle in (90, -90, 450):
            value = plan(); value["items"][0]["rotation_deg"] = angle
            box = analyze_plan(value)["items"][0]["bounds_xyxy"]
            self.assertAlmostEqual(box[2] - box[0], 80)
            self.assertAlmostEqual(box[3] - box[1], 100)

    def test_rotated_bounds_match_independently_projected_corners(self):
        for angle in (-170, -70, 12, 15, 45, 135, 315):
            value = plan(); item = value["items"][0]
            item.update(center=[31, -7], size=[210, 297], rotation_deg=angle)
            a = math.radians(angle)
            corners = [complex(x, y) * complex(math.cos(a), math.sin(a)) + complex(31, -7)
                       for x in (-105, 105) for y in (-148.5, 148.5)]
            expected = [min(z.real for z in corners), min(z.imag for z in corners),
                        max(z.real for z in corners), max(z.imag for z in corners)]
            for actual, target in zip(analyze_plan(value)["items"][0]["bounds_xyxy"], expected):
                self.assertAlmostEqual(actual, target)

    def test_rotation_can_break_a_previously_fitting_frame(self):
        value = plan(); value.update(output_px=[260, 330], view_size=[260, 330], margin=0)
        value["items"][0]["size"] = [210, 297]
        self.assertTrue(analyze_plan(value)["all_planned_margins_met"])
        value["items"][0]["rotation_deg"] = 15
        result = analyze_plan(value)
        self.assertFalse(result["items"][0]["inside_view"])
        self.assertLess(result["items"][0]["edge_clearance"]["right"], 0)
        self.assertLess(result["items"][0]["edge_clearance"]["bottom"], 0)

    def test_positioned_items_form_a_union_instead_of_one_item_size(self):
        value = plan(); value["items"] = [{"id": "left", "center": [-150, 0], "size": [80, 40]},
                                          {"id": "right", "center": [180, 0], "size": [80, 40]}]
        result = analyze_plan(value)
        self.assertEqual(result["layout_bounds_xyxy"], [-190, -20, 220, 20])
        self.assertFalse(result["all_planned_margins_met"])
        self.assertTrue(result["items"][0]["planned_margin_met"])

    def test_aspect_fit_expands_without_stretching(self):
        value = plan(); value["view_size"] = [210, 297]
        result = analyze_plan(value)
        self.assertEqual(result["effective_view_size"][1], 297)
        self.assertAlmostEqual(result["effective_view_size"][0] / 297, 16 / 9)
        self.assertTrue(result["aspect_expansion_applied"])
        self.assertAlmostEqual(result["pixels_per_unit"], 900 / 297)

    def test_minimum_view_contains_layout_and_margin_about_same_origin(self):
        value = plan(); value["items"][0]["center"] = [180, 60]
        result = analyze_plan(value)
        value["view_size"] = result["minimum_centered_view_size_for_layout_and_margin"]
        self.assertTrue(analyze_plan(value)["all_planned_margins_met"])
        self.assertAlmostEqual(value["view_size"][0] / value["view_size"][1], 16 / 9)

    def test_scaling_every_length_preserves_pixels_and_geometry_state(self):
        first = plan(); second = copy.deepcopy(first); second["unit"] = "cm"
        second["view_size"] = [v / 10 for v in second["view_size"]]
        second["margin"] /= 10
        for item in second["items"]:
            for key in ("center", "size"):
                item[key] = [v / 10 for v in item[key]]
        for detail in second["details"]:
            detail["width"] /= 10
        a, b = analyze_plan(first), analyze_plan(second)
        self.assertEqual(a["all_planned_margins_met"], b["all_planned_margins_met"])
        self.assertAlmostEqual(a["details"][0]["span_px_in_current_view"], b["details"][0]["span_px_in_current_view"])

    def test_widening_view_reduces_detail_pixels_at_fixed_output(self):
        value = plan(); value["view_size"] = [420, 236.25]
        before = analyze_plan(value)["details"][0]["span_px_in_current_view"]
        value["view_size"] = [560, 315]
        after = analyze_plan(value)["details"][0]["span_px_in_current_view"]
        self.assertAlmostEqual(after / before, 0.75)

    def test_exact_border_allows_floating_point_rotation_roundoff(self):
        value = plan(); value.update(output_px=[80, 100], view_size=[80, 100], margin=0)
        value["items"][0]["rotation_deg"] = 90
        self.assertTrue(analyze_plan(value)["all_planned_margins_met"])

    def test_inside_view_and_requested_margin_are_different(self):
        value = plan(); value["items"][0]["center"] = [145, 0]
        value["margin"] = 10
        result = analyze_plan(value)
        self.assertTrue(result["items"][0]["inside_view"])
        self.assertFalse(result["items"][0]["planned_margin_met"])

    def test_nonfinite_boolean_and_zero_dimensions_are_rejected(self):
        for bad in (float("nan"), float("inf"), -1, 0, True, "100"):
            value = plan(); value["items"][0]["size"][0] = bad
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                analyze_plan(value)
        for key, bad in (("view_size", [0, 2]), ("output_px", [1600.0, 900]),
                         ("margin", -1), ("items", []), ("details", {})):
            value = plan(); value[key] = bad
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze_plan(value)

    def test_duplicate_ids_and_unknown_fields_are_rejected(self):
        for key in ("items", "details"):
            value = plan(); value[key].append(copy.deepcopy(value[key][0]))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                analyze_plan(value)
        value = plan(); value["view_szie"] = [1, 2]
        with self.assertRaisesRegex(ValueError, "unknown"):
            analyze_plan(value)
        value = plan(); value["items"][0]["angle"] = 30
        with self.assertRaisesRegex(ValueError, "unknown"):
            analyze_plan(value)

    def test_units_basis_and_coordinate_pairs_are_explicit(self):
        for key, bad in (("unit", "px"), ("dimension_basis", "verified"), ("basis_note", [])):
            value = plan(); value[key] = bad
            with self.assertRaises(ValueError):
                analyze_plan(value)
        value = plan(); value["items"][0]["center"] = [0]
        with self.assertRaises(ValueError):
            analyze_plan(value)

    def test_overflow_is_rejected_instead_of_serializing_infinity(self):
        value = plan(); value["items"][0]["center"] = [1e308, 1e308]
        with self.assertRaises(ValueError):
            analyze_plan(value)

    def test_output_binds_exact_input_and_preserves_existing_file(self):
        source = self.save(); output = self.base / "report.json"
        result = framing_report(source, output)
        self.assertEqual(result["plan_file"]["sha256"], hashlib.sha256(source.read_bytes()).hexdigest())
        before = output.read_bytes()
        with self.assertRaises(FileExistsError):
            framing_report(source, output)
        self.assertEqual(output.read_bytes(), before)

    def test_invalid_plan_writes_no_report(self):
        value = plan(); value["margin"] = -1
        source = self.save(value); output = self.base / "report.json"
        with self.assertRaises(ValueError):
            framing_report(source, output)
        self.assertFalse(output.exists())

    def test_duplicate_json_keys_are_rejected(self):
        source = self.base / "plan.json"
        source.write_text('{"unit":"mm","unit":"cm"}')
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            framing_report(source)

    def test_cli_success_with_margin_shortfall_is_a_calculation_result(self):
        value = plan(); value["items"][0]["center"] = [1000, 0]
        source = self.save(value)
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/lightbox.py"), "framing", str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(result.stdout)
        self.assertFalse(record["all_planned_margins_met"])
        self.assertEqual(record["state"], "PLANNING_ESTIMATE")
        self.assertEqual(record["image_generation"], "NOT_RUN")

    def test_cli_invalid_input_has_structured_error_and_no_report(self):
        value = plan(); value["output_px"] = [False, 900]
        source = self.save(value); output = self.base / "report.json"
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/lightbox.py"), "framing", str(source), "--output", str(output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
