import sys
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_uhi_sources as audit

class SourceFilenameRulesTests(unittest.TestCase):
    def test_expected_count_and_periods(self):
        self.assertEqual(len(audit.EXPECTED), 80)
        self.assertEqual(len(set(audit.EXPECTED)), 80)
        self.assertEqual(set(audit.PERIODS), {6, 7, 8, 22})
        self.assertIn("Mod2_Nig_2001_22.csv", audit.EXPECTED)
        self.assertIn("Mod2_Nig_2020_22.csv", audit.EXPECTED)

    def test_amod2_is_not_in_expected_inputs(self):
        self.assertFalse(any(name.startswith("AMod2_") for name in audit.EXPECTED))
        self.assertFalse(any(name.startswith("SMod2_") for name in audit.EXPECTED))

if __name__ == "__main__":
    unittest.main()
