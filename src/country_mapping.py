"""Create the city-to-country mapping used by the China–Türkiye UHII project.

Primary rule:
    Assign a country only when a city point falls within a country polygon.

Unmatched points are inspected using nearest-country distances, but these
candidates are diagnostic only and are NEVER added to the primary mapping.
"""

from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd


# --------------------------------------------------
# 1. Resolve project paths (works regardless of the current terminal folder)
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

INPUT_FILE = DATA_DIR / "CityInfo.csv"
MAPPING_FILE = DATA_DIR / "CityInfo_with_Country.csv"
TARGET_MAPPING_FILE = DATA_DIR / "China_Turkiye_city_mapping.csv"
UNMATCHED_FILE = DATA_DIR / "unmatched_cities.csv"
NEAREST_COUNTRY_FILE = DATA_DIR / "unmatched_nearest_country.csv"

# Natural Earth country boundaries used by the original mapping workflow.
COUNTRY_BOUNDARIES_URL = (
    "https://naturalearth.s3.amazonaws.com/"
    "10m_cultural/ne_10m_admin_0_countries.zip"
)


# --------------------------------------------------
# 2. Validate and load the city information
# --------------------------------------------------

if not INPUT_FILE.exists():
    sys.exit(
        f"ERROR: Input file not found: {INPUT_FILE}\n"
        "Check that this script is saved in the project's src folder "
        "and that data/CityInfo.csv exists."
    )

city_info = pd.read_csv(INPUT_FILE)
required_columns = {"UrbanId", "Longitude", "Latitude", "Area"}
missing_columns = required_columns.difference(city_info.columns)
if missing_columns:
    sys.exit(f"ERROR: CityInfo.csv is missing columns: {sorted(missing_columns)}")

if city_info["UrbanId"].isna().any():
    sys.exit("ERROR: CityInfo.csv contains missing UrbanId values; no files were written.")

if city_info["UrbanId"].duplicated().any():
    duplicate_count = int(city_info["UrbanId"].duplicated().sum())
    sys.exit(
        f"ERROR: CityInfo.csv contains {duplicate_count} duplicate UrbanId values; "
        "no files were written."
    )

city_info["Longitude"] = pd.to_numeric(city_info["Longitude"], errors="coerce")
city_info["Latitude"] = pd.to_numeric(city_info["Latitude"], errors="coerce")
invalid_coordinates = (
    city_info["Longitude"].isna()
    | city_info["Latitude"].isna()
    | ~city_info["Longitude"].between(-180, 180)
    | ~city_info["Latitude"].between(-90, 90)
)
if invalid_coordinates.any():
    bad_count = int(invalid_coordinates.sum())
    sys.exit(
        f"ERROR: {bad_count} row(s) have invalid coordinates; no files were written."
    )

print(f"Loaded city information: {city_info.shape[0]:,} rows")
print("Loading Natural Earth country boundaries...")


# --------------------------------------------------
# 3. Build geographic points and load country boundaries
# --------------------------------------------------

cities = gpd.GeoDataFrame(
    city_info.copy(),
    geometry=gpd.points_from_xy(city_info["Longitude"], city_info["Latitude"]),
    crs="EPSG:4326",
)

try:
    world = gpd.read_file(COUNTRY_BOUNDARIES_URL)
except Exception as exc:
    sys.exit(
        "ERROR: Could not load Natural Earth country boundaries. "
        "Check your internet connection and try again.\n"
        f"Details: {exc}"
    )

if "ADMIN" not in world.columns:
    sys.exit("ERROR: Natural Earth boundary file does not contain the expected 'ADMIN' column.")

world = world[["ADMIN", "geometry"]].copy()


# --------------------------------------------------
# 4. Assign countries only by direct point-in-polygon matching
# --------------------------------------------------

joined = gpd.sjoin(
    cities,
    world,
    how="left",
    predicate="within",
)

# A point should match at most one country for this workflow. Stop rather than
# silently choosing a country if the boundary data creates duplicate UrbanIds.
if joined["UrbanId"].duplicated().any():
    duplicate_count = int(joined["UrbanId"].duplicated().sum())
    sys.exit(
        f"ERROR: Spatial join produced {duplicate_count} duplicate UrbanId rows. "
        "No files were written; inspect boundary overlaps first."
    )

