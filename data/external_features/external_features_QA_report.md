# External Features QA Report

- Run ID: `20261019_142159`
- Source cities: 1,621
- Expected city-year rows: 32,420
- Actual rows: 32,420
- Duplicate UrbanId-year keys: 0
- DEM missing cities: 0
- ERA5 target-year rows missing temperature: 0
- NDVI rows missing a reliable JJA mean: 14,183

## Feature coverage by country

| Country   | feature            |   n_rows |   n_missing |   missing_pct |   n_cities_with_any_value |
|:----------|:-------------------|---------:|------------:|--------------:|--------------------------:|
| China     | elevation_m        |    28820 |           0 |       0       |                      1441 |
| China     | era5_t2m_jja       |    28820 |           0 |       0       |                      1441 |
| China     | era5_precip_jja_mm |    28820 |           0 |       0       |                      1441 |
| China     | era5_wind_jja      |    28820 |           0 |       0       |                      1441 |
| China     | era5_dewpoint_jja  |    28820 |           0 |       0       |                      1441 |
| China     | era5_rh_jja        |    28820 |           0 |       0       |                      1441 |
| China     | ndvi_jja_mean      |    28820 |       13928 |      48.3276  |                      1313 |
| Türkiye   | elevation_m        |     3600 |           0 |       0       |                       180 |
| Türkiye   | era5_t2m_jja       |     3600 |           0 |       0       |                       180 |
| Türkiye   | era5_precip_jja_mm |     3600 |           0 |       0       |                       180 |
| Türkiye   | era5_wind_jja      |     3600 |           0 |       0       |                       180 |
| Türkiye   | era5_dewpoint_jja  |     3600 |           0 |       0       |                       180 |
| Türkiye   | era5_rh_jja        |     3600 |           0 |       0       |                       180 |
| Türkiye   | ndvi_jja_mean      |     3600 |         255 |       7.08333 |                       177 |

## Interpretation

- Missing values are not imputed in this extraction notebook. Model-specific imputation, if scientifically appropriate, is fit only inside the training pipeline.
- Open-Meteo elevation provenance is labelled as Copernicus DEM GLO-90; it is not labelled SRTM.
- ERA5 precipitation is output in mm over JJA using the monthly-averaged daily-means product semantics documented by ECMWF. If the NetCDF units attribute reports only m, the conversion is allowed only after the exact CDS request fingerprint and NetCDF SHA-256 sidecar validate; otherwise the pipeline stops.
- MOD13Q1 NDVI values in the imported AppEEARS CSV are already scaled; no additional 0.0001 scaling is applied. The QA policy is intentionally strict and should be documented in the study methods.
- NDVI is sampled at the mapped point coordinate; it is not a polygon-weighted mean over the urban area.
- ERA5 values use the nearest grid point. The wind feature is the magnitude of monthly-mean 10 m u/v vectors, not the mean scalar wind speed.
- Copernicus DEM GLO-90 data access requires attribution to Copernicus and Open-Meteo.
- This notebook only creates features and QA reports; it does not make a GO decision for the transfer study.