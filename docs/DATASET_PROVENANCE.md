# Dataset Provenance and Version Record

## Dataset used in this project

**Dataset title:** Global Urban Heat Island Intensity Dataset  
**Publisher/repository:** Figshare  
**Main record:** https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset/24821538  
**Dataset DOI:** https://doi.org/10.6084/m9.figshare.24821538  
**Associated paper:** Yang, Q., Xu, Y., Chakraborty, T. C., et al. (2024). *A global urban heat island intensity dataset: Generation, comparison, and analysis*. *Remote Sensing of Environment*, 312, 114343. https://doi.org/10.1016/j.rse.2024.114343

## Version wording — important

The official Figshare page for the main record currently displays **Version 3** and lists Version 1 and Version 2 in that record's version history. The same page identifies the record as posted on 5 January 2024.

The publisher also links to a **separate updated dataset record** described as “Global Urban Heat Island Intensity Dataset (Version2)”: https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset_Version2_/30102847. The publisher's description of that separate updated dataset says that the base map used to delineate urban areas was changed from MODIS land cover to ESACCI land cover; spatial extents for urban and rural/background-reference areas and average urban temperature were also added.

These are two different versioning contexts:

1. **Version 3** is the current version shown in the history of the original Figshare record (`24821538`).
2. **Version 2** is the name used for the separate updated dataset record (`30102847`). It must not be confused with Version 2 in the original record's history.

## What we can and cannot confirm about the local files

The local project directory was checked for the original ZIP/archive and source/metadata/README files. Based on the directory listings provided on 10 October 2026, no such archive or metadata file was found in the project root, `data`, `src`, or `data/UHII_dataset`; the UHII dataset folder contains the CSV files.

The project's local UHII files have been technically audited: 5,372 CSV files were scanned; the audit reported no structural, ID, coverage, or non-`NA` numeric anomalies under its configured checks.

**The exact downloaded archive snapshot for the local files is not independently verified.** The fact that the current original Figshare record displays Version 3 does not establish that the local files were downloaded from that exact snapshot. Therefore, do not label the local files “Version 1” or definitively claim they are Version 3 unless an original download link, archive, checksum, README, or metadata record is later found.

Use this cautious wording in project notes:

> We use the Global Urban Heat Island Intensity Dataset associated with the original Figshare record (DOI: 10.6084/m9.figshare.24821538). The record currently displays Version 3. The exact version of the local downloaded files could not be independently confirmed from the files and metadata currently available in the project directory.

## Project decision

The project will continue with the already audited local dataset for now. No source data are modified by this provenance note. The separate updated dataset record will not be mixed into the current analysis unless the project explicitly decides to switch datasets later.

## Audit outputs

The existing technical audit reports are stored locally in `data/audit_reports/`. These reports describe the local files that were audited; they do not independently establish which Figshare archive revision those files came from.

## Official references

- Original Figshare record and version history: https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset/24821538
- Separate updated dataset record: https://figshare.com/articles/dataset/Global_Urban_Heat_Island_Intensity_Dataset_Version2_/30102847
- Associated 2024 paper: https://doi.org/10.1016/j.rse.2024.114343

**Last checked:** 10 October 2026.
