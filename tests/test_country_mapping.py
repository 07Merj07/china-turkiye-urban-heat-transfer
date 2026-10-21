import unittest
import sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from urban_heat_transfer.country_mapping import merge_city_country
from urban_heat_transfer.merge_test import validate_city_merge

class CountryMappingTests(unittest.TestCase):
    def setUp(self):
        self.city = pd.DataFrame({
            "UrbanId": [1, 2, 3],
            "Longitude": [100.0, 101.0, 102.0],
            "Latitude": [30.0, 31.0, 32.0],
            "Area": [10.0, 11.0, 12.0],
        })
        self.mapping = pd.DataFrame({
            "UrbanId": [1, 2],
            "Longitude": [100.0, 101.0],
            "Latitude": [30.0, 31.0],
            "Area": [10.0, 11.0],
            "Country": ["China", "Turkey"],
        })

    def test_merge_does_not_guess_unmapped_country(self):
        merged, audit, unmatched = merge_city_country(self.city, self.mapping)
        self.assertEqual(len(merged), 3)
        self.assertEqual(merged.loc[merged.UrbanId.eq(2), "Country"].iloc[0], "Türkiye")
        self.assertTrue(pd.isna(merged.loc[merged.UrbanId.eq(3), "Country"].iloc[0]))
        self.assertEqual(len(unmatched), 1)
        self.assertTrue(all(r["status"] in {"PASS", "INFO"} for r in audit))
        checks = validate_city_merge(self.city, self.mapping.assign(Country=["China", "Türkiye"]), merged)
        self.assertTrue(all(r["status"] == "PASS" for r in checks), checks)

    def test_duplicate_cityinfo_ids_fail(self):
        dup = pd.concat([self.city, self.city.iloc[[0]]], ignore_index=True)
        with self.assertRaises(ValueError):
            merge_city_country(dup, self.mapping)

    def test_coordinate_mismatch_fails_closed(self):
        bad = self.mapping.copy()
        bad.loc[0, "Latitude"] = 0.0
        with self.assertRaises(ValueError):
            merge_city_country(self.city, bad)

if __name__ == "__main__":
    unittest.main()