city_mapping = joined[["UrbanId", "Longitude", "Latitude", "Area", "ADMIN"]].copy()
city_mapping = city_mapping.rename(columns={"ADMIN": "Country"})
city_mapping["Country"] = city_mapping["Country"].replace({"Turkey": "Türkiye"})

unmatched = city_mapping[city_mapping["Country"].isna()].copy()


# --------------------------------------------------
# 5. Create the primary China–Türkiye mapping (NO nearest-country fallback)
# --------------------------------------------------

# Important: only direct spatial matches enter this primary research sample.
# Unmatched locations remain unmatched, even if their nearest country is China
# or Türkiye. This keeps the selection rule consistent and avoids silently
# assigning uncertain records to a country.
target_countries = city_mapping[
    city_mapping["Country"].isin(["China", "Türkiye"])
].copy()

if target_countries["UrbanId"].duplicated().any():
    sys.exit("ERROR: Target-country mapping has duplicate UrbanId values; no files were written.")


# --------------------------------------------------
# 6. Create a nearest-country diagnostic report for unmatched points only
# --------------------------------------------------

nearest_country = pd.DataFrame(
    columns=["UrbanId", "Longitude", "Latitude", "Area", "ADMIN", "Distance_KM"]
)

if not unmatched.empty:
    # Use a projected CRS for the spatial distance operation. Distances are
    # diagnostic approximations only; they are not used for country assignment.
    unmatched_points = gpd.GeoDataFrame(
        unmatched[["UrbanId", "Longitude", "Latitude", "Area"]].copy(),
        geometry=gpd.points_from_xy(unmatched["Longitude"], unmatched["Latitude"]),
        crs="EPSG:4326",
    ).to_crs(epsg=6933)
    world_projected = world.to_crs(epsg=6933)

    nearest_join = gpd.sjoin_nearest(
        unmatched_points,
        world_projected[["ADMIN", "geometry"]],
        how="left",
        distance_col="Distance_Meters",
    )

    nearest_country = pd.DataFrame(nearest_join[
        ["UrbanId", "Longitude", "Latitude", "Area", "ADMIN", "Distance_Meters"]
    ]).copy()
    nearest_country["Distance_KM"] = nearest_country["Distance_Meters"] / 1000
    nearest_country = nearest_country.drop(columns=["Distance_Meters"])
    nearest_country = nearest_country.sort_values("Distance_KM", na_position="last")


# --------------------------------------------------
# 7. Final validation before writing output files
# --------------------------------------------------

if len(city_mapping) != len(city_info):
    sys.exit(
        "ERROR: Mapping row count differs from CityInfo.csv. "
        "No files were written."
    )

if city_mapping["UrbanId"].duplicated().any():
    sys.exit("ERROR: Final city mapping has duplicate UrbanId values; no files were written.")

country_counts = target_countries["Country"].value_counts()
china_count = int(country_counts.get("China", 0))
turkiye_count = int(country_counts.get("Türkiye", 0))


# --------------------------------------------------
# 8. Save outputs
# --------------------------------------------------

DATA_DIR.mkdir(parents=True, exist_ok=True)
city_mapping.to_csv(MAPPING_FILE, index=False)
target_countries[
    ["UrbanId", "Longitude", "Latitude", "Area", "Country"]
].to_csv(TARGET_MAPPING_FILE, index=False)
unmatched[["UrbanId", "Longitude", "Latitude", "Area"]].to_csv(
    UNMATCHED_FILE, index=False
)
nearest_country.to_csv(NEAREST_COUNTRY_FILE, index=False)


# --------------------------------------------------
# 9. Print an auditable summary
# --------------------------------------------------

print("\nMapping completed.")
print(f"All-city mapping rows: {len(city_mapping):,}")
print(f"Unmatched city rows: {len(unmatched):,}")
print(f"China rows in primary sample: {china_count:,}")
print(f"Türkiye rows in primary sample: {turkiye_count:,}")
print(f"Total China + Türkiye rows: {len(target_countries):,}")
print("\nFiles saved:")
print(f"- {MAPPING_FILE}")
print(f"- {TARGET_MAPPING_FILE}")
print(f"- {UNMATCHED_FILE}")
print(f"- {NEAREST_COUNTRY_FILE}")
print(
    "\nResearch rule: nearest-country results are diagnostic only and were NOT "
    "used to assign countries in the primary sample."
)
