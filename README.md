# Urban Heat Transfer Between China and Türkiye

*A research project on cross-country transfer learning for Surface Urban Heat Island Intensity (SUHII).*

- **Research team:** Tao Jingchu (陶静初), China · Mert Can Yalçın, Türkiye
- **Study period:** 2001–2020
- **Primary task:** Compare urban-heat prediction when a model trained on one country is applied to the other, and evaluate whether additional environmental features help.

## Project Overview

Climate, geography, vegetation, and human activity differ between cities. These differences may affect how well a model trained in one country works in another. This project studies transfer in both directions—China to Türkiye and Türkiye to China—using city-year records of nighttime Surface Urban Heat Island Intensity (SUHII).

The repository brings together target-data checks, city-country mapping, external-feature preparation, transfer experiments, tests, and post-run validation. The workflow is organized to make its main data choices and checks reviewable and repeatable.

## Research Questions

1. How well does a model transfer from China to Türkiye, and from Türkiye to China?
2. Do climate and environmental features improve cross-country prediction compared with a baseline feature set?
3. How does performance change when only part of the target-country adaptation data is available?
4. How do feature coverage, city mapping, and data-quality checks affect the analysis?

## Research Target

| Item | Definition |
|---|---|
| Target column | `Intensity_MEA` |
| Method | Modified Equal-Area (MEA) |
| Measure | Surface Urban Heat Island Intensity (SUHII) |
| Unit | Degrees Celsius (°C) |
| Product family | `Mod2` — MOD11A2 clear-sky land-surface temperature |
| Time of day | Nighttime (`Nig`) |
| Primary season | Period `22`, June–August (JJA) |
| Study years | 2001–2020 |

### Required source files

The primary source inventory uses filenames matching:

```text
Mod2_Nig_YYYY_PERIOD.csv
```

For every year from 2001 through 2020, the required periods are `6`, `7`, `8`, and `22`, giving **80 files**. Period `22` is the primary JJA target. Periods `6`, `7`, and `8` support monthly-to-seasonal diagnostic checks.

`AMod2` and `SMod2` are different product families and must not be renamed or substituted for `Mod2`. Other source files in the broader archive are not part of this exact 80-file inventory.

The precomputed period-22 value remains the primary seasonal target. The simple mean of June, July, and August is used as a diagnostic comparison, not as a replacement target. Differences are recorded for review rather than automatically deleted.

## Data and Features

The workflow uses:

- **SUHII target data:** the required `Mod2_Nig` source files.
- **City information:** `CityInfo.csv` and related reference files.
- **Country mapping:** explicit `UrbanId` mapping for China and Türkiye.
- **External features:** elevation, ERA5-Land climate variables, and MODIS NDVI.
- **Quality records:** source inventory, mapping audits, feature-coverage reports, and post-run validation outputs.

External feature values are sampled at or near city coordinates using points or grid cells. They are **not polygon-weighted citywide averages**, so they may not represent every part of a city's urban area.

Country labels are assigned through the explicit `UrbanId` mapping. Records without a valid mapping remain unassigned; the workflow does not guess a country based on the nearest city.

## Analysis Workflow

Run the three primary Phase 2 notebooks in this order:

1. **`notebooks/01_Phase2_Core_Final.ipynb`** — prepares and audits the target, reviews city-year records, creates the city manifest, and runs baseline transfer experiments.
2. **`notebooks/02_External_Features_Final.ipynb`** — prepares elevation, ERA5-Land, and NDVI features and records their data provenance and coverage.
3. **`notebooks/03_Transfer_Experiments_Final.ipynb`** — compares baseline and enhanced models using matched samples, both transfer directions, and target-country adaptation settings.

The experiments include Ridge and Random Forest models, with a source-mean baseline. They use fixed target-country test cities within each comparison setting; few-shot adaptation samples are drawn from the adaptation pool rather than the locked test cities. The notebooks report metrics such as R², RMSE, and MAE.

Two additional notebooks are included for supplementary work:

- `notebooks/04_Urban_Feature_Expansion.ipynb`
- `notebooks/05_Final_Results_and_Visualization.ipynb`

For the primary Phase 2 workflow, use notebooks 01–03 and the corresponding generated output tables and audit reports. Treat supplementary notebook outputs separately unless they have been matched to the same data, experiment settings, and current output files.

## Repository Structure

```text
urban-heat-transfer/
├── data/
│   ├── UHII_dataset/                    # Broader source archive included in this repository
│   ├── raw/UHII_dataset/                 # Active input folder for the 80 required files
│   ├── sample_uhi/UHII_dataset/          # Five labelled samples for inspection
│   ├── reference/                        # City reference data
│   ├── external_features/                # Country mapping and feature provenance records
│   ├── processed/                        # Processed city-country mapping
│   └── audit_reports/                    # Current and historical data-quality reports
├── notebooks/                            # Five analysis notebooks
├── src/urban_heat_transfer/               # Mapping and merge helper code
├── scripts/                              # Source-copy, audit, syntax-check, and validation tools
├── tests/                                # Unit tests
├── reports/figures/                      # Saved figures
├── outputs/phase2_outputs/                # Generated Phase 2 outputs; output files are Git-ignored
├── docs/                                 # Research protocol, provenance, QA, and run guide
├── requirements.txt
└── README.md
```

