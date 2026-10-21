# Phase 2 Final Package — Local Verification Results

**This is a code verification report, not a claim that the full 2001–2020 research run was completed.** Full archive and live API data downloads were not executed in this workspace.

## Tests executed after final notebook code edits

| Check | Result | Scope and interpretation |
|---|---|---|
| Notebook code syntax | PASS | All non-empty Python code cells in the 3 delivered notebooks parsed with `ast.parse`; outputs are cleared. |
| Obvious hard-coded credential scan | PASS | The corrected notebook sources use Colab Secrets instead of string-literal assignments for NASA/CDS credentials. This does not revoke credentials already exposed in uploaded originals. |
| Core pipeline on supplied source files | PASS, limited scope | Ran the core notebook's relevant pipeline using the supplied 2012 June/July/August/period-22 CSVs and city mapping. This validates the code path for 2012 only. |
| Core target key / city manifest | PASS, 2012 smoke run | Mapping rows: 1,634; quarantined disputed IDs: 13; eligible pool: 1,441 China + 180 Türkiye = 1,621 cities. Final 2012 target: 1,621 rows, unique by `UrbanId-year`, no missing target values. |
| Monthly vs JJA diagnostic | PASS, with issue preserved | 1,631 strict, unambiguous city-year comparisons; MAE ≈ 0.006513 °C; median absolute difference ≈ 0.000973 °C; maximum absolute difference ≈ 1.187423 °C (UrbanId 6256, year 2012). The residual is flagged and has a nonempty protocol disposition; it is not deleted or represented as physically explained. |
| Core model-output loop | PASS, 2012 smoke run | 18 model evaluation rows saved, including `source_mean`, `ridge`, and `rf` in both transfer directions; the run reported zero train/test city overlap. These one-year metrics are not research conclusions. |
| Transfer experiment logic | PASS, synthetic fixture | 90 evaluation rows; 36 paired comparison rows; both transfer directions and all three model types; no test-city overlap; nested few-shot selections verified. Synthetic fixture only. |
| ERA5 provenance helpers | PASS, synthetic NetCDF | Correct matching request fingerprint + SHA sidecar accepted; missing/mismatching provenance or changed file bytes rejected; schema/time/month/units/extent checks tested. The DEM and raw NDVI cache checks also reject an edited file whose hash no longer matches its sidecar. |
| ERA5 precipitation conversion | PASS, synthetic values | `0.0001 m/day × 1000 × 92 days = 9.2 mm` for JJA in the synthetic fixture. Real source data are not used in this unit test. |
| External feature extraction/QC logic | PASS, synthetic coordinates/data | DEM provenance/cache, ERA5 point extraction, temperature conversion, precipitation sum, wind magnitude, NDVI QA bit filtering, duplicate logs, minimum-observation logic, external-panel uniqueness and coverage reports tested. No live downloads were performed. |
| Post-run validator execution | PASS as a guard, expected NO-GO on incomplete fixture | The validator ran without crashing on the limited 2012/synthetic fixture and returned NO-GO because it correctly lacked full 2001–2020 inputs, full external features and all enhanced outputs. A full real run is needed for its actual final status. |

## Exact unresolved boundary

- The available original source CSVs used for the real-data smoke test cover 2012 only. They do not establish that all expected source files for 2001–2020 exist or are valid.
- The NASA AppEEARS and Copernicus CDS tasks were not executed live from this environment. They require user-owned credentials in Google Colab Secrets and network/service access.
- The final 20-year panel, feature coverage and enhanced-model results have not been empirically recreated here. Do not reuse old `task7_transfer_results*` as final results merely because those files exist.
- The high JJA residual for UrbanId 6256 was preserved as the primary precomputed seasonal label by protocol, with explicit uncertainty. The exact physical/source reason for the difference between the seasonal value and the unweighted monthly arithmetic mean remains unproven.

## Outcome

The corrected code has passed the local syntax, real-2012 core-flow, synthetic model-flow, and synthetic external-feature logic checks listed above. The package is ready for a carefully monitored full Colab run. **Phase 2 must not be called fully validated until all 2001–2020 data are generated and `phase2_validate_outputs.py` returns GO on the actual project folder, with warnings and known limitations reviewed.**
