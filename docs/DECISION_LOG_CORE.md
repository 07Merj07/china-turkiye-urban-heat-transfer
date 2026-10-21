# Phase 2 Core Decision Log

- Run ID: `20261018_002711`
- Decision: **GO**
- Target: `Mod2` / `Nig` / `Intensity_MEA` / period `22`
- Year range: 2001–2020
- Eligible manifest counts: {'China': 1441, 'Türkiye': 180}
- Clean target rows: 32,420
- Clean target unique city-year keys: 32,420

## Checks
- [x] manifest_unique_UrbanId
- [x] country_year_coverage_table_complete
- [x] final_target_rows_reconcile_to_logged_exclusions
- [x] disputed_list_has_13_ids
- [x] all_disputed_ids_quarantined_and_absent_from_final
- [x] all_expected_seasonal_files_present
- [x] all_expected_monthly_files_present
- [x] primary_target_has_only_period_22
- [x] primary_target_has_only_Mod2_Nig
- [x] clean_target_unique_UrbanId_year
- [x] clean_target_complete_labels
- [x] clean_target_years_2001_2020
- [x] feature_matrix_has_no_id_or_country_predictors
- [x] transfer_results_created
- [x] all_baseline_models_reported
- [x] test_city_overlap_zero
- [x] composite_validation_and_high_residual_report_written
- [x] precomputed_jja_target_rule_followed

## Interpretation
- “GO” means the machine-checkable core data gates passed. The period-22 precomputed JJA source remains authoritative; the monthly-mean comparison is diagnostic and flagged residuals remain visible in audit outputs.
- The external feature QA and external-feature transfer experiment are covered by notebooks 02 and 03 and must pass their own gates.
- Do not interpret this log as evidence that remote-source values have already been re-downloaded or that all assumptions have been scientifically reviewed.
