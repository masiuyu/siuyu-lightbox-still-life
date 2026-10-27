#!/usr/bin/env python3
"""Exercise native print contracts without generating or modifying images."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from build_image_job import build_job
from print_direction import _runtime, print_lines


ROOT = Path(__file__).resolve().parents[1]


class PrintDirectionTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "assets/print-direction.example.json").read_text())
        self.record = self.plan["design"]["print"]

    def compile(self):
        return build_job(self.plan, ROOT / "assets")

    def test_default_lightbox_keeps_transmission_and_native_arguments(self):
        plan = json.loads((ROOT / "assets/image-direction.example.json").read_text())
        job = build_job(plan, ROOT / "assets")
        self.assertEqual(set(job), {"prompt"})
        self.assertIn("dominant light from below", job["prompt"])
        self.assertNotIn("Print composition:", job["prompt"])

    def test_two_surfaces_keep_separate_processes_and_portrait_format(self):
        job = self.compile()
        self.assertEqual(set(job), {"prompt"})
        for phrase in ("9:16", "fern-carrier: screenprint_spot", "leaflet-paper: fine_uncoated_offset", "color separation spot", "color separation cmyk"):
            self.assertIn(phrase, job["prompt"])
        self.assertIn("deposited-ink thickness", job["prompt"])

    def test_carrier_color_is_independent_of_material(self):
        first = self.compile()["prompt"]
        self.record["carrier"]["base_rgb"] = [99, 50, 35]
        self.record["carrier"]["color_basis"] = "The user supplied this rust palette."
        second = self.compile()["prompt"]
        self.assertIn("tight_book_cloth", first)
        self.assertIn("tight_book_cloth", second)
        self.assertIn("[99, 50, 35]", second)
        self.assertNotEqual(first, second)

    def test_woven_carrier_rejects_transmitted_profile(self):
        self.plan["photography"]["profile"] = "transmitted_inventory"
        with self.assertRaisesRegex(ValueError, "reflected-light"):
            self.compile()

    def test_print_sources_must_be_content_sources(self):
        self.record["zones"][0]["sources"] = ["unbound-reference"]
        with self.assertRaisesRegex(ValueError, "content IDs"):
            self.compile()

    def test_bound_content_preserves_reference_order(self):
        self.plan["operation"] = "recompose"
        self.plan["inputs"] = [{
            "id": "botanical-source", "role": "subject",
            "path": "showcase/transmitted-paper.png",
            "observation": "Synthetic metadata for a path-order compiler check.",
            "use": "Identity source in this compiler fixture.",
            "content_analysis": {"relationships": "Fixture subject structure.", "target_scope": "Fixture silhouette only.", "basis": "Compiler fixture."},
            "preserve": ["The declared fixture silhouette."],
        }]
        self.plan["decisions"]["identity_sources"] = ["botanical-source"]
        self.plan["design"]["pairings"][0]["sources"] = ["botanical-source"]
        for zone in self.record["zones"]:
            zone["sources"] = ["botanical-source"]
        job = self.compile()
        self.assertEqual(job["referenced_image_paths"], [str((ROOT / "assets/showcase/transmitted-paper.png").resolve())])
        self.assertIn("Image 1 (botanical-source, subject)", job["prompt"])
        self.assertIn("sources: botanical-source", job["prompt"])

    def test_real_objects_retain_their_own_finish(self):
        self.record["zones"].append({"id": "steel-ruler", "surface": "real_object", "sources": [], "treatment": "A real steel ruler with readable dark and bright reflections."})
        self.assertIn("Use the declared object's physical finish.", self.compile()["prompt"])
        self.record["zones"][-1]["screen_mode"] = "fine_color_AM"
        with self.assertRaisesRegex(ValueError, "real_object uses its stated material"):
            self.compile()

    def test_monochrome_screen_rejects_cmyk_separation(self):
        self.record["zones"][1]["screen_mode"] = "fine_monochrome_AM"
        with self.assertRaisesRegex(ValueError, "color_separation"):
            self.compile()
        self.record["zones"][1]["color_separation"] = "monochrome"
        self.assertIn("color separation monochrome", self.compile()["prompt"])

    def test_duotone_is_a_deliberate_separation(self):
        self.record["zones"][1]["color_separation"] = "duotone"
        self.assertIn("color separation duotone", self.compile()["prompt"])

    def test_quantified_controls_reject_out_of_range_and_boolean(self):
        controls = self.record["zones"][0]["style_selection"]["control_overrides"]
        for invalid in (101, -1, True, 20.5):
            with self.subTest(value=invalid):
                controls["source_fidelity"] = invalid
                with self.assertRaises(ValueError):
                    self.compile()

    def test_art_direction_has_one_shared_preset(self):
        self.record["zones"][0]["style_selection"]["art_direction_preset"] = "pop_graphic"
        with self.assertRaisesRegex(ValueError, "share the selected"):
            self.compile()

    def test_each_catalog_process_can_compile_its_compatible_modes(self):
        catalog = _runtime("style_profiles").load_catalog()
        separation = {"fine_color_AM": "cmyk", "fine_monochrome_AM": "monochrome", "FM_stochastic": "cmyk", "spot_screenprint": "spot", "riso_spot_dither": "spot", "gravure_cells": "monochrome"}
        for process, profile in catalog["process_presets"].items():
            for mode in profile["allowed_screen_modes"]:
                with self.subTest(process=process, mode=mode):
                    record = copy.deepcopy(self.record)
                    record["layout"] = "object_prints"
                    record["zones"] = [record["zones"][1]]
                    record["zones"][0]["style_selection"]["process_preset"] = process
                    record["zones"][0]["screen_mode"] = mode
                    record["zones"][0]["color_separation"] = separation[mode]
                    self.assertTrue(print_lines(record, set(), "subject_study", {"profile": "print_editorial"}))

    def test_exact_copy_is_preserved_verbatim(self):
        self.record["layout"] = "typographic"
        self.record["zones"] = [{"id": "caption", "surface": "solid_ink", "sources": [], "treatment": "Authorized short caption on paper.", "exact_copy": "蕨叶 · STUDY 02"}]
        self.assertIn("Authorized visible copy, reproduce exactly: 蕨叶 · STUDY 02", self.compile()["prompt"])
        del self.record["zones"][0]["exact_copy"]
        with self.assertRaisesRegex(ValueError, "authorized exact_copy"):
            self.compile()

    def test_full_frame_requires_explicit_image_and_actual_source(self):
        self.record["layout"] = "full_frame"
        with self.assertRaisesRegex(ValueError, "explicit_image"):
            self.compile()
        self.plan["decisions"]["content_scope"]["kind"] = "explicit_image"
        with self.assertRaisesRegex(ValueError, "supplied content image"):
            self.compile()
        with self.assertRaisesRegex(ValueError, "source bound to a printed surface"):
            print_lines(self.record, {"original-photo"}, "explicit_image", {"profile": "print_editorial"})
        self.record["zones"][1]["sources"] = ["original-photo"]
        self.assertTrue(print_lines(self.record, {"original-photo"}, "explicit_image", {"profile": "print_editorial"}))

    def test_carrier_transfer_needs_a_carrier_ink_surface(self):
        self.record["zones"] = self.record["zones"][1:]
        with self.assertRaisesRegex(ValueError, "carrier_print surface"):
            self.compile()

    def test_material_and_rgb_are_checked(self):
        self.record["carrier"]["base_rgb"] = [True, 45, 66]
        with self.assertRaisesRegex(ValueError, "three integers"):
            self.compile()
        self.record["carrier"]["base_rgb"] = [99, 45, 66]
        self.record["carrier"]["material_id"] = "custom"
        with self.assertRaisesRegex(ValueError, "custom carrier.description"):
            self.compile()

    def test_duplicate_surfaces_and_unknown_fields_are_rejected(self):
        self.record["zones"].append(copy.deepcopy(self.record["zones"][0]))
        with self.assertRaisesRegex(ValueError, "IDs must be unique"):
            self.compile()
        self.record["zones"].pop()
        self.record["unrecognized"] = "value"
        with self.assertRaisesRegex(ValueError, "design.print needs fields"):
            self.compile()

    def test_input_record_is_not_mutated(self):
        before = copy.deepcopy(self.plan)
        self.compile()
        self.assertEqual(self.plan, before)


if __name__ == "__main__":
    unittest.main()
