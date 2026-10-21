# Can Urban Heat Models Cross Borders?
## Master Research Protocol: China–Türkiye Urban Heat Island Transferability Study

**Document type:** Integrated master research plan, data-audit record, and pre-modelling protocol  
**Version:** 1.0 — consolidated 11 October 2026  
**Status:** Pre-modelling; existing dataset audits are complete, but the final target, geometry strategy, feature coverage and split manifests must pass the gates in this document before full model training.  
**Project collaborators:** Mert and Tao  
**Primary research direction:** Transferability of urban heat island intensity (UHII) prediction between China and Türkiye  
**Working title:** *Can Urban Heat Models Cross Borders? Quantifying the Transferability of Urban Heat Models Between China and Türkiye*

---

## How to use this document

This document consolidates (1) the work already completed by the project team, (2) Tao's revised research plan and experimental checklist, and (3) corrections needed to make the combined plan internally consistent and reproducible. It replaces the overlapping draft sections and repeated decision tables in the earlier plan. It does **not** claim that proposed analyses have already been run.

### Status labels

- **COMPLETED — EVIDENCED:** A result is supported by an existing audit, file, or recorded terminal output.
- **DOCUMENTED — NOT INDEPENDENTLY VERIFIED:** A source or decision has been recorded, but an independent check is not possible from the files currently available.
- **PROPOSED — DEFAULT RECOMMENDATION:** A recommended method that still needs team approval and/or evidence.
- **OPEN BLOCKER:** Must be resolved before the affected modelling experiment can start.
- **LATER / OPTIONAL:** Useful only after the primary evaluation is valid, or appropriate as a sensitivity analysis.

A decision written in this document is not automatically an empirical result. The project must keep those two things separate in code, audit reports and the final paper.

## Executive summary

The team has already completed substantial data-inventory and technical-quality work. The current local UHII archive contains 5,372 CSV files. The full audit reported no structural, required-column, ID, filename/combination, configured-coverage, or unexpected non-`NA` numeric-format anomalies under the rules implemented. `CityInfo.csv` and `CityInfo_with_Country.csv` each contain 10,196 unique `UrbanId` values with matching ID sets; the audited coordinates and area values also match between the files. The primary China–Türkiye sample is currently 1,441 Chinese and 180 Turkish urban units (1,621 total). Eighty-three urban units have blank country labels and remain excluded from the primary sample; 13 nearest-country candidate labels are part of those same 83 records, not additional records.

These are meaningful completed checks. They mean the team should **reuse the existing audit evidence rather than rerun every broad structural check from scratch**. They do not, however, establish that the local files are an exact bit-for-bit copy of a particular Figshare archive version, that every measurement is scientifically correct, that the proposed target has been validated, or that the extra predictor datasets have been downloaded and spatially aligned.

Tao's proposed core experiment is a cross-country regression task: train on urban units in one country and test on unseen urban units in the other, in both directions. A proposed main target is nighttime surface UHII using `Intensity_MEA` for June–August (JJA), in °C, with possible target-country adaptation by retraining on source data plus small samples of labelled target-country urban units. Proposed models are Linear Regression, Random Forest and XGBoost. Evaluation includes R², MAE and RMSE; target-country test labels must remain untouched throughout feature selection, tuning, and adaptation.

### Current decision

**Accept Tao's study design as a strong working framework, but do not yet mark the study as ready for full model training.** The four highest-priority unresolved items are:

1. **Exact target identity:** the UHII `Indicator` prefix / temperature product, diurnal period, `Intensity_MEA` method, seasonal convention, units and source definition must be frozen. The current dataset has multiple temperature sources and multiple temporal summaries; `Intensity_MEA` alone does not define one unique target.
2. **Spatial geometry:** the currently audited `CityInfo.csv` is a point/attribute table (`UrbanId`, longitude, latitude and area), not a polygon file. Polygon-based zonal means cannot be claimed unless compatible urban geometries or masks are actually located and validated. The newer, separate UHII dataset record advertises urban and rural spatial extents, but it must not be silently mixed with the existing target archive.
3. **Target-year and predictor coverage:** 2005, 2010 and 2015 are Tao's proposed candidate years, not yet demonstrated to be the only or best usable years. A target-specific and feature-specific coverage report must decide whether to use all overlapping eligible years or a justified fixed subset.
4. **Geospatial calculation and model protocol:** do not use EPSG:3857 for authoritative area measurements; resolve the conflicting split, missing-value, baseline and feature-selection rules before freezing the experiment configuration.

The current research priority is **target and feature auditing, not model tuning**. Full modelling starts only after the decision gates and manifests below are completed.

---

# 1. Research question, scope and hypotheses

## 1.1 Primary research question

Can a regression model trained on urban units in one country predict warm-season surface urban heat island intensity (SUHII) for previously unseen urban units in the other country, using a harmonised set of surface, climatic and topographic predictors?

## 1.2 Secondary research question

Does adding a limited number of labelled target-country urban units to the source-country training data improve prediction on an untouched target-country test set, and how does performance change as the target-country labelled sample grows?

## 1.3 Scope

**In scope:**

- China → Türkiye and Türkiye → China cross-country prediction.
- One explicitly defined, consistently measured SUHII target for the primary experiment.
- Common predictor data with documented definitions, versions, units, spatial supports and time alignment.
- Regression models for tabular data.
- A fixed target-country test set and leakage-safe model selection.
- Optional supervised adaptation using whole target-country `UrbanId` groups.
- Carefully qualified model interpretation using SHAP after the primary evaluation is frozen.

**Out of scope for the primary study:**

- Causal claims that a predictor physically causes UHII.
- Near-surface air-temperature UHI unless a separate target is explicitly designed.
- Future climate projections.
- Fine-scale within-city temperature mapping.
- Deep learning unless a later, evidence-based change in scope is approved.

## 1.4 Hypotheses translated into measurable tests

The original wording about whether “statistical relationships” transfer is broad. The primary experiments are predictive, so the confirmatory hypotheses should be stated in terms of held-out predictive performance.

- **H1 — Direct transfer:** In each transfer direction, the source-trained model achieves better prediction on the untouched target-country test set than a simple source-training-mean predictor, evaluated on exactly the same test observations.
- **H2 — Target-labelled adaptation:** Retraining on source-country training data plus a small, disjoint sample of labelled target-country `UrbanId` groups improves performance relative to direct transfer, across the tested adaptation sample sizes.
- **H3 — Adaptation curve:** Target-country test performance tends to improve as the amount of labelled target-country data increases. A claim of saturation is made only if the tested sample-size range contains evidence of a plateau; improvement from 1% through 50% alone does not prove that performance has saturated at larger sample sizes.

H1 and H2 are not assumed to be true. A model can transfer poorly, adaptation can fail for small samples, and the two transfer directions can produce different results. Both directions should be reported separately.

### Operational definition of useful transfer

For each direction, compare every model with the source-mean baseline on the same target-test rows. Report R², MAE and RMSE. A conservative primary interpretation rule is that transfer is useful only when the model improves absolute error relative to the source-mean baseline and the result is not explained by leakage or an invalid test design. R² is reported directly, including negative values; it must not be clipped to zero. The exact formal success rule and which metric is primary must be recorded before target-test results are inspected.

---

# 2. Confirmed project work: existing audit evidence

This section records completed work so the team does not repeat it unnecessarily. Source records are the project progress log, `UHII_Final_Audit_Summary.txt`, `DATA_QUALITY_AUDIT_NOTES.md`, `DATASET_PROVENANCE.md`, and the row-level 13-record mapping comparison.

## 2.1 Local folder and UHII file inventory — COMPLETED

