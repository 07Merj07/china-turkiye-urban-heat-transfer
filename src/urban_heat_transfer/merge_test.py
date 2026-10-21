"""Independent structural checks for the CityInfo-country merge."""
from __future__ import annotations
import pandas as pd


def validate_city_merge(cityinfo: pd.DataFrame, mapping: pd.DataFrame, merged: pd.DataFrame) -> list[dict]:
    checks = []
    def add(name, ok, value, detail):
        checks.append({"check": name, "status": "PASS" if ok else "FAIL", "value": value, "detail": detail})
    add("output row count preserved", len(merged) == len(cityinfo), len(merged), f"input rows={len(cityinfo)}")
    add("output UrbanId unique", "UrbanId" in merged and not merged["UrbanId"].duplicated().any(), merged["UrbanId"].nunique() if "UrbanId" in merged else "missing", "One row per CityInfo UrbanId.")
    add("allowed mapped country labels", set(merged["Country"].dropna().unique()).issubset({"China", "Türkiye"}) if "Country" in merged else False, sorted(merged["Country"].dropna().unique().tolist()) if "Country" in merged else "missing", "Country is assigned only when the ID is in the reviewed mapping.")
    expected = mapping.set_index("UrbanId")["Country"].to_dict()
    observed = merged.set_index("UrbanId")["Country"].to_dict() if {"UrbanId", "Country"}.issubset(merged.columns) else {}
    mismatches = [int(i) for i, country in expected.items() if observed.get(i) != country]
    add("all mapped countries preserved", not mismatches, len(mismatches), f"Mismatch UrbanIds (first 10): {mismatches[:10]}")
    add("unmapped city country remains blank", merged.loc[~merged["UrbanId"].isin(mapping["UrbanId"]), "Country"].isna().all() if "Country" in merged else False, int(merged.loc[~merged["UrbanId"].isin(mapping["UrbanId"]), "Country"].isna().sum()) if "Country" in merged else "missing", "No country is assigned by nearest-neighbour guessing.")
    return checks
