import sys
from pathlib import Path
import unittest
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from urban_heat_transfer.country_mapping import merge_city_country

class SuppliedProjectDataTests(unittest.TestCase):
    def test_cityinfo_mapping_merge_invariants(self):
        city = pd.read_csv(ROOT / "data/reference/CityInfo.csv")
        mapping = pd.read_csv(ROOT / "data/external_features/China_Turkiye_city_mapping.csv")
        merged, audit, unmatched = merge_city_country(city, mapping)
        self.assertEqual(len(city), 10196)
        self.assertEqual(city.UrbanId.nunique(), 10196)
        self.assertEqual(len(mapping), 1634)
        self.assertEqual(mapping.UrbanId.nunique(), 1634)
        self.assertEqual(len(merged), len(city))
        self.assertEqual(int((merged.Country == "China").sum()), 1451)
        self.assertEqual(int((merged.Country == "Türkiye").sum()), 183)
        self.assertEqual(len(unmatched), 8562)
        self.assertTrue(all(row["status"] in {"PASS", "INFO"} for row in audit))

if __name__ == "__main__":
    unittest.main()
