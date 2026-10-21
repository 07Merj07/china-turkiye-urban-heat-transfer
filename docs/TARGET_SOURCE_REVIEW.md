# TARGET_SOURCE_REVIEW.md
## Task1: Source Dataset Documentation Review
Source: Global UHII Figshare Dataset, DOI:10.6084/m9.figshare.24821538
> All definitions verified from official README documentation (not inferred purely from filenames).

### 1. Product prefix definitions
- Mod1: MOD11A1 clear-sky LST
- Mod2: MOD11A2 clear-sky LST
- Myd1: MYD11A1 clear-sky LST
- Myd2: MYD11A2 clear-sky LST
- SMod2: Seamless MOD11A2 clear-sky LST
- SMyd1: Seamless MYD11A1 clear-sky LST
- AMod2: All-sky MOD11A2 LST
- SAT: Surface air temperature (canopy UHI)

### 2. Diurnal definition (Day / Nig)
- Day: Daytime overpass UHII
- Nig: Nighttime overpass UHII

### 3. Four UHII method definitions
- **EA (Equal-Area)**: Create buffer equal to urban area size; exclude water and topography to get BRA.
- **IEA (Improved Equal-Area)**: Based on EA BRA; further remove pixels with >5% impervious surface from other urban influence.
- **MEA (Modified Equal-Area)**: Double-size buffer; remove high NLI pixels above urban median to reduce anthropogenic disturbance, also remove water and topography.
- **DEA (Dynamic Equal-Area)**: Iterative dynamic cyclic method to remove water, topography and human disturbance; ensures BRA pixel count matches urban area size.

### 4. Period / Month code verification
Month = 22 corresponds to **June–August (JJA)** quarterly composite.
- 1–12: monthly
- 21: MAM (Mar-May)
- 22: JJA (Jun-Aug)
- 23: SON (Sep-Nov)
- 24: DJF (Dec-Feb)
- 30: annual average

### 5. Target metadata & interpretation
- Unit: °C (degrees Celsius, UHII surface temperature difference)
- Positive UHII: Urban surface LST > rural background reference temperature
- Negative UHII: Urban surface LST < rural background reference temperature
- Temporal coverage:
  - Mod2: 2001–2021
  - AMod2/SMod2:2001–2020
- Key limitations for China–Türkiye cross-country comparison:
    1. BRA (background reference area) masks are static for each city.
    2. Consistent method pipeline applied globally across all cities, supporting cross-nation comparison.
    3. Raw LST pixel data are not distributed; only final derived UHII table is provided.
    4. All four metrics (EA/IEA/MEA/DEA) are precomputed and stored in each CSV.

### 6. Verification summary
All definitions are confirmed by reading the source README file, rather than guessing from CSV filenames alone.
