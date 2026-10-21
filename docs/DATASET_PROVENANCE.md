# Dataset Provenance

## Primary SUHII source

- Dataset: Global Urban Heat Island Intensity Dataset, version 3 (Figshare).
- DOI: [10.6084/m9.figshare.24821538](https://doi.org/10.6084/m9.figshare.24821538)
- Main target input files: `Mod2_Nig_YYYY_22.csv`, where `YYYY` runs from 2001 through 2020.
- Required source inventory for the complete notebook pipeline: 80 files — periods 6, 7, 8, and 22 for each year 2001–2020. Period 22 is the primary JJA label; monthly files support diagnostics.
- Required target column: `Intensity_MEA`; units are °C.

The raw source CSV archive is not copied into Git history. It is large and comes from an upstream dataset; the repository contains five clearly labelled sample files. The PowerShell script copies the 80 required files from the owner's existing local folder into the ignored `data/raw/UHII_dataset/` directory.

## City metadata

- `data/reference/CityInfo.csv` is the supplied city metadata table.
- `data/external_features/China_Turkiye_city_mapping.csv` is the canonical country mapping used by the final notebooks.
- `data/processed/CityInfo_with_Country.csv` is regenerated from these inputs using an exact `UrbanId` join. It does not infer country by nearest city.

## External features

The final feature notebook documents its external sources and checks cache provenance:

- Elevation: Open-Meteo Elevation API / Copernicus DEM GLO-90.
- Climate: ERA5-Land via the Copernicus Climate Data Store (CDS).
- Vegetation: NASA MODIS MOD13Q1 NDVI via AppEEARS.

Live requests require user-controlled credentials in Google Colab Secrets. Do not commit NASA or CDS secrets, `.cdsapirc`, raw API responses, NetCDF source downloads, or unverified old caches.

## Limitation

The entire 2001–2020 end-to-end pipeline has not yet been run on the complete local archive in this workspace. Source provenance, hashes, metadata, and validation outputs must pass at run time before results can be reported as final.
