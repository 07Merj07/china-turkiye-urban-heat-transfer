# Current Decision Log — Phase 2 Research Run

## Primary target

- Research scope: transfer of surface urban heat island intensity (SUHII) between China and Türkiye.
- Product: `Mod2` (MOD11A2 clear-sky LST family), nighttime (`Nig`).
- Target column: `Intensity_MEA` (Modified Equal-Area method).
- Period code: `22`, the June–August (JJA) seasonal product.
- Analysis years for this run: 2001–2020.
- The filename must match exactly `Mod2_Nig_YYYY_PERIOD.csv`. `AMod2` and `SMod2` products are not renamed or substituted.

## City cohort

- The supplied mapping has 1,634 unique UrbanIds: 1,451 China and 183 Türkiye before the disputed-ID review.
- The final notebook quarantines 13 disputed IDs, giving an expected eligible cohort of 1,441 China + 180 Türkiye = 1,621 cities, conditional on the reviewed mapping version.
- Unknown country labels and disputed IDs are not assigned by nearest-neighbour guessing.

## Seasonal target checks

- The precomputed period-22 JJA product is the primary target.
- The arithmetic mean of June, July, and August is a diagnostic, not a forced equality condition. A difference does not automatically cause a target row to be deleted.
- Target missing values are not silently imputed during source construction. They must be handled and reported under the notebook's cleaning protocol.

## External predictors

- Elevation, ERA5-Land climate features, and MODIS NDVI are added in the external-feature stage.
- Current external feature tables from older runs are historical artefacts. They are not accepted as verified current cache data unless source metadata and content hashes pass the final notebook's checks.

## Verification status

The final notebook code has passed syntax checks, a limited real-data smoke test on supplied 2012 files, and documented synthetic logic tests. The complete 2001–2020 run has **not** been completed. The project is not ready to report final model performance until all inputs are checked, all three notebooks finish, and `phase2_validate_outputs.py` returns `GO` on the real project folder with warnings reviewed.
