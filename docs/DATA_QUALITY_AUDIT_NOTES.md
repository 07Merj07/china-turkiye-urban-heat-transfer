# Data Quality Check Notes

**Project:** Can Urban Heat Models Cross Borders? Quantifying the Transferability of Urban Heat Models Between China and Türkiye

**Why this file exists:** This file records the data checks completed before model development. It explains what we checked, what we found, and what still needs to be confirmed. We can use it as a record while developing the project. The final paper should include a shorter summary in its Data and Methods sections.

## 1. Overall result

The local dataset files passed the structural checks in our final audit. The script found no problems with file structure, urban IDs, expected data coverage, or numeric values other than `NA` entries. These results apply to the checks listed in this file. They do not prove that every measurement is scientifically correct. The user confirmed that the files were downloaded using **Download all** from the official Figshare record linked below; that record currently displays Version 3. The original downloaded archive is not kept in the project folder, so the source path is documented but a separate file-by-file archive check is not available.

## 2. City information and country labels

We checked the following files:

- `CityInfo.csv` has 10,196 rows and 10,196 unique `UrbanId` values. There are no blank IDs or duplicate rows.
- `CityInfo_with_Country.csv` also has 10,196 rows and 10,196 unique `UrbanId` values. There are no blank IDs or duplicate rows.
- Both files contain the same set of IDs. We found no differences in the ID lists and no differences in the coordinates or area values across the 30,588 cells compared.

The main country sample currently contains **1,441 urban units in China** and **180 in Türkiye**. We keep the **83 rows with blank country labels** outside the primary comparison unless a country assignment can be supported by a clear and consistent rule.

We compared `CityInfo_with_Country.csv` with `China_Turkiye_city_mapping.csv` by `UrbanId`. The second file contains **13 additional labelled rows**: 10 labelled as China and 3 labelled as Türkiye. All 13 IDs are present in the main file, but their `Country` labels are blank there. Their longitude, latitude, and area values match between the two files. The exact IDs and assigned labels are listed in `Country_Mapping_13_Row_Comparison.csv`.

This explains the difference in the counts. The project mapping notes record that the 83 unmatched points were reviewed using a nearest-country check: 10 were closest to China and 3 were closest to Türkiye, matching the 13 IDs listed above. This is different from the direct point-in-country spatial join used for the primary mapping. The available files do not include the exact nearest-boundary distances or enough detail to justify adding those points to the main sample.

**Decision:** keep the 13 nearest-country candidates out of the primary sample. Do not use a 5 km fallback rule for the main mapping. The primary sample remains **1,441 China + 180 Türkiye = 1,621 urban units**. The count difference is now explained; whether the 13 labels are suitable for a separate sensitivity analysis can be considered later if needed.

## 3. Checks across the UHII data files

The final audit checked **5,372 CSV files** in `data/UHII_dataset`.

The checks found:

- No files with an unexpected row count; each file had 10,196 rows.
- No missing required columns.
- No empty or malformed files or rows.
- No file-reading errors.
- No blank or duplicate `UrbanId` values.
- No unknown or missing IDs when compared with the expected city list.
- No problems with the indicator, year, or period information in file names.
- No missing indicator-year-period groups based on the coverage rules used in the audit.

The audit used these expected annual ranges: Mod1 and Mod2 from 2001 to 2021; AMod2, SAT, SMod2, and SMyd1 within their checked 2001–2020 ranges; and Myd1 and Myd2 from 2003 to 2021. These ranges should be checked against the dataset documentation before publication.

## 4. Numeric values and missing data

The audit found no blank values in the intensity columns, unexpected text values, or infinite numeric values. All entries flagged by the first numeric check were `NA` values.

| Intensity column | Valid numeric values | `NA` values |
|---|---:|---:|
| `Intensity_EA` | 54,563,834 | 209,078 |
| `Intensity_IEA` | 54,560,493 | 212,419 |
| `Intensity_MEA` | 54,560,204 | 212,708 |
| `Intensity_DEA` | 54,557,592 | 215,320 |

