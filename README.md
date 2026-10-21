# Urban Heat Transfer Between China and Türkiye

**A reproducible research pipeline for cross-country transfer learning of Surface Urban Heat Island Intensity (SUHII).**

The project studies whether urban-heat patterns learned from Chinese cities can transfer to Turkish cities, and vice versa. The active Phase 2 workflow prepares the target, audits city-year records, creates external climate/environmental features, and compares baseline and enhanced transfer models.

## Research target

- **Primary label:** `Intensity_MEA` — Modified Equal-Area SUHII, in °C.
- **Product:** `Mod2` (MOD11A2 clear-sky land-surface temperature family), nighttime (`Nig`).
- **Season:** period `22`, June–August (JJA).
- **Years:** 2001–2020.
- **Exact source-file pattern:** `Mod2_Nig_YYYY_PERIOD.csv`, with periods 6, 7, 8 and 22 for each year — 80 required files.

`AMod2` and `SMod2` are distinct product families. They are not renamed or substituted for `Mod2`.

## Repository layout

```text
urban-heat-transfer/
├── data/
│   ├── raw/UHII_dataset/       # local-only; 80 source CSVs, ignored by Git
│   ├── sample_uhi/UHII_dataset/ # 5 labelled source samples for inspection
│   ├── reference/CityInfo.csv
│   ├── external_features/China_Turkiye_city_mapping.csv
│   ├── processed/CityInfo_with_Country.csv
│   └── audit_reports/           # current merge audit + labelled historical summaries
├── notebooks/
│   ├── 01_Phase2_Core_Final.ipynb
│   ├── 02_External_Features_Final.ipynb
│   └── 03_Transfer_Experiments_Final.ipynb
├── src/urban_heat_transfer/     # tested mapping/merge helpers
├── scripts/                     # source-copy, data audit, and post-run validator
├── outputs/phase2_outputs/      # generated locally; ignored by Git
└── docs/                        # protocol, provenance, decisions, QA, and run guide
```

## Quick start

### 1. Install Python packages

```bash
python -m pip install -r requirements.txt
```

### 2. Copy the required source files (Windows)

The full source archive is intentionally not committed to GitHub. In PowerShell, run from the repository root:

```powershell
.\scripts\copy_required_uhi_files.ps1 -Source "C:\path\to\existing\urban-heat-transfer\data\UHII_dataset"
```

Replace the example path with the existing folder on your computer. The script prechecks all 80 filenames and existing-file hash conflicts before copying. It never moves, renames, or deletes source files.

Then audit the copied files:

```bash
python scripts/audit_uhi_sources.py
```

A full ready-to-run source inventory should report all **80/80** exact `Mod2_Nig` filenames, readable CSVs, the required columns, and no duplicate `UrbanId` values. The five files under `data/sample_uhi/` are examples only; they cannot replace all 80 source inputs.

### 3. Rebuild and test city-country mapping

```bash
python scripts/build_city_mapping.py
python scripts/check_extreme_values.py  # review flags only; does not modify source data
python -m unittest discover -s tests -v
```

The merge assigns country only through the explicit `UrbanId` mapping. Unmapped global city records remain unassigned; the code does not guess a country from the nearest city.

### 4. Run the notebooks in Google Colab

Place the entire `urban-heat-transfer` folder inside Google Drive's `MyDrive`, then open and run the notebooks in order:

1. `notebooks/01_Phase2_Core_Final.ipynb`
2. `notebooks/02_External_Features_Final.ipynb`
3. `notebooks/03_Transfer_Experiments_Final.ipynb`

In the first notebook cells, verify the printed project/data/output paths before continuing. The external-feature notebook requires credentials stored in Colab Secrets; see [`docs/LOCAL_RUN_GUIDE_TR.md`](docs/LOCAL_RUN_GUIDE_TR.md).

After all three notebooks finish in Google Colab, run:

```python
!python /content/drive/MyDrive/urban-heat-transfer/scripts/phase2_validate_outputs.py --project-dir /content/drive/MyDrive/urban-heat-transfer
```

For a local run from the repository root, the equivalent command is `python scripts/phase2_validate_outputs.py --project-dir .`.

The project is structurally ready for a full run, but **the entire 2001–2020 pipeline has not yet been completed on the full source archive**. The validator must return `GO` on the real project outputs and all warnings must be reviewed before reporting final research results.

## What is and is not a final result

- Historical source-audit summaries are explicitly stored under `data/audit_reports/historical_*` and are not current model outputs.
- Previous `task7_transfer_results*.csv` tables are preserved separately outside the public repository package; do not cite them as final performance results just because the files exist.
- The precomputed period-22 JJA product is the primary label. The monthly mean of June/July/August is a diagnostic; discrepancies are surfaced for review, not automatically deleted.
- External features are point/grid-cell samples around city coordinates, not polygon-weighted citywide means. The methodological limitations are documented in `docs/RESEARCH_PROTOCOL.md` and the notebook audit notes.

## Data citation and license

Primary data: [Global Urban Heat Island Intensity Dataset, Figshare, DOI 10.6084/m9.figshare.24821538](https://doi.org/10.6084/m9.figshare.24821538). Follow the dataset provider's terms. A project-code license has intentionally not been chosen until all contributors agree; see [`docs/LICENSE_AND_CITATION.md`](docs/LICENSE_AND_CITATION.md).
