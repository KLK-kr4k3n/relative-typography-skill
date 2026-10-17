"""Behavior checks for scale invariants and failure handling; stdlib only."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "skills/relative-typography/scripts/type_scale.py"
SPEC = importlib.util.spec_from_file_location("type_scale", SCRIPT)
SCALE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCALE)


class TypeScaleTests(unittest.TestCase):
    def test_unit_resolution_preserves_proportions(self):
        small = SCALE.make_scale("display", "mixed", 40, body_value=5, unit="mm")
        large = SCALE.make_scale("display", "mixed", 40, body_value=10, unit="mm")
        for role, token in small["tokens"].items():
            other = large["tokens"][role]
            self.assertEqual(token["ratio"], other["ratio"])
            self.assertAlmostEqual(other["resolved"]["font_size"],
                                   2 * token["resolved"]["font_size"], places=3)

    def test_body_does_not_shrink_with_container(self):
        for profile in SCALE.PROFILES:
            for width in (10, 20, 36, 60, 200):
                result = SCALE.make_scale(profile, "zh", width)
                self.assertEqual(result["tokens"]["body"]["ratio"], 1)
                self.assertGreater(result["tokens"]["title"]["ratio"],
                                   result["tokens"]["section"]["ratio"])

    def test_titles_increase_then_stop(self):
        for profile in SCALE.PROFILES:
            values = [SCALE.make_scale(profile, "mixed", x)["tokens"]["title"]["ratio"]
                      for x in (10, 20, 30, 40, 60, 100, 1000)]
            self.assertEqual(values, sorted(values))
            self.assertEqual(values[-1], values[-2])
            self.assertEqual(values[-2], values[-3])

    def test_local_title_geometry_does_not_resize_body(self):
        base = SCALE.make_scale("balanced", "mixed", 40)
        narrow = SCALE.make_scale("balanced", "mixed", 40, title_width_b=20)
        self.assertEqual(base["tokens"]["body"], narrow["tokens"]["body"])
        self.assertLess(narrow["tokens"]["title"]["ratio"], base["tokens"]["title"]["ratio"])

    def test_impossible_title_requests_reflow(self):
        base = SCALE.make_scale("balanced", "mixed", 24)
        result = SCALE.make_scale("balanced", "mixed", 24,
                                  title_advance_em=30, title_lines=2)
        self.assertEqual(result["title_fit"]["status"], "reflow_required")
        self.assertEqual(result["tokens"]["title"]["ratio"], base["tokens"]["title"]["ratio"])

    def test_measurable_title_can_reduce_within_interval(self):
        result = SCALE.make_scale("balanced", "en", 40,
                                  title_advance_em=46, title_lines=2)
        self.assertEqual(result["title_fit"]["status"], "estimated_fit")
        self.assertGreaterEqual(result["tokens"]["title"]["ratio"], 1.65)
        self.assertLess(result["tokens"]["title"]["ratio"], 1.825)
        self.assertTrue(result["title_fit"]["requires_render_check"])

    def test_readability_floor_raises_small_roles(self):
        result = SCALE.make_scale("compact", "zh", 24, minimum_ratio=1)
        self.assertTrue(all(t["ratio"] >= 1 for t in result["tokens"].values()))
        self.assertEqual(result["tokens"]["body"]["ratio"], 1)

    def test_cli_outputs_json_and_rejects_invalid_inputs(self):
        valid = subprocess.run([sys.executable, str(SCRIPT), "--width-b", "36"],
                               capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(valid.stdout)["schema_version"], "1.0")
        invalid_args = [
            ["--width-b", "nan"], ["--width-b", "inf"], ["--width-b", "0"],
            ["--width-b", "24", "--title-lines", "0"],
            ["--width-b", "24", "--minimum-ratio", "1.1"],
            ["--width-b", "24", "--body-value", "5"],
            ["--width-b", "24", "--unit", "mm"],
        ]
        for args in invalid_args:
            invalid = subprocess.run([sys.executable, str(SCRIPT), *args],
                                     capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0, args)
            self.assertEqual(invalid.stdout, "")


if __name__ == "__main__":
    unittest.main()
