# Enhanced Transfer Decision Log

- Run ID: `20261019_151310`
- Decision: **GO**

- Baseline target rows: 32,420
- Primary common-pool rows: 32,420
- NDVI complete-case rows: 18,237
- Total model evaluations: 1,530
- Paired comparison rows: 612

## Checks

- [x] base_target_unique_city_year
- [x] external_feature_unique_city_year
- [x] joined_rows_match_baseline
- [x] primary_pool_nonempty
- [x] primary_external_columns_present
- [x] model_predictors_exclude_ID_country_target
- [x] all_baseline_models_reported
- [x] no_test_city_overlap
- [x] paired_comparison_created
- [x] external_feature_coverage_report_created
- [x] both_transfer_directions_reported
- [x] primary_pool_has_both_countries
- [x] reported_error_metrics_finite

## Interpretation

- Model results are matched within each pool, transfer direction, model, few-shot ratio, and seed.
- Baseline-versus-extended comparisons are valid only within their named common pool and paired keys.
- NDVI complete-case results represent a smaller, potentially selected sample; they should not be compared directly with primary-pool scores without acknowledging the population change.
- The decision covers only the machine-checkable gates listed here. It is not causal evidence and does not mean raw LST pixels were recomputed.
- NDVI is sampled at city coordinates; it is not a polygon-weighted urban-area mean.
- Keep the external-feature QA report and country coverage tables with these model results.