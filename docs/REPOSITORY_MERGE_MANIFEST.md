# Repository Merge Manifest

This is the exact plan used to combine the owner's `urban-heat-transfer` materials with the final audited Phase 2 notebook package. The active GitHub repository is deliberately separated from the historical artefact archive.

## Included in the active repository

| Source item | Destination / treatment | Reason |
|---|---|---|
| Owner's `CityInfo(4).csv` upload | `data/reference/CityInfo.csv` | Standardized name; same supplied 10,196-row table. |
| Owner's `China_Turkiye_city_mapping(1).csv` and final-package mapping version | One canonical `data/external_features/China_Turkiye_city_mapping.csv` | The two tables have identical columns and row values (1,634 rows); duplicate copy is unnecessary. Comparison evidence is in `data/audit_reports/mapping_source_comparison.csv`. |
| Owner's five uploaded exact `Mod2_Nig` samples | `data/sample_uhi/UHII_dataset/` | Useful for smoke checks; explicitly not presented as the full dataset. |
| Owner's prior target-coverage and target-summary CSVs | `data/audit_reports/historical_user_audits/` | Retained with historical labels because they predate the 13-ID quarantine. |
| Owner's small older external missingness reports | `data/audit_reports/historical_external_feature_audits/` | Retained as historical context; not accepted as verified current feature tables. |
| `CityInfo_with_Country.csv` seen in the owner screenshot but not uploaded as a file | Regenerated to `data/processed/CityInfo_with_Country.csv` from the uploaded CityInfo and canonical mapping | One-to-one UrbanId merge; no guessed country assignments. This is a reproducible replacement, not a byte-for-byte copy of the unseen original. |
| Three audited final notebooks from the delivered package | `notebooks/01...`, `02...`, `03...` | Active analysis notebooks. Only project-root/output path setup was adapted to this repository; the scientific model/cleaning logic was retained. |
| Phase 2 post-run validator | `scripts/phase2_validate_outputs.py` | Updated to validate the new `outputs/phase2_outputs/` and `data/external_features/` paths; supports legacy layout too. |
| Source inventory/copy, mapping, and merge check utilities | `scripts/` and `src/urban_heat_transfer/` | Functional GitHub-ready tools with tests. |
| Project protocol and final code/test notes | `docs/` | Preserves the target definition, source review, research protocol, and verification boundary. |

## Preserved outside the GitHub repository

- Large old target validation/exclusion logs and old Phase 2 output CSVs are preserved under `archive/historical_artifacts/` in the all-in-one local bundle. `archive/` is ignored by Git, so those old tables remain available locally but are not added to GitHub or mixed into fresh outputs.
- The 1,037-file / ~1.5 GB source collection is not copied into Git history. The original collection stays on the owner's computer; `scripts/copy_required_uhi_files.ps1` copies only the exact 80 required source files locally.
- `AMod2` samples are not put into the active target path. They are a distinct product family, not a name variant of `Mod2`.
- Old draft notebooks are not placed in the public repository because some earlier originals may contain hard-coded access credentials or outdated paths. The active repository includes only the audited final notebooks. The owner should rotate any credentials that were exposed in old drafts.
- Uploaded ERA5 NetCDF copies are not included as active inputs: six filenames resolve to two distinct content hashes, and no verified provenance sidecar was supplied. The original copies remain in the owner's local folders; new notebook reuse requires provenance verification.

## Reconstructed source utilities — transparency

The screenshots showed `src/country_mapping.py`, `src/merge_test.py`, and two PowerShell audit scripts, but their original source-code bytes were not attached. The versions in this repository are **new, tested replacements** based on the available CSV schemas and the visible purpose of those files. `country_mapping.py` performs an explicit `UrbanId` merge; `merge_test.py` checks invariants; `UHII_Extreme_Values_Check.ps1` flags per-file Tukey outliers for human review only; `UHII_Final_Audit.ps1` runs current data checks. They are not claimed to be byte-for-byte copies of the unseen originals; the original local files are not altered.