The audit also checked missing values by country:

| Country | `NA` values / expected values | Missing rate | Files with at least one `NA` |
|---|---:|---:|---:|
| China | 38,650 / 30,964,208 | 0.1248% | 875 |
| Türkiye | 1,515 / 3,867,840 | 0.0392% | 12 |

In two files, all 180 Türkiye units have `NA` values for all four intensity methods: `Myd1_Nig_2018_5.csv` and `Myd2_Day_2013_6.csv`. These may be linked to gaps in the source data, but we have not confirmed the reason. The audit found no missing values for Türkiye in the annual files.

**Important:** We should not replace `NA` with zero. Once we choose the target variable, years, and features, we need to decide how to handle missing data and clearly report any rows we remove or values we impute.

## 5. Review of unusually high or low values

Negative UHII values can be valid, so we did not treat a value as an error only because it was negative.

We checked 2,006 monthly files for Mod1, Myd1, and Myd2 and looked for values below −40 or above +40. The check flagged 16 values and found no file-reading errors. Most of these values were outside the China–Türkiye sample used for this project.

One flagged value was within the main sample: China `UrbanId` 5560 in `Mod1_Day_2017_10.csv`, where `Intensity_DEA` is **41.82**. The values in nearby months and in the seasonal and annual records were much lower. This makes it an unusual monthly observation, but we have not shown that it is wrong. We should not delete or change it without further evidence. If we use monthly data, we can check whether the results change when this observation is included or excluded, and report that check.

## 6. What these checks mean for the study

The files passed the structural and numeric-format checks described above. This is a useful first step, but it does not prove that every value is scientifically accurate.

China has many more mapped urban units than Türkiye: **1,441 compared with 180**. This difference needs to be considered when we design and interpret the experiments, especially when training in Türkiye and testing in China. Repeated records for the same urban unit across months or years do not count as new independent cities.

Monthly, seasonal, and annual summaries may overlap. We must not treat them as independent observations if this would increase the apparent sample size or cause data leakage. Training and test sets should contain separate urban units. We should avoid a simple random row split if records from the same or nearby urban areas could appear in both sets.

The four columns `EA`, `IEA`, `MEA`, and `DEA` are different methods for calculating UHII; they do not represent different countries. Before modeling, we need to choose the target method or methods and explain why we selected them.

## 7. Open points and current decisions

This section separates decisions we can make now from questions that still need evidence or a final modeling plan.

### 7.1 Dataset source and version

**Status: The original Figshare source record and download path are documented; the exact snapshot of the local files is not independently verified.**

The user confirmed that the dataset files were downloaded by opening the official Figshare page below and clicking **Download all**. The original record currently displays **Version 3**, dated 5 January 2024, and lists Versions 1 and 2 in its history. This records the source path and the version displayed on the page at the time it was checked; it does not independently prove that the local extracted CSVs exactly match that archive snapshot.

The original downloaded archive and a checksum are not stored in the project folder, so we cannot compare the local extracted files byte-for-byte with the original archive. This is a traceability limitation, not evidence that the local files are wrong. No re-download is needed solely to resolve this documentation wording.

Do not confuse Version 3 of the original record with the separate dataset record titled *Global Urban Heat Island Intensity Dataset (Version 2)*. The latter is a different record that uses ESACCI land-cover data for urban-area delineation.

**Decision:** cite the original Figshare record and the related research paper. Describe the data as associated with the original Figshare record, whose page currently displays Version 3; do not state that the exact local files are definitively Version 3 unless the original archive, checksum, or equivalent version metadata can be verified.

References:
- Original dataset record (Version 3 currently displayed): https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset/24821538
- Separate updated dataset record (Version 2): https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset_Version2_/30102847
- Research paper: https://doi.org/10.1016/j.rse.2024.114343

### 7.2 Different country counts in the mapping files