## Quick Start

### 1. Install Python packages

Use Python 3.10 or newer. From the repository root, run:

```bash
python -m pip install -r requirements.txt
```

### 2. Prepare the required source files (Windows)

The active Phase 2 notebooks use `data/raw/UHII_dataset/`. The repository also includes the broader source archive under `data/UHII_dataset/`. To copy only the required 80 files into the active input folder, open PowerShell at the repository root and run:

```powershell
.\scripts\copy_required_uhi_files.ps1 -Source ".\data\UHII_dataset"
```

If the source archive is not present on your computer, replace the example with the path to your local `UHII_dataset` folder:

```powershell
.\scripts\copy_required_uhi_files.ps1 -Source "C:\path\to\existing\UHII_dataset"
```

The script checks all expected filenames and detects same-name files with different contents before copying. It does not move, rename, or delete the source files.

Audit the active input folder:

```bash
python scripts/audit_uhi_sources.py
```

The complete inventory should contain **80/80** required filenames. The audit checks file readability, the required `UrbanId` and `Intensity_MEA` columns, and basic data-integrity conditions. The five sample files under `data/sample_uhi/UHII_dataset/` are for inspection and do not replace the 80-file inventory.

### 3. Run mapping and code checks

From the repository root:

```bash
python scripts/build_city_mapping.py
python scripts/check_extreme_values.py
python -m unittest discover -s tests -v
python scripts/check_notebook_syntax.py
```

The mapping uses explicit IDs. The extreme-value script flags values for human review; it does not automatically remove or change target values. Review the generated reports rather than relying on a successful command alone.

### 4. Run the primary notebooks in Google Colab

1. Put the complete `urban-heat-transfer` folder in Google Drive.
2. Open notebooks 01, 02, and 03 in the order shown above.
3. Check the project, input, and output paths printed near the start of the notebooks.
4. Make sure the 80 required source files are available in `data/raw/UHII_dataset/` before running notebook 01.

Notebook 02 uses Google Colab Secrets for external-data access. The expected secret names are:

- `NASA_EARTHDATA_USERNAME`
- `NASA_EARTHDATA_PASSWORD`
- `CDS_API_KEY`

Do not put passwords, access keys, or tokens into notebook cells or commit them to GitHub. See [`docs/LOCAL_RUN_GUIDE_TR.md`](docs/LOCAL_RUN_GUIDE_TR.md) for the run instructions.

### 5. Validate generated outputs

After the three primary notebooks finish, run the validator from a Colab code cell. If the project folder is directly under `MyDrive`, use:

```python
!python /content/drive/MyDrive/urban-heat-transfer/scripts/phase2_validate_outputs.py --project-dir /content/drive/MyDrive/urban-heat-transfer
```

If the folder is nested in Drive, replace both paths with the actual project path. For a local run from the repository root, use:

```bash
python scripts/phase2_validate_outputs.py --project-dir .
```

The validator writes a CSV report under the Phase 2 output audit folder and a Markdown report at `docs/PHASE2_FINAL_AUDIT.md`. Review the report and all warnings before using the outputs in a paper, application, or presentation. A unit test, existing notebook output, or successful file upload is not a substitute for checking the current analysis outputs.

## Methodological Notes

- **Duplicate records:** ambiguous `UrbanId` or city-year records are flagged or quarantined instead of silently selecting the first row.
- **Target leakage:** `UrbanId` and country labels are used for mapping and data splitting, not as model predictors. Target-derived monthly values are not intended as model inputs.
- **Matched comparisons:** baseline and enhanced models should be compared on the same pool, test cities, and experiment settings.
- **Point-sampled features:** external features are not polygon-weighted citywide means.
- **Model evaluation:** interpret R² alongside RMSE and MAE and identify the transfer direction, feature set, data pool, and adaptation setting for each reported metric.

See [`docs/RESEARCH_PROTOCOL.md`](docs/RESEARCH_PROTOCOL.md), [`docs/DATASET_PROVENANCE.md`](docs/DATASET_PROVENANCE.md), and [`docs/PHASE2_LOCAL_TEST_RESULTS.md`](docs/PHASE2_LOCAL_TEST_RESULTS.md) for further details on design choices, data sources, and documented checks.

## Data Citation and License

The primary target dataset is the **Global Urban Heat Island Intensity Dataset** by Qiquan Yang (2024):

- Dataset record: [Figshare, DOI 10.6084/m9.figshare.24821538](https://doi.org/10.6084/m9.figshare.24821538)
- Related paper: [Yang et al. (2024), *Remote Sensing of Environment*, 312, 114343](https://doi.org/10.1016/j.rse.2024.114343)
- Dataset license: **CC BY 4.0**. Retain attribution and follow the dataset's license terms when reusing or redistributing the data.

No project-code license has been chosen in this repository. The contributors should agree on a code license before adding a `LICENSE` file. See [`docs/LICENSE_AND_CITATION.md`](docs/LICENSE_AND_CITATION.md).

## Authors

**Tao Jingchu (陶静初)** — China  
**Mert Can Yalçın** — Türkiye

This project brings together contributors in China and Türkiye to study whether urban-heat prediction models transfer across different national and environmental settings.
