# Phase 2 Final — Change Log and Verification Record

## Included files

- `01_Phase2_Core_Final.ipynb`
- `02_External_Features_Final.ipynb`
- `03_Transfer_Experiments_Final.ipynb`
- `phase2_validate_outputs.py`
- `PHASE2_FINAL_README_TR.md`
- `PHASE2_CHANGELOG_AUDIT.md`
- `PHASE2_LOCAL_TEST_RESULTS.md`

## Main corrections applied

### Core target/cleaning notebook

- Strict filename parsing for `Mod2_Nig_YYYY_PERIOD.csv`, constrained to periods 6/7/8/22 and years 2001–2020.
- Explicit manifest matching, quarantining of the 13 known disputed IDs, separate unknown-country handling, and one target row per `UrbanId-year` policy.
- Ambiguous duplicate city-year groups are not resolved by taking the first source row; exclusions are logged.
- Added key-set reconciliation between nonmissing primary-target keys, explicit quarantine/exclusion actions, and final cleaned target.
- Outlier screening is a review flag, not automatic removal.
- Monthly-vs-precomputed-JJA checks use only unambiguous keys and write a separate high-residual table.
- Fixed a malformed quote in country normalization discovered by AST checks.
- Added a nonempty default disposition to each high JJA residual. This retains the precomputed JJA target while explicitly saying the residual's exact source/physical cause is not proven; it does not silently exclude the row.
- Confirmed all three baseline models' scores are captured inside the loop, not just the last model.
- Baseline model inputs do not include ID, country label or monthly target-derived values; preprocessing is inside sklearn pipelines.

### External feature notebook

- Removed hard-coded API credentials; all secrets are read from Colab Secrets.
- ERA5 file reuse requires matching request fingerprint, file SHA-256, schema, years/months, coordinates, plausible variable units and geographical coverage.
- Existing unverified source files are backed up and not silently treated as current data.
- Temporary `.cdsapirc` is removed after the CDS client reads it.
- NetCDF extraction uses a unique temporary filename to avoid a source/destination collision.
- ERA5 precipitation conversion explicitly depends on source request and metadata: the monthly mean daily accumulation is converted to a JJA accumulation in mm by multiplying `m/day × 1000 × days_in_month` and summing the three months.
- DEM provenance is labeled Open-Meteo Elevation API / Copernicus DEM GLO-90; stale cache reuse is guarded by source, coordinate signature and SHA-256 of the exact canonical CSV bytes. Metadata is refreshed after the final canonical write.
- MOD13Q1 V6.1 QA bit positions, NDVI range, scale factor and minimum valid-observation rule are specified in the notebook; raw NDVI is reusable only with a matching request fingerprint and SHA-256 of the exact CSV bytes. The ERA5 CDS client config is removed after client initialization.
- External feature panel checks one row per included city-year and emits country-specific missingness reports.

### Transfer notebook

- Uses a common comparison pool for fair baseline-vs-extended comparison and a separately reported NDVI complete-case sensitivity pool.
- Fixed test cities per pool/transfer direction, independent of few-shot ratio.
- Few-shot cities are sampled only from the non-test adaptation pool; samples are nested across ratios and repeated by seeds.
- Checks for duplicate `UrbanId-year` rows, forbidden predictors, test-city overlap, non-finite metrics, required transfer directions and paired comparison outputs.
- Enhanced outputs are separately named and old outputs are backed up rather than overwritten without preservation.

### Post-run validator

- Added `phase2_validate_outputs.py`, which compares files, key uniqueness, country/year scope, row reconciliations, JJA summary-vs-detail metrics, documented high-residual dispositions, source inventory status, ERA5 source/hash sidecar, feature leakage, common-panel shape, split isolation, nested few-shot sets and paired comparison completeness.
- The validator's GO is machine-checkable only, not an independent confirmation of source-science truth.

## Known scientific/design limitations retained deliberately

- The ready precomputed period-22 JJA product remains the primary target. Monthly arithmetic averaging is a diagnostic, not a mandatory equality rule. Large differences stay visible and must be disclosed; they are not automatically discarded.
- External ERA5 and NDVI predictors are sampled at points/nearest grid cells using coordinates, not polygon-weighted urban-area means. Polygon files were not provided in the inputs reviewed here.
- A full 2001–2020 end-to-end download was not executed in this workspace because the complete target archive and authorized live API access were not available. The new notebooks will stop/fail QA rather than silently treating stale or unproven files as current.
- API credentials embedded in source originals were removed from the final copies, but those exposed credentials should be rotated/revoked at their service providers.

## Verification status

All non-empty Python code cells in the three delivered notebooks were parsed with Python `ast.parse`, notebook outputs were cleared, and the test runs documented in `PHASE2_LOCAL_TEST_RESULTS.md` were executed after the final logic changes where indicated. Synthetic tests prove the tested logic paths only; they are not presented as the actual 20-year transfer research results.