**Status: The difference in counts is explained by an ID-level comparison. The method used to assign the 13 additional country labels is still unconfirmed.**

`CityInfo_with_Country.csv` gives 1,441 urban units in China and 180 in Türkiye. `China_Turkiye_city_mapping.csv` gives 1,451 in China and 183 in Türkiye. We compared the two files directly and found the exact 13 rows that explain the difference.

- **China labels in the second file:** `UrbanId` 3, 62, 617, 2133, 4785, 5253, 7288, 8344, 8486, and 9175.
- **Türkiye labels in the second file:** `UrbanId` 64, 601, and 4586.

All 13 IDs already exist in `CityInfo_with_Country.csv`, but their country labels are blank in that file. Their longitude, latitude, and area values match between the files. Therefore, the second file did not add new urban units to the underlying city list; it assigned country labels to 13 previously blank rows.

The comparison explains the count difference, but it does not prove that the 13 country assignments follow the correct geographic rule. The available files do not explain how these labels were assigned.

**Decision for now:** keep `CityInfo_with_Country.csv` as the primary mapping and keep these 13 rows outside the primary sample until the assignment method is documented and checked. Do not apply the 5 km fallback rule. The primary sample remains **1,441 China and 180 Türkiye urban units**. The file `Country_Mapping_13_Row_Comparison.csv` records the row-level comparison.

### 7.3 Blank country labels and boundary candidates

**Status: The rule for the primary sample is set.**

We will not force a country label onto every urban unit. The 83 rows with blank country labels in `CityInfo_with_Country.csv` stay outside the primary China–Türkiye comparison unless the assignment can be supported by a clear rule and checked coordinates. The 13 IDs listed in Section 7.2 are part of these 83 blank-labelled rows, not 13 new units beyond them.

The project mapping notes indicate that these 13 records received labels from a nearest-country check after they were not assigned by the direct spatial join. The 83 blank rows include these 13 candidates; they are not 13 extra records on top of the 83. The remaining unmatched rows were associated with other nearest countries.

This does not mean the records are bad. It means a nearest-country label alone is not enough for the primary country sample. We will use the direct spatial-join sample for the main analysis and will not force labels onto the 83 unmatched records.

### 7.4 Reasons for missing values (`NA`)

**Status: The reason is not stated in the available dataset README; a safe handling rule is now defined.**

We checked the supplied `Readme.docx` and the public dataset description. They explain the UHII methods and file structure, but they do not identify the specific reason for the `NA` values in our local CSV files. We therefore cannot say that these values were caused by clouds, sensor gaps, or any other particular issue without further evidence from the data authors.

The audit found:
- China: 38,650 `NA` values out of 30,964,208 checked cells (0.1248%).
- Türkiye: 1,515 `NA` values out of 3,867,840 checked cells (0.0392%).
- Two monthly files have `NA` values for all 180 Türkiye units across all four UHII methods: `Myd1_Nig_2018_5.csv` and `Myd2_Day_2013_6.csv`.
- The audit found no Türkiye `NA` values in the annual files.

**Rules we can apply now:**
1. Never replace `NA` with zero.
2. For a specific modelling experiment, do not use a row as a labelled training or test example when its selected UHII target is missing. Record how many examples are excluded.
3. Do not choose a final rule for missing predictor values until the common predictor list is agreed. At that point, decide whether to remove rows or use imputation, and document the reason.
4. If imputation is used, fit it on the training data only. Do not use the held-out test data to calculate imputation values.
5. Report missingness again for the final selected indicators, years, countries, and predictors, because the overall audit counts may not represent the final modelling sample.

This resolves the handling principle, but it does not reveal the original cause of the missing values. If the data documentation does not explain the cause, we should report it as unknown rather than make a guess.

### 7.5 Final modeling choices

**Status: Still open; this belongs in the modeling protocol, not in the data-quality audit alone.**

