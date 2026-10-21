"""Rebuild CityInfo_with_Country from the supplied CityInfo and city mapping table.

Country is assigned only from the reviewed UrbanId mapping. This module deliberately
never infers a country's identity from nearest-city proximity.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

REQUIRED_CITYINFO = {"UrbanId", "Longitude", "Latitude", "Area"}
REQUIRED_MAPPING = REQUIRED_CITYINFO | {"Country"}


def _normalise_ids(frame: pd.DataFrame, label: str) -> pd.DataFrame:
    df = frame.copy()
    if "UrbanId" not in df.columns:
        raise ValueError(f"{label} is missing UrbanId")
    ids = pd.to_numeric(df["UrbanId"], errors="coerce")
    if ids.isna().any() or ((ids % 1) != 0).any():
        raise ValueError(f"{label} has a missing or non-integer UrbanId")
    df["UrbanId"] = ids.astype("int64")
    if df["UrbanId"].duplicated().any():
        examples = df.loc[df["UrbanId"].duplicated(keep=False), "UrbanId"].head(10).tolist()
        raise ValueError(f"{label} has duplicate UrbanId values, examples={examples}")
    return df


def _canonical_country(value):
    if pd.isna(value):
        return None
    text = str(value).strip().casefold()
    if text in {"china", "prc", "people's republic of china"}:
        return "China"
    if text in {"türkiye", "turkiye", "turkey"}:
        return "Türkiye"
    return str(value).strip()


def merge_city_country(cityinfo: pd.DataFrame, mapping: pd.DataFrame, tolerance: float = 1e-6):
    """Return (merged_cityinfo, audit_rows, unmapped_cityinfo_rows)."""
    city = _normalise_ids(cityinfo, "CityInfo")
    mp = _normalise_ids(mapping, "city mapping")
    missing_city_cols = REQUIRED_CITYINFO - set(city.columns)
    missing_map_cols = REQUIRED_MAPPING - set(mp.columns)
    if missing_city_cols:
        raise ValueError(f"CityInfo missing columns: {sorted(missing_city_cols)}")
    if missing_map_cols:
        raise ValueError(f"city mapping missing columns: {sorted(missing_map_cols)}")
    mp["Country"] = mp["Country"].map(_canonical_country)
    bad_countries = sorted(set(mp["Country"].dropna()) - {"China", "Türkiye"})
    if bad_countries:
        raise ValueError(f"Unexpected mapping country labels: {bad_countries}")
    missing_mapping_ids = sorted(set(mp["UrbanId"]) - set(city["UrbanId"]))
    if missing_mapping_ids:
        raise ValueError(f"Mapping UrbanIds not found in CityInfo, examples={missing_mapping_ids[:10]}")

    overlap = mp.merge(city[["UrbanId", "Longitude", "Latitude", "Area"]], on="UrbanId", how="left", suffixes=("_map", "_city"), validate="one_to_one")
    coord_mismatches = []
    for col in ("Longitude", "Latitude", "Area"):
        left = pd.to_numeric(overlap[f"{col}_map"], errors="coerce")
        right = pd.to_numeric(overlap[f"{col}_city"], errors="coerce")
        bad = left.isna() | right.isna() | ((left - right).abs() > tolerance)
        if bad.any():
            coord_mismatches.extend(overlap.loc[bad, "UrbanId"].astype(int).tolist())
    if coord_mismatches:
        raise ValueError("Mapping and CityInfo disagree on coordinates/area for UrbanIds " + str(sorted(set(coord_mismatches))[:20]))

    country_map = mp[["UrbanId", "Country"]]
    merged = city.merge(country_map, on="UrbanId", how="left", validate="one_to_one", indicator=True)
    unmatched = merged.loc[merged["Country"].isna(), city.columns].copy()
    counts = merged["Country"].value_counts(dropna=False).to_dict()
    audit = [
        {"check": "CityInfo rows", "status": "PASS", "value": len(city), "detail": "Input rows preserved."},
        {"check": "CityInfo unique UrbanId", "status": "PASS", "value": city["UrbanId"].nunique(), "detail": "No duplicate keys."},
        {"check": "Mapping rows", "status": "PASS", "value": len(mp), "detail": "Reviewed country assignments."},
        {"check": "Mapping unique UrbanId", "status": "PASS", "value": mp["UrbanId"].nunique(), "detail": "No duplicate keys."},
        {"check": "Mapping IDs absent from CityInfo", "status": "PASS", "value": len(missing_mapping_ids), "detail": "All mapping IDs exist in CityInfo."},
        {"check": "Coordinate/area mismatches", "status": "PASS", "value": len(set(coord_mismatches)), "detail": f"Absolute tolerance={tolerance}; no automatic coordinate corrections."},
        {"check": "Country mapped: China", "status": "PASS", "value": int((merged["Country"] == "China").sum()), "detail": "Count from input mapping."},
        {"check": "Country mapped: Türkiye", "status": "PASS", "value": int((merged["Country"] == "Türkiye").sum()), "detail": "Count from input mapping."},
        {"check": "CityInfo records without an explicit country mapping", "status": "INFO", "value": len(unmatched), "detail": "Left blank; no nearest-country inference was performed."},
        {"check": "Merged row count preserved", "status": "PASS" if len(merged) == len(city) else "FAIL", "value": len(merged), "detail": "Expected one output row for each CityInfo row."},
    ]
    merged = merged.drop(columns=["_merge"])
    return merged, audit, unmatched


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cityinfo", type=Path, default=Path("data/reference/CityInfo.csv"))
    parser.add_argument("--mapping", type=Path, default=Path("data/external_features/China_Turkiye_city_mapping.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/CityInfo_with_Country.csv"))
    parser.add_argument("--audit", type=Path, default=Path("data/audit_reports/city_mapping_merge_audit.csv"))
    parser.add_argument("--unmatched", type=Path, default=Path("data/audit_reports/CityInfo_rows_without_country_mapping.csv"))
    args = parser.parse_args()
    city = pd.read_csv(args.cityinfo)
    mapping = pd.read_csv(args.mapping)
    merged, audit, unmatched = merge_city_country(city, mapping)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    args.unmatched.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(args.output, index=False)
    pd.DataFrame(audit).to_csv(args.audit, index=False)
    unmatched.to_csv(args.unmatched, index=False)
    print(f"Merged CityInfo: {args.output} ({len(merged):,} rows)")
    print(f"Audit report: {args.audit}")
    print(f"Rows without explicit country mapping: {len(unmatched):,} (left unassigned)")
    print("No original inputs were overwritten.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