**Known local project root:** `C:\Users\Mertc\OneDrive\Masaüstü\urban-heat-transfer`  
**UHII CSV directory:** `data\UHII_dataset\`

The current inventory records:

- 5,372 UHII CSV files.
- File naming pattern: `Indicator_Diurnal_Year_Period.csv`.
- `Day` means daytime and `Nig` means nighttime.
- Period codes `1`–`12` represent months January–December.
- `21` = March–May; `22` = June–August; `23` = September–November; `24` = December–February.
- `30` = annual average.
- The intensity columns are `Intensity_EA`, `Intensity_IEA`, `Intensity_MEA` and `Intensity_DEA`. These are four methods, not four countries or independent datasets.

### Indicator-prefix notes captured in the existing project log

The prior project notes record the following preliminary meanings. They must be cross-checked against the source README / paper before the final target is frozen:

| Prefix | Preliminary meaning in project notes | Modelling implication |
|---|---|---|
| `Mod1` | UHII based on MOD11A1 | Confirm product cadence, surface category, QA and coverage. |
| `Mod2` | UHII based on MOD11A2 | Confirm product cadence, surface category, QA and coverage. |
| `Myd1` | UHII based on MYD11A1 | Confirm product cadence, surface category, QA and coverage. |
| `Myd2` | UHII based on MYD11A2 | Confirm product cadence, surface category, QA and coverage. |
| `AMod2` | All-sky MOD11A2-related product in the project notes | Verify exact meaning and how it differs from `Mod2`. |
| `SMod2` | Seamless MOD11A2-related product in the project notes | Verify the gap-filling / seamless processing and its comparability. |
| `SMyd1` | Seamless MYD11A1-related product in the project notes | Verify the gap-filling / seamless processing and its comparability. |
| `SAT` | Recorded in prior notes as “surface air temperature” | **Do not assume it is surface LST SUHII.** Read source documentation; it may represent a different target construct and should not be mixed with surface-temperature products. |

The dataset paper describes multiple temperature data sources and includes clear-sky surface, all-sky surface and canopy-related UHII products. Therefore, the final target must identify the exact prefix and construct, not merely choose `Intensity_MEA`. The meanings above are provisional notes, not a substitute for the primary source documentation.
- Indicator prefixes in the audited directory: `AMod2`, `Mod1`, `Mod2`, `Myd1`, `Myd2`, `SAT`, `SMod2` and `SMyd1`.
- The inventory includes 316 annual (`_30.csv`) files.

The recorded filename ranges vary by indicator. The audit configuration used the following ranges:

| Indicator prefix | Configured years in the file inventory | Notes |
|---|---:|---|
| `Mod1` | 2001–2021 | Confirm exact product definition from official data documentation. |
| `Mod2` | 2001–2021 | Confirm exact product definition from official data documentation. |
| `AMod2` | 2001–2020 | Confirm exact product definition from official data documentation. |
| `SAT` | 2001–2020 | Confirm exact product definition and interpretation of SAT. |
| `SMod2` | 2001–2020 | Confirm exact product definition from official data documentation. |
| `Myd1` | 2003–2021 | Confirm exact product definition from official data documentation. |
| `Myd2` | 2003–2021 | Confirm exact product definition from official data documentation. |
| `SMyd1` | 2003–2020 | Confirm exact product definition from official data documentation. |

These are ranges from the project's configured inventory and must be cited to the source documentation before publication. A complete filename pattern does not, by itself, prove that each individual measurement is valid.

## 2.2 Full technical audit of the 5,372 CSV files — COMPLETED

The existing full audit reported:

| Check | Audited result |
|---|---|
| CSV files found / expected | 5,372 / 5,372 |
| Files with unexpected row count | 0 |
| Missing required columns | 0 files |
| Empty/malformed files or malformed rows | 0 reported |
| CSV read errors | 0 |
| Blank `UrbanId` values | 0 reported |
| Duplicate `UrbanId` rows within a file | 0 reported |
| Unknown/missing IDs relative to the expected city list | 0 reported under the audit rules |
| Country-count mismatch issue records | 0 reported under the audit rules |
| Incomplete indicator-year-period groups | 0 under the configured expected-coverage rules |
| Blank, unexpected text or non-finite numeric cells outside explicit `NA` values | 0 reported |

**Interpretation:** this is a successful technical audit of the implemented checks. It does **not** establish that each temperature retrieval is scientifically correct, that every `NA` has a known cause, that the exact archive version is independently verified, or that the proposed predictor layers are ready.

## 2.3 Numeric `NA` values — COMPLETED

The audit reported these counts across the overlapping files and indicators:

| Intensity field | Valid numeric cells | `NA` cells |
|---|---:|---:|
| `Intensity_EA` | 54,563,834 | 209,078 |
| `Intensity_IEA` | 54,560,493 | 212,419 |
| `Intensity_MEA` | 54,560,204 | 212,708 |
| `Intensity_DEA` | 54,557,592 | 215,320 |

Country-specific aggregate missingness recorded by the audit:

| Country | `NA` cells / checked cells | Rate | Files with at least one `NA` |
|---|---:|---:|---:|
| China | 38,650 / 30,964,208 | 0.124822% | 875 |
| Türkiye | 1,515 / 3,867,840 | 0.039169% | 12 |

Two files were specifically noted to contain `NA` for all 180 Turkish records across all four intensity methods:

- `Myd1_Nig_2018_5.csv`
- `Myd2_Day_2013_6.csv`

The audit did not establish the cause of those missing values. They must not be attributed to cloud contamination or another specific cause without evidence from the data producer. The existing audit found no Turkish `NA` values in the annual files, but the target-specific report must be rerun for the chosen indicator, period and years.

**Established rule:** never replace missing UHII target values with zero. A record with a missing selected target cannot be used as a labelled training or evaluation example. Predictor missingness is handled under the single, consistent protocol in Section 8.

## 2.4 City information and country mapping — COMPLETED

Both `CityInfo.csv` and `CityInfo_with_Country.csv` were audited as 10,196-row, 10,196-unique-ID tables. The ID sets matched. The audit compared 30,588 coordinate/area cells between the two files and reported no mismatch in those compared values.

The present primary map contains:

| Group | Count | Primary-analysis rule |
|---|---:|---|
| China | 1,441 | Include, subject to target/feature eligibility. |
| Türkiye | 180 | Include, subject to target/feature eligibility. |
| Blank/unknown country | 83 | Keep outside the primary comparison unless a documented geographic rule resolves them. |
| Other countries | 8,492 | Outside the China–Türkiye comparison. |
| Total city metadata rows | 10,196 | Source city-reference table. |

A separate `China_Turkiye_city_mapping.csv` assigns labels to 13 of the 83 blank-labelled records using a nearest-country procedure. The row-level difference was audited:

- China-labelled candidates: `UrbanId` 3, 62, 617, 2133, 4785, 5253, 7288, 8344, 8486 and 9175.
- Türkiye-labelled candidates: `UrbanId` 64, 601 and 4586.

These 13 records are part of the 83 blank-labelled records; they are not 13 additional urban units. Their coordinates and area values match the primary table, but the available records do not establish that the nearest-country assignment is valid for the primary definition. Keep them out of the primary sample unless manual geographic checking establishes a defensible rule. They can be listed in a separate review manifest; do not use a 5 km fallback just to increase the sample size.

**Primary mapping rule:** use the direct country-label/spatial-join table as the primary mapping, with 1,441 China and 180 Türkiye units before target/feature filtering.

## 2.5 Unusual UHII values — COMPLETED FIRST-PASS REVIEW

The prior audit checked values below −40 or above +40 in 2,006 monthly files for `Mod1`, `Myd1` and `Myd2`. It flagged 16 values. One flagged observation is within the current China–Türkiye sample:

- China `UrbanId` 5560, `Mod1_Day_2017_10.csv`, `Intensity_DEA` = 41.82.

Nearby months and seasonal/annual records were much lower. This is a suspicious observation, but the evidence does not prove it is wrong. Do not delete or overwrite it based solely on extremeness. It belongs to daytime, October and DEA, so it is not part of the currently proposed nighttime MEA JJA primary target. Revisit only if the final target or sensitivity analysis includes that observation; otherwise record it as an existing audit finding, not as a blocker to the primary target.

Negative UHII values are physically possible because UHII is a temperature difference. They must not be automatically treated as errors.

## 2.6 What is **not** completed by the existing audit

The current audit does not yet prove:

- the precise indicator prefix / temperature product to use for the primary target;
- the final JJA aggregation method and the exact target values per `UrbanId × year`;
- that 2005, 2010 and 2015 are the only or best years with complete predictor coverage;
- that external feature datasets (NDVI, ERA5-Land, DEM, etc.) have been downloaded, validated and extracted for these urban units;
- that urban polygon geometries/masks are available in the current local project folder;
- that urban area and centroid metadata semantics/units are documented well enough for modelling;
- a finalized feature matrix, target coverage report, leakage-safe split manifests or any model-performance results.

---

# 3. Data provenance, archive version and source strategy

## 3.1 Original UHII source — DOCUMENTED, LOCAL SNAPSHOT NOT INDEPENDENTLY VERIFIED

The project records the original Figshare dataset record:

- **Dataset:** *Global Urban Heat Island Intensity Dataset*.
- **Record:** <https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset/24821538>
- **DOI:** <https://doi.org/10.6084/m9.figshare.24821538>
- **Related paper:** Yang, Q., Xu, Y., Chakraborty, T. C., et al. (2024), “A global urban heat island intensity dataset: Generation, comparison, and analysis,” *Remote Sensing of Environment*, 312, 114343. <https://doi.org/10.1016/j.rse.2024.114343>
- **Licence displayed on original record:** CC BY 4.0.

The original record currently displays **Version 3 dated 5 January 2024**. Project notes record that the local files were downloaded using “Download all” from the original record. However, the original downloaded ZIP/archive and a checksum are not currently stored in the project directory. Therefore, the exact local archive snapshot cannot be independently confirmed as Version 3. This is a traceability limitation, not evidence that the files are wrong.

**Approved source wording:** “We use the Global Urban Heat Island Intensity Dataset associated with the original Figshare record (DOI: 10.6084/m9.figshare.24821538). The record currently displays Version 3; the exact version of the local extracted files could not be independently verified from an original archive or checksum.”

Do not spend time redownloading the 1.34 GB original archive solely to change this wording unless the team decides that byte-level provenance is essential to the final deliverable. Retain the existing technical audit and record this limitation honestly.

## 3.2 Separate updated dataset record — DO NOT CONFUSE WITH ORIGINAL RECORD VERSION 2

A separate updated record is linked from the original Figshare page:

- <https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset_Version2_/30102847>

The dataset authors' update announcement states that this separate record:

1. changes the base map for urban-area delineation from MODIS land cover to ESA CCI land cover;
2. provides spatial extents for urban and rural/background-reference areas; and
3. adds average urban temperature in addition to UHII.

This is a **separate updated dataset record**, not merely “Version 2” in the version history of the original `24821538` record. Keep these two versioning contexts separate.

### Why this matters to this project

The additional spatial extents in the updated record may be useful for extracting predictors over urban polygons. However, the team has so far audited the original local CSV archive. It has not yet established that the updated record has the same `UrbanId` mapping, target fields, target definitions, indicator names, time coverage or missing-value behaviour as the currently audited files.

**Do not combine updated-record geometries with the original UHII target values without a documented equivalence check.** That could mean the target and the predictor geometry describe different urban delineations.

### Source decision gate — OPEN BLOCKER

The team must make one explicit choice:

- **Path A — Retain the already audited original archive.** Continue using its target values and mapping. Find and validate a compatible geometry source if polygon zonal statistics are required. If compatible polygons cannot be obtained, change the feature extraction plan honestly (for example, a pre-defined point/buffer strategy) rather than describing it as polygon zonal averaging.
- **Path B — Adopt the separately updated record.** First compare record contents and IDs, then rerun the relevant structural, numeric, country-mapping, target-coverage and missingness audits on the chosen updated archive. Document how the update changes target/geometry compatibility. Do not merge old and new target data in the same primary sample unless equivalence is demonstrated and a combined protocol is justified.

**Default recommendation:** keep the current, audited original archive as the working target source while performing a short geometry-feasibility check on both records. Decide explicitly whether the research needs a boundary-based feature design; do not switch the target archive merely because the updated record exists. If the proposed polygon-mean feature extraction cannot be carried out with the current record, Path B should be evaluated seriously before model development.

## 3.3 Data and code storage

- Do not commit the full UHII archive / all 5,372 source CSV files to a normal Git repository.
- Keep source data outside Git; commit scripts, lightweight processed tables, manifests, audit summaries and versioned documentation.
- Record the source link, DOI, retrieved date, record/version wording, file inventory and any checksums that are available.
- Keep raw source files immutable. Derive modelling data into separate files and make every filtering/transformation reproducible.

---

# 4. Target definition and observational unit

## 4.1 Candidate target recommended by Tao

Tao proposes a **nighttime surface urban heat island intensity (SUHII)** target using `Intensity_MEA`, in °C, with positive values indicating that urban land surface temperature is higher than the rural reference. The proposed seasonal window is June–August (JJA), with one row per `UrbanId × year`.

One additional source-definition conflict must be checked: the earlier project notes record MEA as a method that uses information about the urban area's surrounding reference region and excludes certain areas based on nighttime-light intensity (NLI), with the buffer/eligible area defined by the source's detailed rules. Tao's draft paraphrases MEA more generally as a rural buffer around the urban extent. These descriptions must not be assumed equivalent. Use the dataset README and scientific paper as the authority, record the source's exact MEA definition, and correct either draft wording if needed. Do not invent a method definition from the acronym alone.

This is a good candidate, but `Intensity_MEA` alone is not enough to uniquely identify the target. The local archive also contains multiple `Indicator` prefixes (e.g., `Mod1`, `Mod2`, `AMod2`, `Myd1`, `Myd2`, `SAT`, `SMod2`, `SMyd1`), both `Day` and `Nig`, and monthly/seasonal/annual files. Different prefixes may represent different temperature sources or processing choices. The primary target must freeze **all** of the following:

1. data archive record and snapshot wording;
2. `Indicator` prefix / temperature product;
3. `Diurnal` value (`Nig` for the proposed night target);
4. target field (`Intensity_MEA` for the proposed primary method);
5. period definition (monthly values aggregated to JJA, or the archive's native JJA period `22`);
6. units and sign convention;
7. eligible years and valid-record rules.

## 4.2 Target formula and interpretation

Conceptually, surface UHII is the difference between mean urban land surface temperature and the corresponding rural/background reference temperature:

\[
SUHII_{i,y} = \overline{LST}_{urban,i,y} - \overline{LST}_{rural,i,y}
\]

where `i` denotes the urban unit and `y` denotes a year or explicitly defined period. For this project, the team intends to use an archive-provided `Intensity_MEA` field rather than recalculate the urban-minus-rural difference for every observation, unless the necessary raw temperatures and exact masks are available and the team explicitly adopts an independent recalculation procedure.

**Do not describe the selected target as near-surface air-temperature UHI unless the selected archive field actually represents that quantity.** The main study is intended to concern surface UHII. The `SAT` prefix must be checked against the original data documentation rather than inferred from its letters alone.

## 4.3 JJA aggregation: reconcile Tao's plan with the existing archive

The audited archive uses period code `22` for June–August (JJA) quarterly averages. Tao's revised plan instead proposes averaging monthly nighttime `Intensity_MEA` values for June, July and August and retaining an `UrbanId × year` if at least two months are valid.

These definitions must not be silently treated as identical. A native seasonal product may use a different aggregation process from the arithmetic mean of three monthly UHII values. The existing audit establishes that period code `22` exists in the naming system; it does not independently validate exactly how the selected indicator's JJA value was calculated.

### Required decision process

1. Read and cite the original data README / methods for the selected indicator prefix and confirm the meaning of period `22`.
2. Inspect the selected `*_Nig_<year>_22.csv` files and the monthly June, July and August files for a sample of UrbanIds and years.
3. Quantify differences between the native period-22 value and the arithmetic mean of the available monthly `Intensity_MEA` values. The two methods do **not** have to match exactly if the source's aggregation methods differ; discrepancies must be understood and recorded.
4. Choose **one primary rule** before training:
   - **Preferred archive-native option:** use period `22` if the source documentation confirms that it is the appropriate JJA summary for the selected product and it fits the research definition; or
   - **Custom monthly-derived option:** compute the arithmetic mean from June, July and August monthly values and document the minimum-month rule. Tao proposes retaining a year when at least two of three monthly target values are valid. This is a custom study target and should be labelled accordingly.
5. Treat the alternative calculation as a sensitivity analysis only if the data supports it and time permits.

**Do not average different indicator prefixes together.** The same prefix, diurnal period, UHII method, seasonal definition and measurement convention must be used in China and Türkiye.

## 4.4 Target-year selection — OPEN BLOCKER

Tao currently proposes 2005, 2010 and 2015 as joint usable years. These are **candidate years**, not yet proven to be the only eligible years. The current file audit shows broad archive coverage across many years; its configured coverage checks do not establish predictor coverage for these three years or justify excluding all other common years.

### Recommended decision rule

- First produce target-specific valid-count tables for every candidate year available for the selected indicator, day/night value and JJA definition.
- Produce feature-specific coverage tables for the same years.
- Prefer **all common eligible years** if the target and predictors are valid and time-aligned, because this retains more observations and temporal variation.
- Use only 2005, 2010 and 2015 if the team predefines a defensible reason (such as deliberate five-year snapshots, an external data limitation or manageable project scope), documents why these three years were selected, and acknowledges the lost temporal information.
- Do not state that those years have “complete predictor coverage” until the actual feature files have been checked and the coverage report has been produced.

For any selected year, the observation is one `UrbanId × year`. A city can contribute one, two or three valid years under the current three-year proposal; if more years are used, it can contribute more. All observations for one `UrbanId` must remain in the same train/validation/test partition.

## 4.5 Valid target and target aggregation rules

- A missing target is never imputed.
- Under the custom monthly-derived JJA rule, retain a city-year only when at least two of June/July/August have valid target values, as proposed by Tao. Report which month(s) were missing and the number of months used for each retained annual warm-season value.
- Under the archive-native period-22 rule, use the period-22 value only if it is valid and passes the documented product quality criteria; do not also require two monthly records unless that requirement is part of the source or the chosen sensitivity analysis.
- Preserve negative SUHII values when scientifically valid.
- Save the selected target formula, file-prefix rule, period rule, units, source citation and exclusions in `docs/TARGET_DEFINITION.md`.

---

# 5. Geospatial geometry, boundaries and CRS

## 5.1 Current geometry status — OPEN BLOCKER FOR POLYGON MEANS

The previously inventoried `CityInfo.csv` has fields `UrbanId`, `Longitude`, `Latitude` and `Area`. The available audit files document those attributes and their consistency, but do not establish that a compatible urban polygon geometry or pixel mask has been located in the current project folder.

Tao's feature plan requires zonal means/percentages over urban polygons for NDVI, elevation and possibly land-cover/albedo features. That operation requires actual polygon geometries or a compatible raster mask. **A centroid and an area number are not sufficient to calculate a polygon zonal mean.** The team must locate and validate geometries before claiming polygon-based feature extraction.

### Geometry feasibility checklist

- [ ] Inventory all local files for polygon/raster masks, not just CSVs; record exact file paths and formats.
- [ ] Determine whether the original UHII source provides the urban and rural masks/areas used to calculate the selected target.
- [ ] If evaluating the separate updated record for geometry, compare its IDs, boundaries and target definitions with the already audited original archive before adoption.
- [ ] Validate geometry count, unique ID relationship, geometry validity, coordinate reference system (CRS), area and boundary overlap.
- [ ] Confirm whether `CityInfo.Area` is an authoritative supplied attribute, its units and how it was computed; do not assume the units.
- [ ] If matching external city boundaries are used, document source, version, date and harmonisation method; do not mix urban definitions without a sensitivity analysis.

If no suitable geometry source is available, choose a different feature extraction method and explicitly rename the measurements. For example, a value sampled at the point coordinates is a **centroid/pixel sample**, not an urban-polygon mean. A fixed-radius buffer is also a different support from the original urban polygon and must be specified before use. Do not describe one as the other.

## 5.2 Coordinate reference system and area calculations

Tao's draft suggests EPSG:4326 for storage and EPSG:3857 for area/buffer calculations. Keep EPSG:4326 as a possible storage CRS for longitude/latitude geometry, but **do not use EPSG:3857 as the authoritative area-measurement CRS**. Web Mercator is intended primarily for display and can distort distances/areas, with distortion varying by latitude. This is a concern when comparing urban areas across China and Türkiye.

Recommended rule:

- Calculate area using an appropriate equal-area projection for each region or a consistent geodesic-area method on the appropriate ellipsoid.
- Calculate distances/buffers in a suitable projected CRS or use a documented geodesic method. Do not assume EPSG:3857 metres are accurate for the study's spatial calculations.
- Record the CRS, transformation, area units and calculation method in the data dictionary.
- Validate a sample of area calculations against known geometry values or an independent GIS measurement.

The team must choose one reproducible geospatial rule and use it consistently for both countries. Where different regional projected CRSs are used, the calculation method and resulting unit (e.g., m² or km²) must still be consistent and comparable.

## 5.3 Spatial aggregation details

If polygons/masks are available, document for every raster feature:

- raster product and version;
- native spatial resolution and CRS;
- time range and temporal compositing;
- QA filters and scaling factors;
- pixel inclusion rule at polygon edges;
- statistic used (mean, median, percent cover, etc.);
- valid-pixel threshold and no-data handling;
- how the extraction is linked to `UrbanId`;
- resulting rows/pixels available per country and year.

ERA5-Land has approximately 9 km grid spacing. A city polygon may overlap only a small number of its grid cells; nearby or small urban units may consequently receive very similar climate values. Report this limitation and consider point/cell extraction or a different aggregation rule only as a documented sensitivity analysis, not an ad hoc change.

---

# 6. Candidate predictor data dictionary

The following is the initial common-feature proposal. A feature is not “available” simply because a global product exists; project coverage, the actual acquisition/version, quality-filtered valid pixels, temporal matching and spatial extraction must be demonstrated.

## 6.1 Core candidate features

| Feature | Initial source / definition | Temporal treatment | Spatial treatment | Status / conditions |
|---|---|---|---|---|
| NDVI | MODIS/Terra MOD13Q1 vegetation index; proposed 250 m, 16-day product | JJA composite matching each target year, using quality flags | Urban-polygon zonal statistic if compatible polygons exist; otherwise declare the alternative support clearly | **Proposed.** Use a documented current collection such as Version 6.1 if it is the product adopted; archive exact version and QA rules. Do not say it is already downloaded/extracted. |
| Mean 2 m air temperature | ERA5-Land | JJA mean for the same year as the target | Polygon zonal mean only if geometry is available; otherwise pre-defined grid/point method | **Proposed.** Approximately 9 km grid; document units, conversion and extraction. |
| Precipitation | ERA5-Land total precipitation | JJA accumulation/total for the same year, with correct accumulation convention and units | Same spatial rule as temperature | **Proposed.** Do not average accumulated precipitation as if it were a temperature; follow the product's accumulation semantics. |
| Elevation | One documented global DEM; SRTM 30 m is Tao's candidate | Static | Mean elevation over compatible urban polygons, if available | **Proposed.** Verify product/version, no-data pixels and area support. |
| Urban area | Source `Area` attribute or recomputed from valid polygon geometry | Static or boundary-year-specific if the boundary changes | Use a documented and validated area definition | **Proposed.** Confirm units and meaning of the source `Area`; do not blindly recompute with EPSG:3857. |
| Latitude / longitude | `CityInfo.csv` coordinates, subject to source metadata | Static | Use supplied coordinate attributes unless evidence supports re-computing a centroid | **Available in metadata, semantics still to confirm.** Do not calculate a new centroid from a nonexistent polygon. |

## 6.2 Optional features — not part of the initial core model

| Optional feature | Potential source | Why optional | Rule for inclusion |
|---|---|---|---|
| NDBI | Global Landsat-derived product or another documented consistent source | Additional processing and sensor/temporal alignment burden | Add only after cross-country coverage, QA and leakage review. |
| Surface albedo | Documented MODIS albedo product | Product QA and temporal alignment need checking | Sensitivity run only after coverage and leakage review. |
| Land-cover fractions | Documented global land-cover product | Class proportions are correlated and products may not be annual | Add only if years, classes and boundaries are comparable. Drop one reference class when modelling compositional fractions to avoid perfect collinearity. |
| Building height / density | Harmonised building data if available | Current expected coverage differs between the countries and may bias transfer | Exclude from core model unless quality and completeness are demonstrably comparable. |

Optional variables are not prerequisites for a valid first experiment. A smaller, reliable shared feature set is preferable to a larger but incomparable set.

## 6.3 Product version and time alignment rules

### NDVI

- The NASA MOD13Q1 Version 6 product was decommissioned; NASA encourages Version 6.1. If MOD13Q1 is selected, use an explicitly recorded version (the default recommendation is Version 6.1), apply quality flags and the documented scale factor, and preserve the processing settings.
- Calculate the JJA vegetation value consistently for every selected year. The composite rule (e.g., pixel-level median/quality composite or average of valid composites) must be stated and used for both countries.
- The target and NDVI can share a season but must not reuse target-derived thermal values. NDVI should still be checked against the actual target pipeline and image timing before being declared leakage-free.

### ERA5-Land

- Record the exact product, variables, retrieval date, grid, units and temporal source (hourly or monthly aggregation).
- For 2 m temperature, compute a clearly defined JJA mean and convert units if needed.
- For total precipitation, use a correctly aggregated seasonal total and the product's documented accumulation convention.
- ECMWF describes ERA5-Land as having roughly 9 km grid spacing; this is relatively coarse for small city units. Report this spatial-support limitation.

### Elevation and urban area

- Use a single elevation product/version and the same extraction methodology in both countries.
- Confirm whether source `Area` is in m², km² or another unit before using it.
- If boundaries vary by year, do not pretend the static area attribute captures the yearly urban form; record the definition and consider it a static proxy.

## 6.4 Feature-availability audit — REQUIRED OUTPUT

Before training, create `data/audit_reports/FEATURE_COVERAGE_BY_COUNTRY.csv` and `docs/FEATURE_DATA_DICTIONARY.md`. For every candidate feature, record at least:

- name, source citation, product ID/version and retrieval date;
- spatial resolution, CRS and units;
- valid years and months;
- quality flag / scaling rules;
- spatial support and aggregation method;
- number of valid `UrbanId` records by country × year;
- missing rate by country × year and overall;
- missingness pattern by target sample;
- reason to include/exclude the feature;
- leakage assessment and any product overlap with the target computation.

Feature sources that are not actually downloaded must remain labelled **planned**, not **available**. A table of globally available products is not a feature-coverage audit.

---

# 7. Feature redundancy and preprocessing

## 7.1 Redundancy checks

Potentially redundant predictors include NDVI, NDBI, albedo, land-cover fractions and climate variables. Coordinates may act as proxies for regional climate or continental location rather than directly transferable physical relationships.

Proposed diagnostic tools:

- Pearson correlations for pairwise linear association;
- Spearman correlations for monotonic association;
- VIF as a multicollinearity diagnostic where the selected model/features make it informative;
- feature-distribution summaries separately for China and Türkiye, and a combined view for description only.

Tao proposes a redundancy flag at `|Pearson r| ≥ 0.7` or `VIF ≥ 10`. These thresholds can serve as an initial rule, but should not be treated as universal laws. The final retained feature set must follow a documented decision log.

### Consistent feature-set rule

- Define the same feature definitions and units in both countries.
- Perform supervised feature selection and any model-based selection using source-country training data only.
- Do not use target-country test labels, target-test performance or SHAP results from the locked test set to revise the primary model.
- Use the same final feature definition for both transfer directions in the primary model. If a feature cannot meet the common coverage rule, remove it from the core model in both directions; test alternatives only as clearly labelled sensitivity experiments.
- Latitude/longitude should be included or excluded by a rule specified in advance. A useful planned sensitivity experiment is to compare results with and without coordinates to assess dependence on geographic position.

Land-cover fractions that sum to one are compositionally dependent. If all classes are represented as fractions, omit one reference class from models that require a full-rank design matrix or otherwise use a documented compositional-data strategy.

## 7.2 Missingness and row eligibility: one consistent policy

Tao's initial text mixes row deletion and median imputation. Use the following harmonised rule to prevent the two from contradicting each other.

1. **Missing target:** never impute. Exclude that `UrbanId × year` from labelled modelling for the selected target and record the count/reason.
2. **Feature-level exclusion:** Tao proposes excluding a core feature if more than 30% of eligible records are missing in either country. Treat this as the proposed pre-declared threshold; approve it before reviewing test performance. Re-check the feature's actual coverage after applying the target/year scope.
3. **Remaining predictor missingness:** for features retained under the 30% rule, use median imputation fitted only on the training portion of each CV fold/model fit. Apply the fitted imputer to validation/test predictors without refitting. Do not both drop every row with any predictor missing and then claim median imputation was used.
4. **Adaptation pipeline:** for an adapted model, the imputer may be refitted on the allowed combined source-training plus target-adaptation training rows. Never use target-test values or labels to fit the imputer.
5. **Test sample definition:** apply pre-declared feature availability and target eligibility rules before evaluating models. Report how many target units remain and whether exclusions differ by country or year. Do not adjust exclusions after looking at test scores.
6. Never convert `NA` into zero unless a source-specific definition establishes that zero is correct; the current audit provides no such basis for UHII missing values.

A predictor with missingness below the threshold may be imputed, but the imputation rate and distribution must be reported. Missing data mechanisms are unknown unless independently documented.

## 7.3 Outliers and impossible values

- Calculate IQR thresholds on training data only for the relevant training fold.
- Flag extreme observations for review; do not remove them automatically.
- Remove/correct a value only if it is demonstrably corrupt or physically invalid under a documented rule.
- Retain plausible extremes and report the review decision.
- Do not treat negative SUHII as automatically erroneous.
- Save before/after counts and the reason for each exclusion/correction.

## 7.4 Scaling and transformations

- Linear Regression: include standardization in a fold-safe modelling pipeline where useful for numerical stability/comparable coefficient scales. Fit scaling only on training data.
- Random Forest and XGBoost: normally do not require feature scaling; keep the same leakage-safe split and data preparation discipline.
- Any log transform or skew correction must have a scientific and statistical reason, be appropriate for values including zero/negative values, and be fitted/decided without target-test leakage.

---

# 8. Leakage prevention

Data leakage can come from target construction, temporal overlap, repeated urban units, spatial proximity, preprocessing, feature selection, model tuning or adaptation. The team must check each type explicitly.

## 8.1 Target leakage

- Exclude UHII itself, target-derived values and any direct re-encoding of the target from predictors.
- Preserve the original target files as immutable inputs.
- Record the target field's exact temperature source and construction method.
- Do not assume NDVI, NDBI or albedo are leakage-free solely because they have different names or bands. Check acquisition dates and the actual target calculation pipeline.
- If a selected target product reuses LST from a source that is also proposed as a predictor, document why the predictor is independent enough for the intended prediction setting, or exclude it from the core model.
- If urban/rural raw LST data and masks are available, independently verify a pre-specified random sample of approximately 100 `UrbanId × year` records, balanced across countries where sample sizes permit. Record formula, masks, source files, residual discrepancies and tolerance. Do not imply this recomputation has already been done.

## 8.2 Spatial and group leakage

- Every `UrbanId` and all years belonging to it must remain in the same source CV fold or target partition.
- Never randomly split individual `UrbanId × year` rows.
- For the target-test experiment, the target `UrbanId` set must be disjoint from target adaptation and development IDs.
- A city-ID group split does not necessarily separate nearby urban units. Where feasible, perform spatially blocked validation as a robustness check. Define block construction and block size before reviewing model scores.
- Report both observation-row count and unique `UrbanId` count for every split.

## 8.3 Preprocessing and model-selection leakage

The following must be fitted using permitted training data only: imputation, scaling, feature-selection filters, transformations, hyperparameter search and model selection. The held-out target test labels must not be used at any stage of development or adaptation. Apply fitted transforms to held-out predictors without refitting on test data.

## 8.4 Target-country covariates versus labels

In a realistic transfer setting, target-test predictor values are available at prediction time, but target-test **labels** must remain hidden. This protocol does not allow target-test labels or test performance to influence model choices. If any unsupervised procedure is later allowed to use the distribution of target predictors, it must be explicitly predeclared as a transductive method and must not be mixed with the current source-statistics-only protocol.

---

# 9. Models and tuning protocol

## 9.1 Candidate models

| Model | Role | Notes |
|---|---|---|
| Source-mean predictor | Non-learning baseline | Predicts the mean target value in the source training data for every target observation. Its target-test R² is not assumed to equal zero. |
| Linear Regression | Interpretable regression baseline | Captures linear effects; standardize predictors within a fold-safe pipeline if needed. |
| Random Forest Regressor | Nonlinear tabular model | Can model nonlinear relationships and interactions; tune depth, tree count, leaf sizes and feature subsampling using source-only CV. |
| XGBoost Regressor | Gradient-boosted tree model | Can model nonlinear tabular patterns; tune depth, learning rate, estimator count, subsampling and regularization using source-only CV. |

The source-mean predictor is separate from Linear Regression. Do not refer to all of them as “the baseline” without specifying which baseline is meant.

## 9.2 Hyperparameter tuning

Tao proposes RandomizedSearchCV with 50 draws per model, fixed random seeds and GroupKFold-like splits grouped by `UrbanId`. This is a reasonable starting point if computational resources and source sample counts support it.

**Harmonised default protocol:**

1. Finalize eligible records and the locked target test UrbanIds first.
2. Within the source country only, tune each model using grouped cross-validation with groups defined by `UrbanId`. A proposed default is 5 folds, provided each fold has sufficient urban units. Reduce folds only with a documented reason.
3. Run randomised hyperparameter search with 50 draws as a starting plan; record search spaces and seed values. If compute constraints require fewer draws, record the deviation before looking at target-test outcomes.
4. For the cross-country final model, select the model family and hyperparameters using the predeclared source-only criterion (Tao proposes grouped CV R² as primary tuning criterion; MAE/RMSE remain mandatory secondary metrics).
5. Refit the selected specification on all eligible source-country training UrbanIds using the fitted modelling pipeline; predict the locked target-test data once per predeclared experiment.
6. If the team also reports unbiased **within-source-country** performance, use a separate nested grouped CV estimate or spatially blocked validation. Do not mix these source-domain scores with cross-country target-test scores.

This replaces the ambiguous combination of a fixed 80/20 source split and nested grouped CV unless the team explicitly implements both for separate purposes. The final config must say which data are used for tuning, which scores choose the model, and which split provides the final metric.

All random seeds and software versions must be recorded. Tao's draft proposes Python 3.10, `scikit-learn==1.3.0` and `xgboost==2.0.0`; these are proposed reproducibility pins, not a statement that the current environment is already using them. If different versions are installed, record the actual versions and test compatibility rather than silently claiming the proposal was used.

---

# 10. Cross-country test design and benchmarks

## 10.1 Two primary transfer directions

Both directions are primary research questions and must be reported separately.

### Experiment A — China → Türkiye

- **Source:** eligible Chinese `UrbanId × year` records.
- **Source tuning:** grouped by Chinese `UrbanId`; all years for a city remain together.
- **Target pool:** eligible Turkish UrbanIds, partitioned into a locked test set and a disjoint adaptation pool before training.
- **Target test:** Turkish UrbanIds unseen in source training and not used in any adaptation/development decision.

### Experiment B — Türkiye → China

- **Source:** eligible Turkish `UrbanId × year` records.
- **Source tuning:** grouped by Turkish `UrbanId`; all years for a city remain together.
- **Target pool:** eligible Chinese UrbanIds, partitioned into a locked test set and a disjoint adaptation pool before training.
- **Target test:** Chinese UrbanIds unseen in source training and not used in any adaptation/development decision.

Because the current mapping has 1,441 China units and 180 Türkiye units before target/feature filtering, the source and target sample sizes differ strongly by direction. Report this imbalance, test-set uncertainty and the actual retained counts. Do not infer that all eligible mapped units remain after target/features are filtered.

## 10.2 Partition policy

- **Sampling unit:** `UrbanId`, never individual rows.
- **Initial target holdout:** lock a target-country test group before tuning or adaptation. Tao's draft does not establish a justified final percentage; use a predeclared grouped holdout (e.g., 20% if the post-filter sample supports it) or a spatial-blocked holdout if the team can define robust geographic blocks. Freeze the exact ID list and seed.
- **Target adaptation pool:** all eligible target-country UrbanIds not in test, minus any separately designated development set if needed.
- **No overlap:** test IDs must not appear in adaptation training, target-only training, feature/model selection or imputation fitting.
- **Coordinates:** use only according to the feature plan, but may be used for predeclared spatial grouping / diagnostics. A spatial holdout's construction cannot be chosen after comparing test model scores.
- Save the ID lists and row counts before model evaluation. The test labels must be inaccessible to the tuning/adaptation code paths until the final evaluation step.

If the final eligible Turkish city count becomes too small for a stable 20% split or 5-fold CV, lower-fold or alternate split choices may be necessary. Define the minimum group counts and decision rule before training.

## 10.3 Required benchmark models

1. **Source-mean baseline:** predict the mean target value of the source training rows for all target-test rows. Calculate actual target-test R², MAE and RMSE. Do not claim its R² is necessarily zero; the mean of the source country generally differs from the mean of the target test labels.
2. **Direct transfer model:** fit only on source-country data and evaluate on the untouched target test.
3. **Target-country-only reference model:** train using target-country labelled data outside the locked test set. Ideally report (a) a matched-label-budget local model using the same target adaptation sample sizes and (b) an available-local-data reference trained on the full non-test target pool where sample size permits. This is a reference, not a guaranteed mathematical upper bound.
4. **Within-country validation:** optional/supplementary GroupKFold or spatially blocked evaluation within each country. Report separately; do not compare those metrics as if they were cross-country test metrics.

All comparisons of models or adaptation levels must use exactly the same target-test observations within each direction, except if a predeclared missingness rule makes that impossible. If test rows differ, state why and do not present the values as a like-for-like comparison.

---

# 11. Supervised target-country adaptation experiment

## 11.1 Primary adaptation method

Use the single primary method proposed by Tao: **supervised combined-data retraining**. Refit the selected model on source-country training data plus a small labelled sample from the target-country adaptation pool. Do not confuse this with residual correction, recalibration or unsupervised domain adaptation.

## 11.2 Sample-size design

Proposed target adaptation ratios: **1%, 5%, 10%, 20% and 50%** of the eligible target adaptation pool, not of the whole target-country dataset. The sampling unit is whole `UrbanId` groups; if an ID has multiple eligible years, all those rows remain together.

- Lock target-test IDs first.
- Use nested sampling within each random seed so larger samples include the smaller samples when feasible.
- Use 10 fixed/reproducible random seeds as Tao proposes, subject to feasibility.
- If 1% rounds to zero UrbanIds, include one UrbanId only if that rule is predeclared, and report the actual count rather than label it as an exact 1% sample.
- Record the actual number of UrbanIds, urban units, rows and years selected at every ratio.
- If a tiny sample is too small to support a stable estimate, report that limitation; do not overinterpret apparent gains/losses.
- Keep the target test set constant across ratios and seeds.

A performance plateau cannot be firmly claimed unless the sample-size curve contains sufficient range and uncertainty analysis. If the study stops at 50%, describe only the observed response over the tested range.

## 11.3 Preprocessing and tuning during adaptation

- Freeze hyperparameters based on the predeclared source-only tuning procedure before running adaptation.
- At each ratio, fit the model only on source training rows plus that ratio's labelled target adaptation rows.
- Refit imputation/scaling on the allowed combined training data if the model's predeclared adaptation pipeline specifies this; never fit on target-test data.
- Do not use target-test labels for selecting adaptation ratio, tuning the model or choosing which seed's result to report.
- Preserve all adaptation membership lists in a manifest.

## 11.4 Required adaptation comparisons

- Direct source-only transfer.
- Source + target adaptation rows at each target-label sample size.
- Target-only model with the same target-label budget, where feasible.
- Target-only model using the full non-test labelled target pool, as a local-data reference, where feasible.

Report mean, median, standard deviation/range and confidence intervals across repeats where statistically defensible. Ten random seeds alone are not a substitute for a well-defined uncertainty method; use the city as the resampling unit when bootstrapping.

---

# 12. Evaluation metrics and uncertainty

## 12.1 Required metrics

- **R²:** performance relative to target-test variability. Values near 1 generally indicate strong fit; 0 means performance equivalent to predicting the **test-set mean** under the standard formula; negative values mean worse performance than that reference. A source-mean predictor does not automatically have R² = 0 on the target test.
- **MAE (°C):** average absolute prediction error in the target's temperature-difference unit.
- **RMSE (°C):** square-root mean squared error, more sensitive to large errors.

Report all three for each model and direction. Also report target-test target variance, the number of evaluated rows, number of unique `UrbanId` groups, selected years, target units and split design.

## 12.2 Uncertainty and city dependence

Repeated years from one urban unit are not independent cities. For transfer-model uncertainty, use a predeclared city-level bootstrap of target-test `UrbanId` groups (Tao proposes 1,000 replicates) where the number of test groups supports it. All years for a sampled city should travel together in a bootstrap draw.

For adaptation, quantify variability across the repeated city-level adaptation samples. Report mean and spread across seeds; where possible, add a city-group bootstrap confidence interval. Do not present the 10 seeds as 10 independent target populations.

For paired model comparisons, compute metric differences on the same target-test IDs and observations. If confidence intervals for a difference are used, describe the resampling unit and interval method. Do not make casual “statistically significant” claims from simple score differences; any inferential rule must be predeclared.

## 12.3 Row-weighted versus city-weighted results

If one city contributes more valid years than another, row-level metrics can give that city more weight. The report must state whether the primary metric is row-weighted over `UrbanId × year` observations. A useful sensitivity summary is also to calculate errors at city level (e.g., average within-city error, then compare across cities), provided it is defined before results are inspected. Never treat repeated years as independent cities for confidence intervals.

---

# 13. SHAP and interpretation

SHAP is a post-evaluation interpretation tool, not proof of causality or physical mechanism.

## 13.1 Proposed protocol

- Run SHAP only after the primary model-selection protocol and target-country test evaluation are frozen.
- Explain the selected tree model (Random Forest or XGBoost, according to the predeclared model-selection outcome). Tao suggests XGBoost with `shap.TreeExplainer`; use XGBoost specifically only if it is the selected model or predeclare it as a separate interpretation model.
- Use a reference/background sample drawn from source-training data only; Tao proposes 200 observations where the sample size permits.
- Explain source-domain predictions and target-country transfer predictions separately.
- Compare feature attributions cautiously across countries; differences may be caused by distribution shift, correlated features, coverage/measurement differences or model behaviour, not only different UHI physics.
- Describe correlated predictors (NDVI, NDBI, land-cover fractions, albedo and climate variables) and the resulting instability/shared attribution of importance.
- SHAP describes model attribution/associations, not causal effects.

If inspecting SHAP leads to changes in feature set, tuning or model selection, the previous target-test results are no longer an untouched final evaluation of that revised model. Use a new reserved test set or label the revised evaluation exploratory.

---

# 14. Limitations to declare in the eventual paper

1. **Archive provenance:** exact local archive snapshot is not independently verified by checksum; original source record and download route are documented.
2. **Dataset / urban-boundary definition:** urban boundaries and background/rural masks depend on the UHII source definition and version; a shift to the separate updated record must be documented.
3. **Unequal sample size:** the mapped sample currently contains substantially more Chinese than Turkish urban units. Directional results and uncertainty should be interpreted in light of this imbalance.
4. **Sample representation:** the primary sample represents urban units available in the chosen dataset and country-mapping method, not every city in either country.
5. **Remote-sensing uncertainty:** satellite LST/UHII can contain retrieval, cloud/quality and compositing uncertainties; specific missing-value causes in the local data remain unknown unless the data producer documents them.
6. **Reference-area uncertainty:** the MEA rural/background mask must be understood from source documentation and be comparable across countries.
7. **Temporal limitation:** a three-year design (if retained) covers little interannual variation; any sparse-year selection must be justified.
8. **Spatial resolution mismatch:** MODIS NDVI, a DEM and coarse ERA5-Land grids have different native spatial resolutions and spatial supports.
9. **Unobserved drivers:** anthropogenic heat emissions and other factors may not be available as harmonised cross-country features.
10. **Prediction rather than causation:** machine learning models describe predictive associations; they do not establish that a feature causes urban warming.
11. **Transfer scope:** success on China and Türkiye does not demonstrate transfer to all countries or climate zones.
12. **Geometry fallback:** if point/buffer extraction is used instead of urban-polygon averages, the measurement support must be described and its limitation stated.

---

# 15. Reproducibility and file outputs

All primary decisions, split lists and experiment configurations must be version-controlled. Large raw data should remain outside the repository.

## 15.1 Proposed repository structure

```text
urban-heat-transfer/
├── README.md
├── .gitignore
├── docs/
│   ├── MASTER_RESEARCH_PROTOCOL.md
│   ├── DATASET_PROVENANCE.md
│   ├── DATA_QUALITY_AUDIT_NOTES.md
│   ├── TARGET_DEFINITION.md
│   ├── FEATURE_DATA_DICTIONARY.md
│   ├── EXPERIMENT_PROTOCOL.md
│   ├── LIMITATIONS.md
│   └── DECISION_AND_DEVIATION_LOG.md
├── data/
│   ├── CityInfo.csv
│   ├── CityInfo_with_Country.csv
│   ├── audit_reports/
│   │   ├── UHII_Final_Audit_Summary.txt
│   │   ├── UHII_Final_Mapping_Audit.csv
│   │   ├── UHII_Final_File_Audit.csv
│   │   ├── UHII_Final_Country_NA_Audit.csv
│   │   ├── UHII_Final_Coverage_Audit.csv
│   │   ├── UHII_Final_Audit_Issues.csv
│   │   ├── UHII_Final_Value_Ranges.csv
│   │   ├── Country_Mapping_13_Row_Comparison.csv
│   │   ├── TARGET_YEAR_COVERAGE.csv
│   │   ├── FEATURE_COVERAGE_BY_COUNTRY.csv
│   │   └── GEOMETRY_QA_REPORT.csv
│   ├── splits/
│   │   ├── target_test_cn_urbanids.csv
│   │   ├── target_test_tr_urbanids.csv
│   │   ├── source_cv_folds_cn.csv
│   │   ├── source_cv_folds_tr.csv
│   │   └── adaptation_sample_manifest.csv
│   └── processed/
│       ├── target_table.csv
│       ├── feature_table.csv
│       └── modelling_table.csv
├── scripts/
│   ├── UHII_Final_Audit.ps1
│   ├── build_target_table.py
│   ├── audit_feature_coverage.py
│   ├── extract_features.py
│   ├── build_splits.py
│   ├── train_and_evaluate.py
│   └── adaptation_experiment.py
└── results/
    ├── model_metrics.csv
    ├── adaptation_metrics.csv
    ├── bootstrap_intervals.csv
    ├── feature_correlations.csv
    └── figures/