Before training models, we still need to choose and document:
- the main UHII target method (EA, IEA, MEA, or DEA);
- the temperature indicator and time scale (for example, annual or monthly) and the years to include;
- predictor variables and their verified data sources, versions, periods, and spatial resolution;
- rules for missing target and predictor values;
- a validation design that keeps the same urban units out of both training and test data;
- the exact adaptation experiment, including how target-country training samples will be selected.

We should not guess these choices just to make this audit file look finished. Tao's feature research can help us confirm which predictors are available and comparable in both countries. Then we can write a separate, final modeling protocol before running the experiments.

For the two transfer directions, China-to-Türkiye can be the main experiment because the current mapped sample is larger in China. Türkiye-to-China can be retained as a secondary exploratory experiment. The unequal sample sizes should be reported and considered when interpreting the results.

## 8. Current status: what is done and what remains

### Completed or sufficiently documented for now

1. **Dataset source:** the user confirmed downloading the files with **Download all** from the original Figshare record, whose page currently displays Version 3. The source record and download path are documented, but the exact archive snapshot of the local CSVs is not independently verified because the original archive/checksum is not stored locally. This is a traceability limitation, not evidence that the data are wrong; no re-download is needed solely for this documentation point.
2. **Country-count difference:** an ID-level comparison found the 13 rows that explain the count difference. These are 10 nearest-country candidates labelled China and 3 labelled Türkiye that were blank in the direct spatial-join map. The primary sample remains unchanged.
3. **Unmatched country labels:** the main sample rule is set. Use the direct spatial join, with 1,441 China and 180 Türkiye urban units. Keep all 83 blank-labelled units outside the main comparison; the 13 nearest-country candidates are part of those 83, not an additional group.
4. **Missing UHII values:** the overall audit is complete and the handling principles are set. Do not replace `NA` with zero. Exclude an example when the selected target is missing, record the exclusion count, and decide how to handle missing predictor values only after the shared predictor list is agreed. If imputation is used, fit it on the training data only.
5. **Structural file audit:** the audit checked 5,372 UHII CSV files and found no structural, ID, filename/combination, or non-`NA` numeric-format problems under the checks performed. This does not prove every measurement is scientifically correct.

### Not solvable from the current local files alone

- **Exact cause of `NA` values:** the available README does not explain why the specific cells are missing. The research paper notes that missing observations can affect clear-sky land-surface temperature data in general, but that does not establish the cause of these particular `NA` values. Unless the data authors or additional source metadata provide a specific explanation, report the cause as unknown.
- **Exact archive checksum:** the source page and download action are recorded, but the original downloaded archive or checksum is not available locally. We do not need to download the 1.34 GB file again just for this project note.

### Waiting for Tao's research

The following decisions depend on the common predictors and the research protocol, so we should not guess them now:

- the main UHII target method (`EA`, `IEA`, `MEA`, or `DEA`);
- indicator, time scale, and years;
- predictor list and confirmed data sources;
- final missing-predictor strategy and the exact sample after filtering;
- leakage-safe validation design;
- precise adaptation experiment.

Once Tao's document arrives, we can agree on the shared feature set and then write a short modeling protocol. A reasonable working plan is to make China-to-Türkiye the primary transfer experiment and Türkiye-to-China a secondary exploratory experiment, but the final setup must follow the verified data availability and validation design.

### Next steps

1. Keep this file and `Country_Mapping_13_Row_Comparison.csv` in the project folder as the current audit record.
2. Do not change the main country sample or impute any UHII values before the modeling target is chosen.
3. When Tao's plan arrives, finalize the model target/features/time range and run a new missing-value summary for only the selected records.
4. If monthly data are used, include a sensitivity check for the unusual China observation `UrbanId` 5560 (`Mod1_Day_2017_10.csv`, `Intensity_DEA = 41.82`) rather than deleting it without evidence.

In the public README or final paper, summarize the relevant checks and decisions rather than copying every technical detail. Record future changes to country mapping, sample selection, missing-data treatment, or model design and explain the reason for each change.
