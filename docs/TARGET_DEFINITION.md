# TARGET_DEFINITION.md
## Task2: Final Primary Target Definition for China-Türkiye Urban Heat Transfer Project

### Selected Primary Target
Nighttime JJA Surface Urban Heat Island Intensity (SUHII), calculated by MEA method (Intensity_MEA)

1. Dataset / Source record
Global Urban Heat Island Intensity Dataset, Figshare, DOI: 10.6084/m9.figshare.24821538

2. Exact temperature product family
Mod2 (MOD11A2 clear-sky LST product)

3. Nighttime / Daytime selection
Nighttime (Nig)

4. Target column & method
Column: `Intensity_MEA` (Modified Exact Area method).
Primary target uses only MEA. DEA will be reserved for separate sensitivity analysis, not mixed within main target.

5. Season / Period code & unit
Period code (month field) = 22, JJA (June–July–August warm season).
Unit: °C (degrees Celsius).

6. Filename pattern & value interpretation
Filename pattern: `Mod2_Nig_{year}_22.csv`
- Positive value: Urban surface LST warmer than rural BRA reference
- Negative value: Urban surface LST cooler than rural BRA reference

### Rationale for selecting MEA as primary target
MEA (Modified Exact Area) removes water, topographic relief and high nighttime light disturbance within background reference zones. It is one of four standardized area-based metrics published by the dataset authors and consistently computed for all cities across China and Türkiye.
DEA will be used only for sensitivity test in later analysis and will not be mixed into the main modelling target.

### Rule compliance
No mixing of different methods or product families in the primary target table.