```

This is a proposed layout; do not create empty placeholder files and mark the work completed. Only include scripts/results after they exist and have been tested. Do not commit raw UHII files or large external raster sources.

## 15.2 Experiment manifest

Every run must store:

- source archive and version wording;
- selected indicator prefix, diurnal period, target field and seasonal rule;
- target years, units, minimum-month rule if applicable, QA filters and exclusion counts;
- features, product/version, source links, processing, aggregation and units;
- geometry source/version, CRS, area/buffer calculation and spatial extraction settings;
- country-mapping source and `UrbanId` inclusion/exclusion list;
- train/validation/test city IDs and row counts;
- adaptation sample IDs, ratio, seed and repeat number;
- preprocessing pipeline and where each fitted transform obtained its training data;
- model family, software/package versions, hyperparameters and seed;
- metrics, bootstrap settings and result file paths;
- any deviation from this protocol, date, reason, and whether it occurred before or after target-test evaluation.

Save split assignments and sampled `UrbanId` lists so rerunning the code does not silently change the experiment.

---

# 16. Decision register before full modelling

| ID | Decision / check | Current status | Evidence already available | Required action to mark resolved | Owner proposal |
|---|---|---|---|---|---|
| D01 | Original UHII source record | Documented | Original Figshare URL/DOI, related paper and download route are recorded | Keep source citation and retrieval record in project docs | Mert |
| D02 | Exact local archive snapshot | Documented — not independently verified | Local archive/checksum not found in current project inventory | Keep cautious wording; only verify byte-level snapshot if original archive/checksum can be recovered | Mert/shared |
| D03 | Whether to adopt the separate updated UHII record | Open blocker | Separate update announcement describes ESA CCI base map and added urban/rural extents | Compare target fields, IDs, geometry, coverage and audit requirements; decide Path A or Path B | Shared |
| D04 | Indicator / temperature product prefix | Open blocker | Eight prefixes and their filename coverage inventoried | Read source README, choose one primary prefix and justify target construct/coverage | Tao + shared |
| D05 | Diurnal field | Proposed | Filenames encode `Day`/`Nig`; Tao proposes nighttime | Confirm selected product metadata; freeze `Nig` if supported by the chosen study question | Tao |
| D06 | UHII method | Proposed | `Intensity_EA`, `Intensity_IEA`, `Intensity_MEA`, `Intensity_DEA` exist; Tao proposes MEA | Confirm definition of MEA from source; document rationale and field mapping | Tao |
| D07 | JJA aggregation | Open blocker | Archive period `22` is JJA per current file naming; Tao proposes monthly mean with ≥2 valid months | Read source aggregation metadata; compare native period 22 with month-derived mean on a sample; select one primary rule | Shared |
| D08 | Target years | Open blocker | Filename coverage audit completed; Tao proposes 2005, 2010, 2015 | Generate target/feature coverage over all candidate years; select all shared eligible years or document fixed-year rationale | Mert + Tao |
| D09 | Target recalculation check | Proposed | Target-specific independent validation not yet evidenced | If raw LST and masks exist, validate a balanced sample of ~100 records; otherwise document why only archive value checks are possible | Tao |
| D10 | Country mapping | Completed for main sample | Mapping audit and 13-row comparison; 1,441 China + 180 Türkiye | Keep 13 candidates and all 83 blank labels outside primary sample unless new evidence changes this | Mert |
| D11 | Urban polygon geometry availability | Open blocker | Current `CityInfo` inventory has coordinates and area attributes; polygon/mask presence not confirmed | Inventory actual geometry/mask files and validate join to `UrbanId`; if unavailable, decide a non-polygon feature strategy or evaluate updated archive | Shared |
| D12 | Area / CRS method | Open blocker | Tao proposed EPSG:3857; this is not suitable as authoritative area method | Select suitable equal-area/geodesic area procedure; document projection/buffer methods and units | Tao + geospatial support |
| D13 | Core features | Proposed | Tao proposes NDVI, ERA5-Land JJA temperature/precipitation, DEM elevation, urban area and coordinates | Confirm product versions; only retain features with acceptable coverage and valid extraction | Tao |
| D14 | Feature coverage and missingness | Open blocker | No completed project-specific feature coverage report evidenced | Generate per-country/per-year CSV report and data dictionary | Tao |
| D15 | Predictor missing data policy | Proposed | UHII `NA` rules are documented; features not yet final | Use >30% country-specific missingness as proposed feature exclusion threshold; median-impute remaining predictor gaps only inside each training fold | Shared |
| D16 | Outlier handling | Proposed | One first-pass outlier is documented | Use train-only IQR flags; review, never auto-drop plausible extremes | Shared |
| D17 | Feature redundancy rule | Proposed | Tao proposes Pearson/Spearman/VIF screening | Freeze thresholds and common retained feature-set rule before fitting primary models | Tao |
| D18 | Cross-country split | Proposed | Correct requirement to keep all years of each `UrbanId` together | Build immutable target test IDs and source grouped folds; publish row and unique-ID counts | Shared |
| D19 | Tuning design | Proposed | Tao proposes RandomizedSearchCV, 50 draws, GroupKFold, seed 42 | Freeze exact CV nesting, group design, hyperparameter spaces and primary score | Tao |
| D20 | Mean baseline interpretation | Correction required | Tao draft incorrectly says source-mean baseline corresponds to R² = 0 | Remove claim; compute actual R²/MAE/RMSE on same target test | Tao |
| D21 | Target-country-only comparison | Correction required | Draft uses term “upper bound” ambiguously | Train only on non-test target data; call it a target-only reference and ensure no test-label use | Tao |
| D22 | Adaptation sample sizes | Proposed | 1%, 5%, 10%, 20%, 50%; whole IDs and 10 seeds proposed | Freeze target pool and test IDs first; record actual city/row counts per sample | Tao |
| D23 | Metrics and uncertainty | Proposed | R²/MAE/RMSE and city bootstrap are proposed | Freeze metric priority, city-level bootstrap and reporting format | Shared |
| D24 | SHAP | Later | Interpretation plan drafted | Run only after model/test evaluation is frozen; interpret attribution, not causality | Tao |
| D25 | Reproducibility and documentation | In progress | Existing audit/provenance files and progress log exist | Consolidate final protocol, config, manifest, outputs and deviation log | Shared |

---

# 17. Go/no-go checklist before full model training

Full modelling is **NO-GO** until all mandatory checks below are resolved. Lightweight file inspection and feature-feasibility prototypes are permitted before then, as long as their results are labelled exploratory and are not presented as final model experiments.

## P0 — mandatory blockers

- [ ] Chosen UHII archive path and the source-version wording are documented.
- [ ] One indicator / temperature product prefix is selected; its scientific definition and coverage are verified.
- [ ] One diurnal field and one target method (`Intensity_MEA` if adopted) are frozen.
- [ ] Native JJA period-22 versus monthly-derived JJA aggregation is resolved and documented.
- [ ] Target units, sign convention, eligibility rules and candidate years are recorded.
- [ ] `TARGET_YEAR_COVERAGE.csv` shows valid target counts by country and year and justifies the year range.
- [ ] Compatible urban polygons/masks are located and validated, **or** the team explicitly changes the feature extraction strategy and its claims.
- [ ] Area / centroid semantics and units are understood; EPSG:3857 is not used for authoritative area calculation.
- [ ] Core features have actual source/version, temporal coverage, spatial extraction and leakage checks.
- [ ] `FEATURE_COVERAGE_BY_COUNTRY.csv` and `FEATURE_DATA_DICTIONARY.md` are created from real downloaded/extracted data.
- [ ] Final eligible `UrbanId × year` counts and country-specific exclusions are calculated after applying target and feature rules.
- [ ] Immutable target-test ID lists and source grouped-CV split manifests are saved.
- [ ] Mean-baseline, target-only-reference and direct-transfer comparisons are specified without test leakage.

## P1 — must be frozen before primary test results are inspected

- [ ] Core feature set and redundancy-selection rule are frozen.
- [ ] Missing-predictor and outlier policies are consistent, implemented in training pipelines and documented.
- [ ] Hyperparameter space, random seeds, package versions, CV groups and model-selection metric are recorded.
- [ ] The primary metric and operational interpretation rule for useful transfer are predeclared.
- [ ] Adaptation sampling ratios, seeds, sampling unit and permitted use of adaptation labels are frozen.
- [ ] Bootstrap/uncertainty procedure and result tables are defined.

## P2 — after a valid primary evaluation

- [ ] SHAP analysis and interpretation figures are created.
- [ ] Sensitivity analyses are run (alternative target aggregation, target method, feature subsets and with/without coordinates, where justified).
- [ ] Final scientific discussion, limitation section and GitHub README are completed.

---

# 18. Action plan and ownership

This action plan is designed to build on the completed work, not repeat it.

## Step 1 — Reuse the existing audit artifacts (Mert)

**Inputs already available:** `UHII_Final_Audit_Summary.txt`, the file/mapping/coverage audit reports, `DATA_QUALITY_AUDIT_NOTES.md`, `DATASET_PROVENANCE.md`, and `Country_Mapping_13_Row_Comparison.csv`.

**Actions:**

- Keep these as the authoritative baseline audit records.
- Update documentation only if a new target-specific analysis reveals an issue; do not rerun the all-file audit unless the underlying archive changes or a specific failure justifies it.
- Preserve the primary mapping of 1,441 Chinese + 180 Turkish urban units and the exclusion of 83 blank country labels unless new verified evidence supports a change.

**Outputs:** existing report set retained; the new main document references it.

## Step 2 — Resolve source and target identity (Tao + Mert)

**Actions:**

- Read the source dataset README and document the selected prefix definitions, MEA method, unit and season-period coding.
- Inventory local geometry files and investigate what the separate updated record actually supplies.
- Decide whether the target remains the original archive or whether the project switches to the separate updated archive. Do not combine both implicitly.
- Compare native JJA period 22 with the candidate monthly calculation on a reproducible sample.
- Select one target prefix/method/diurnal/period/year rule and record it in `TARGET_DEFINITION.md`.

**Outputs:** `TARGET_DEFINITION.md`, source decision in `DECISION_AND_DEVIATION_LOG.md`, sample-comparison table if computable.

## Step 3 — Generate target-year and target-record coverage (Mert)

**Actions:**

- Use the existing inventory and audit reports to avoid re-scanning unrelated files.
- For every candidate year under the selected prefix and night/day field, compute valid target counts for China and Türkiye.
- Evaluate all common candidate years first. If the team retains 2005/2010/2015 only, document the reason.
- Apply the predeclared valid-target rule and count retained `UrbanId × year` records.

**Output:** `data/audit_reports/TARGET_YEAR_COVERAGE.csv` plus a short year-selection note.

## Step 4 — Decide geometry and create verified predictors (Tao + Mert)

**Actions:**

- Confirm polygon/mask availability and `UrbanId` linkage.
- Select consistent geospatial measurement methods, avoiding EPSG:3857 for authoritative area calculations.
- Retrieve/process the common core features using documented versions and the exact target seasons/years.
- Produce missingness and coverage per country/year, including post-QA valid-pixel counts where relevant.
- If polygons are unavailable, pause polygon zonal statistics and agree on an explicitly named point/buffer alternative or source change.

**Outputs:** `FEATURE_DATA_DICTIONARY.md`, `FEATURE_COVERAGE_BY_COUNTRY.csv`, `GEOMETRY_QA_REPORT.csv`, feature-extraction scripts and a first feature table.

## Step 5 — Freeze the modelling table and split manifests (Shared)

**Actions:**

- Merge target and predictor tables by `UrbanId` and year using one-to-one / many-to-one validation appropriate to the schema.
- Check duplicates, row counts, `UrbanId` coverage, target units, feature units and missingness.
- Create one immutable target-test group per direction, and source grouped CV folds.
- Generate manifests with both rows and unique IDs, check disjointness programmatically and save them.
- Freeze the experiment configuration before looking at target-test scores.

**Outputs:** `modelling_table.csv`, `data/splits/*.csv`, `experiment_config.yaml` (or JSON), and a pre-model split audit report.

## Step 6 — Fit models and evaluate transfer (Tao leads, Shared review)

**Actions:**

- Train source mean, Linear Regression, Random Forest and XGBoost using the approved pipelines.
- Tune using source-only grouped CV.
- Evaluate once on the locked target test per predeclared model and direction.
- Record R², MAE, RMSE, target variance, eligible rows, unique UrbanIds and split details.
- Run target-country-only reference experiments without test IDs.

**Outputs:** `model_metrics.csv`, plots and a reproducible run log.

## Step 7 — Run adaptation and uncertainty analyses (Tao leads, Shared review)

**Actions:**

- Keep the same target test IDs for all sample sizes and random seeds.
- Run 1%, 5%, 10%, 20% and 50% target adaptation samples or document why a level is infeasible.
- Report actual sample sizes, mean/spread over seeds and city-level uncertainty.
- Avoid claiming saturation unless the tested range supports it.

**Outputs:** `adaptation_sample_manifest.csv`, `adaptation_metrics.csv`, `bootstrap_intervals.csv` and adaptation curve figures.

## Step 8 — Explain, report and publish (Shared)

**Actions:**

- Run SHAP only after the primary modelling decisions are frozen.
- Compare transfer directions and adaptation curves without making causal claims.
- Write limitations and cite the source dataset/product documentation.
- Finalize README and keep large raw data out of GitHub.

**Outputs:** result interpretation, final report, figures, project README and updated decision/deviation log.

---

# 19. Required result-table templates

## 19.1 Target coverage table

| Indicator prefix | Diurnal | Target method | Period/year | Country | UrbanIds with valid target | Valid `UrbanId × year` rows | Exclusion count | Notes |
|---|---|---|---|---|---:|---:|---:|---|
| To be filled from audit | Nig (proposed) | MEA (proposed) | To be selected | China | — | — | — | — |
| To be filled from audit | Nig (proposed) | MEA (proposed) | To be selected | Türkiye | — | — | — | — |

Do not leave the dashes in a final report; fill them from actual calculations or explain why no calculation could be performed.

## 19.2 Feature coverage table

| Feature | Source/version | Year/season | Country | Eligible UrbanIds | Valid rows/pixels | Missing rate | Spatial support | Include/exclude decision |
|---|---|---|---|---:|---:|---:|---|---|
| NDVI | To be verified | JJA/year | China | — | — | — | Polygon or declared alternative | — |
| NDVI | To be verified | JJA/year | Türkiye | — | — | — | Polygon or declared alternative | — |
| ERA5-Land temperature | To be verified | JJA/year | China | — | — | — | Polygon or declared alternative | — |
| ERA5-Land temperature | To be verified | JJA/year | Türkiye | — | — | — | Polygon or declared alternative | — |

Add rows for precipitation, elevation, area, coordinates and optional features.

## 19.3 Primary model results

| Direction | Model | Target test rows | Target test UrbanIds | R² | MAE (°C) | RMSE (°C) | Baseline comparison | CI / uncertainty | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|---|
| China → Türkiye | Source mean | — | — | — | — | — | Reference | — | — |
| China → Türkiye | Linear Regression | — | — | — | — | — | — | — | — |
| China → Türkiye | Random Forest | — | — | — | — | — | — | — | — |
| China → Türkiye | XGBoost | — | — | — | — | — | — | — | — |
| Türkiye → China | Source mean | — | — | — | — | — | Reference | — | — |
| Türkiye → China | Linear Regression | — | — | — | — | — | — | — | — |
| Türkiye → China | Random Forest | — | — | — | — | — | — | — | — |
| Türkiye → China | XGBoost | — | — | — | — | — | — | — | — |

## 19.4 Adaptation results

| Direction | Adaptation ratio | Actual target UrbanIds | Rows used for adaptation | Seed | R² | MAE (°C) | RMSE (°C) | Compared with no-adaptation | Notes |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| To be filled | 1% | — | — | — | — | — | — | — | — |
| To be filled | 5% | — | — | — | — | — | — | — | — |
| To be filled | 10% | — | — | — | — | — | — | — | — |
| To be filled | 20% | — | — | — | — | — | — | — | — |
| To be filled | 50% | — | — | — | — | — | — | — | — |

---

# 20. Decision and deviation log template

Every change after this protocol is adopted must be documented here. A change to target, indicator, period, feature set or test split can affect the scientific interpretation and may require a new test set.

| Date | Decision / deviation | Reason and evidence | Affected files/experiments | Before or after target-test results? | Approved by |
|---|---|---|---|---|---|
| 2026-10-11 | Consolidated prior audit evidence and Tao's research protocol into one master plan | Existing audit/provenance records and Tao's revised protocol | Master protocol | Before modelling | Mert + Tao to confirm |
| To be filled | | | | | |

---

# 21. References and verified data documentation

The references below should be supplemented with product guides and scientific literature actually used in the final implementation. Access date for dynamic pages: 11 October 2026 unless stated otherwise.

1. Yang, Q., Xu, Y., Chakraborty, T. C., et al. (2024). *A global urban heat island intensity dataset: Generation, comparison, and analysis*. **Remote Sensing of Environment, 312**, 114343. <https://doi.org/10.1016/j.rse.2024.114343>
2. Yang, Q. (2024). *Global Urban Heat Island Intensity Dataset*. Figshare, original record (currently displays Version 3). <https://doi.org/10.6084/m9.figshare.24821538>
3. Separate updated dataset record: *Global Urban Heat Island Intensity Dataset (Version 2)*, with ESA CCI urban-area base map and additional spatial extents per the authors' update notice. <https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset_Version2_/30102847>
4. Community dataset issue documenting UHII filename conventions and the September 2025 update announcement. <https://github.com/samapriya/awesome-gee-community-datasets/issues/276>
5. NASA MODIS/Terra Vegetation Indices MOD13Q1 Version 6.1 product information. <https://data.nasa.gov/dataset/modis-terra-vegetation-indices-16-day-l3-global-250m-v061-2eb0d>
6. NASA note that MOD13Q1 Version 6 was decommissioned and Version 6.1 is recommended. <https://data.nasa.gov/dataset/modis-terra-vegetation-indices-16-day-l3-global-250m-sin-grid-v006>
7. European Centre for Medium-Range Weather Forecasts (ECMWF). ERA5-Land product overview; approximately 9 km grid spacing. <https://www.ecmwf.int/en/era5-land>
8. ECMWF/Copernicus ERA5-Land data documentation. <https://confluence.ecmwf.int/pages/viewpage.action?pageId=501029136>

## Reference-use rules

- Cite the product documentation for the exact product version and processing details used, not only its landing page.
- Add an appropriate scientific reference when justifying the MEA target, summer period, spatial validation, adaptation design, and metric interpretation.
- Do not cite a newer dataset record as if it were the exact version of the local archive unless the project adopts that record.
- Do not claim any external product was downloaded, processed or verified until the corresponding project artifacts exist.

---

# 22. Consolidated final position

The project has already completed the broad technical audit of the local UHII archive and the primary country-mapping review. Those accomplishments should remain part of the official project record. Repeating the entire audit is unnecessary unless the data source changes or a new problem is discovered.

Tao's revised protocol provides a strong scientific structure: two-direction transfer, a shared feature set, group-aware validation, multiple regression models, an untouched target test set, supervised adaptation, appropriate error metrics, SHAP with non-causal interpretation, and reproducibility tracking. Those components are retained here.

The merged protocol also resolves or explicitly flags the problems identified during review:

- no false claim that source-mean predictions always yield R² = 0;
- no target-country-only “upper bound” trained with test labels;
- no simultaneous, unexplained fixed 80/20 split and nested CV instruction;
- no contradictory rule to drop every missing-feature row while also median-imputing it;
- no use of EPSG:3857 as the authoritative area-measurement CRS;
- no unverified claim that current `CityInfo` attributes provide polygons for zonal statistics;
- no assumption that source period-22 JJA values equal arithmetic means of monthly UHII;
- no assertion that 2005, 2010 and 2015 are the only appropriate years before a real target/feature coverage audit;
- no mixing of the original Figshare archive and the separate updated dataset record without a decision and compatibility check.

**Next decision point:** the team should jointly sign off the source/geometry path, exact target identity, seasonal calculation and eligible year set. Once those are fixed, the project can move directly from the existing audit evidence to the target and feature coverage reports, then to the frozen modelling table and split manifests. That is the shortest defensible route forward.
