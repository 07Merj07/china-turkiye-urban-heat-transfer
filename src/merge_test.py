"""Smoke-test the city mapping and one UHII dataset file.

This script reads project data and prints merge diagnostics. It does not write
or modify any data files.
"""

from pathlib import Path
import sys

import pandas as pd


# Resolve paths from this script's location so it can run from any folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
UHII_DIR = DATA_DIR / "UHII_dataset"

CITY_INFO_FILE = DATA_DIR / "CityInfo_with_Country.csv"
UHII_FILE = UHII_DIR / "AMod2_Day_2001_30.csv"

REQUIRED_CITY_COLUMNS = {
    "UrbanId", "Longitude", "Latitude", "Area", "Country"
}
REQUIRED_UHII_COLUMNS = {
    "UrbanId", "Intensity_EA", "Intensity_IEA",
    "Intensity_MEA", "Intensity_DEA"
}


def stop(message: str) -> None:
    """Print an error and stop without changing files."""
    sys.exit(f"ERROR: {message}")


if not CITY_INFO_FILE.is_file():
    stop(f"City-country mapping not found: {CITY_INFO_FILE}")

if not UHII_FILE.is_file():
    stop(
        f"UHII sample file not found: {UHII_FILE}\n"
        "Check that the dataset file exists under data/UHII_dataset/."
    )

city_info = pd.read_csv(CITY_INFO_FILE)
missing_city_columns = REQUIRED_CITY_COLUMNS.difference(city_info.columns)
if missing_city_columns:
    stop(f"City mapping is missing columns: {sorted(missing_city_columns)}")

uhii = pd.read_csv(UHII_FILE)
missing_uhii_columns = REQUIRED_UHII_COLUMNS.difference(uhii.columns)
if missing_uhii_columns:
    stop(f"UHII file is missing columns: {sorted(missing_uhii_columns)}")

# Restrict the mapping to the two countries in this study.
target_cities = city_info[
    city_info["Country"].isin(["China", "Türkiye"])
].copy()

if target_cities["UrbanId"].duplicated().any():
    stop("The China–Türkiye mapping contains duplicate UrbanId values.")

if uhii["UrbanId"].duplicated().any():
    stop("The UHII sample file contains duplicate UrbanId values.")

print("China + Türkiye urban units:", len(target_cities))
print("\nUHII sample shape:", uhii.shape)
print("UHII columns:", uhii.columns.tolist())

# Validate one-to-one matching to prevent accidental row multiplication.
merged = target_cities.merge(
    uhii,
    on="UrbanId",
    how="inner",
    validate="one_to_one",
)

print("\nMerged shape:", merged.shape)
print("\nFirst 5 merged rows:")
print(merged.head().to_string(index=False))

print("\nMissing UHII values in the merged sample:")
print(
    merged[
        [
            "Intensity_EA",
            "Intensity_IEA",
            "Intensity_MEA",
            "Intensity_DEA",
        ]
    ].isna().sum()
)

matched_ids = set(merged["UrbanId"])
unmatched_target_count = int(
    (~target_cities["UrbanId"].isin(matched_ids)).sum()
)
print(
    "\nTarget-country urban units without a match in this UHII file:",
    unmatched_target_count,
)

print("\nCheck complete. No files were written or modified.")
