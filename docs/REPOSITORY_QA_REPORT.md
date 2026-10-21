# Repository Quality-Control Report

## Checks that passed on the files included in this package

- The three active notebooks are valid Jupyter notebook documents. Every non-empty Python code cell parses successfully with Python's AST parser.
- The notebook secret-literal scan found no hard-coded credential assignments in the three active notebooks. The external notebook reads secrets from Colab Secrets.
- Six unit tests passed for country mapping, duplicate-ID rejection, coordinate mismatch rejection, exact source-file naming, and the supplied project data.
- `CityInfo.csv` has 10,196 rows and unique UrbanIds. The canonical mapping has 1,634 rows and unique UrbanIds. All mapping IDs exist in CityInfo, and longitude, latitude, and area match exactly for all mapped IDs.
- The reproducible ID-based merge creates 10,196 output rows; 1,451 rows are labelled China, 183 Türkiye, and 8,562 rows remain without a country assignment. No nearest-country inference is performed.
- The five sample `Mod2_Nig` CSVs each passed the source audit checks for required columns, readable numeric values, and unique UrbanIds. Missing `Intensity_MEA` values are counted, not invented or silently filled.
- A smoke run of the adapted post-run validator completed without crashing and returned `NO-GO` because the fresh output directories intentionally do not yet contain the required research outputs. This is the expected guard state before notebook execution, not a failed research result.

## Checks not yet completed

- The owner reported that an exact filename check in the original local dataset folder returned 80/80 required filenames. The 80-file copy operation has not yet been executed against the owner's Windows computer from this workspace, and the 80 full file contents are not embedded in this GitHub ZIP.
- The full 2001–2020 data pipeline, live AppEEARS/CDS downloads, final transfer experiments, and real-project `GO` validation have not been completed.
- The two distinct groups of uploaded ERA5 NetCDF hashes have no validated provenance sidecars in the provided artefacts. They are not included as active caches; the notebook must validate or re-download them.

## Interpretation

The package is organized and the available code/data checks pass, but the scientific pipeline is **ready for a monitored full run, not yet fully validated**. Do not report final 20-year model results until all source files and generated artifacts pass the in-project validator and flagged discrepancies are reviewed.
