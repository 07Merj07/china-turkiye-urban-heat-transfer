# Can Urban Heat Models Cross Borders?
## Quantifying the Transferability of Urban Heat Models Between China and Türkiye

### Project aim

This project will study whether a model trained using urban data from one country can predict urban heat island intensity (UHII) in another country. The planned comparison includes China-to-Türkiye transfer and Türkiye-to-China transfer. A possible target-country adaptation experiment will be considered after the shared features and validation plan are agreed.

### Dataset

The project uses the *Global Urban Heat Island Intensity Dataset* from the original Figshare record:

- Dataset: https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset/24821538
- DOI: https://doi.org/10.6084/m9.figshare.24821538
- Related paper: https://doi.org/10.1016/j.rse.2024.114343

The full UHII dataset is large, so it is not included in this GitHub repository. Download it from the official source and place the extracted CSV files in `data/UHII_dataset/` when running the audit script.

### Current data checks

A structural audit was run on 5,372 UHII CSV files. Under the checks described in the audit notes, no structural, ID, expected-coverage, or unexpected non-`NA` numeric-format problems were found. This does not prove that every measurement is scientifically correct.

The current primary country sample uses direct spatial joins to country boundaries:

- China: 1,441 urban units
- Türkiye: 180 urban units
- Total: 1,621 urban units

The 83 urban units with blank country labels remain outside the primary comparison. This includes 13 units that received China or Türkiye labels in a separate nearest-country file. They are not added to the primary sample because their assignment method has not been fully confirmed.

### Research status

The project is still in the research-design stage. The final UHII target method, indicator, year range, shared predictor set, validation design, and adaptation method have not yet been fixed. These decisions will be made after the cross-country feature review is complete. No model-performance results are reported in this repository at this stage.

### Repository guide

- `docs/DATASET_PROVENANCE.md` — source and download record.
- `docs/DATA_QUALITY_AUDIT_NOTES.md` — data audit findings and current decisions.
- `data/CityInfo.csv` — urban-unit reference table from the source dataset.
- `data/CityInfo_with_Country.csv` — current primary country mapping.
- `data/audit_reports/Country_Mapping_13_Row_Comparison.csv` — row-level comparison of the 13 disputed country labels.
- `scripts/UHII_Final_Audit.ps1` — script used to check the local dataset files.

### Reproducibility note

The audit script expects `data/CityInfo.csv`, `data/CityInfo_with_Country.csv`, and the extracted `data/UHII_dataset/` folder. The full dataset is not committed to GitHub; users must obtain it from the official Figshare page before running the full audit.

See the data quality audit notes for details about missing values, the country mapping, coverage checks, and current limitations.
