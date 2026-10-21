#!/usr/bin/env python3
"""Post-run structural/scientific QA for the Phase 2 Urban Heat Transfer project.

This tool checks saved artefacts, row keys, country/year scope, joins, split isolation,
paired model comparison and provenance sidecars. It cannot independently authenticate
remote-source science or replace manual interpretation of the source dataset.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from datetime import datetime
import numpy as np
import pandas as pd

YEARS=set(range(2001,2021))
COUNTRIES={'China','Türkiye'}
DISPUTED={3,62,64,601,617,2133,4586,4785,5253,7288,8344,8486,9175}
FORBIDDEN={'UrbanId','Country','Intensity_MEA','Intensity_MEA_jun','Intensity_MEA_jul','Intensity_MEA_aug',
           'Jun_MEA','Jul_MEA','Aug_MEA','season_MEA_period22','monthly_mean_MEA'}

class Audit:
    def __init__(self, root: Path):
        self.root=root
        # GitHub repository layout first; legacy tao_documents layout remains supported.
        if (root/'data').is_dir() and (root/'outputs').is_dir():
            self.phase=root/'outputs'/'phase2_outputs'
            self.ext=root/'data'/'external_features'
        else:
            self.phase=root/'phase2_outputs'
            self.ext=root/'external_features'
        self.docs=root/'docs'
        self.rows=[]
    def check(self,name,ok,detail='',severity='FAIL'):
        self.rows.append({'check':name,'status':'PASS' if bool(ok) else severity,'detail':str(detail)})
    def read(self, folder, name, required=True):
        p=folder/name
        if not p.exists():
            self.check(f'file_exists:{p.relative_to(self.root)}',not required,'missing' if required else 'optional artifact absent', 'FAIL' if required else 'WARN')
            return None
        try:
            return pd.read_csv(p)
        except Exception as e:
            self.check(f'csv_readable:{p.relative_to(self.root)}',False,repr(e))
            return None
    def run(self):
        p=self.phase; e=self.ext
        required_core=[
            'analysis_city_manifest.csv','disputed_urbanid_review.csv','phase2_primary_target_raw.csv',
            'phase2_cleaned_target.csv','task3_composite_validation.csv','task3_composite_validation_summary.csv',
            'task3_composite_high_residual_review.csv','task3_composite_review_decisions.csv',
            'task4_year_country_coverage.csv','task4_missing_city_years.csv','task5_cleaning_log.csv',
            'task5_target_validation.csv','task5_country_year_summary.csv','task5_coverage_reconciliation.csv',
            'task6_feature_matrix.csv','task6_leakage_audit.csv','task7_transfer_results.csv','task7_split_manifest.csv']
        for f in required_core: self.check(f'core_file:{f}',(p/f).exists(),'required for full Phase 2')
        inventory=self.read(p,'phase2_file_inventory.csv')
        if inventory is not None and {'status','filename','period','year'}.issubset(inventory.columns):
            missing_inputs=inventory[inventory.status.astype(str).eq('MISSING_EXPECTED_FILE')]
            self.check('all expected monthly and JJA source files present',missing_inputs.empty,
                       f'missing_count={len(missing_inputs)}; examples={missing_inputs.filename.head(8).tolist()}')
            selected=inventory[inventory.get('selected',pd.Series(False,index=inventory.index)).fillna(False).astype(bool)]
            self.check('source inventory exact filename scope',selected.filename.astype(str).str.match(r'^Mod2_Nig_\d{4}_(6|7|8|22)\.csv$').all(),
                       f'selected_rows={len(selected)}')
        else:
            self.check('source file inventory schema',False,'phase2_file_inventory.csv missing or required columns unavailable')
        manifest=self.read(p,'analysis_city_manifest.csv')
        raw=self.read(p,'phase2_primary_target_raw.csv')
        target=self.read(p,'phase2_cleaned_target.csv')
        comp=self.read(p,'task3_composite_validation.csv')
        comp_sum=self.read(p,'task3_composite_validation_summary.csv')
        high=self.read(p,'task3_composite_high_residual_review.csv')
        decisions=self.read(p,'task3_composite_review_decisions.csv')
        coverage=self.read(p,'task4_year_country_coverage.csv')
        missing=self.read(p,'task4_missing_city_years.csv')
        reconciliation=self.read(p,'task5_coverage_reconciliation.csv')
        target_validation=self.read(p,'task5_target_validation.csv')
        feature=self.read(p,'task6_feature_matrix.csv')
        leakage=self.read(p,'task6_leakage_audit.csv')
        results=self.read(p,'task7_transfer_results.csv')
        split=self.read(p,'task7_split_manifest.csv')
        cleaning=self.read(p,'task5_cleaning_log.csv')

        if manifest is not None and {'UrbanId','Country','eligibility_status'}.issubset(manifest.columns):
            self.check('manifest unique UrbanId',not manifest['UrbanId'].duplicated().any(),f'rows={len(manifest)}, unique={manifest.UrbanId.nunique()}')
            quarantined=set(pd.to_numeric(manifest.loc[manifest.eligibility_status.eq('QUARANTINED'),'UrbanId'],errors='coerce').dropna().astype(int))
            eligible=manifest[manifest.eligibility_status.eq('INCLUDED')]
            country_counts=eligible.groupby('Country').UrbanId.nunique().to_dict()
            self.check('manifest eligible country counts',country_counts=={'China':1441,'Türkiye':180},country_counts)
            self.check('manifest disputed IDs quarantined',DISPUTED.issubset(quarantined),f'quarantined_disputed={len(DISPUTED & quarantined)}/13')
            included_ids=set(pd.to_numeric(eligible.UrbanId,errors='coerce').dropna().astype(int))
        else:
            included_ids=set(); quarantined=set()
            self.check('manifest schema',False,'required columns missing')

        if raw is not None:
            need={'UrbanId','year','Intensity_MEA','product','daynight','period','target_method','source_file'}
            self.check('raw target schema',need.issubset(raw.columns),f'missing={sorted(need-set(raw.columns))}')
            if need.issubset(raw.columns):
                years=pd.to_numeric(raw.year,errors='coerce')
                self.check('raw target years 2001-2020',bool(years.notna().all() and years.between(2001,2020).all()),f'min={years.min()}, max={years.max()}')
                self.check('raw target product/time/method',set(raw['product'].astype(str))=={'Mod2'} and set(raw['daynight'].astype(str))=={'Nig'} and set(raw['target_method'].astype(str))=={'Intensity_MEA'} and set(pd.to_numeric(raw.period,errors='coerce').dropna().astype(int))=={22},
                           f"product={raw['product'].unique()[:5]}, daynight={raw['daynight'].unique()[:5]}, method={raw['target_method'].unique()[:5]}, periods={sorted(pd.to_numeric(raw.period,errors='coerce').dropna().astype(int).unique().tolist())}")
                self.check('raw target key source traceability',raw.source_file.notna().all() and raw.source_file.astype(str).str.len().gt(0).all(),f'rows={len(raw)}')

        if target is not None:
            need={'UrbanId','year','Intensity_MEA','Country','source_file'}
            self.check('clean target schema',need.issubset(target.columns),f'missing={sorted(need-set(target.columns))}')
            if need.issubset(target.columns):
                keys=['UrbanId','year']
                self.check('clean target unique city-year',not target.duplicated(keys).any(),f'rows={len(target)}, duplicate_rows={int(target.duplicated(keys,keep=False).sum())}')
                y=pd.to_numeric(target.year,errors='coerce')
                self.check('clean target year scope',bool(y.notna().all() and y.between(2001,2020).all()),f'min={y.min()}, max={y.max()}')
                self.check('clean target target values complete',pd.to_numeric(target.Intensity_MEA,errors='coerce').notna().all(),f'missing={int(pd.to_numeric(target.Intensity_MEA,errors='coerce').isna().sum())}')
                self.check('clean target countries',set(target.Country.dropna().unique()).issubset(COUNTRIES) and set(target.Country.dropna().unique())==COUNTRIES, sorted(target.Country.dropna().unique().tolist()))
                t_ids=set(pd.to_numeric(target.UrbanId,errors='coerce').dropna().astype(int))
                self.check('clean target has no disputed IDs',not bool(t_ids & DISPUTED),f'intersection={sorted(t_ids & DISPUTED)}')
                self.check('clean target subset of included manifest',bool(t_ids.issubset(included_ids)) if included_ids else False, f'target_cities={len(t_ids)}, manifest_cities={len(included_ids)}')
                counts=target.groupby('Country').UrbanId.nunique().to_dict()
                self.check('clean target has both countries',set(counts)==COUNTRIES,counts)
                expected=len(included_ids)*len(YEARS) if included_ids else None
                if expected is not None:
                    self.check('clean target complete panel (if target exists each city-year)',len(target)==expected, f'rows={len(target)}, eligible_city_year_capacity={expected}', 'WARN')

        if coverage is not None:
            need={'year','country','method','period','eligible_cities_in_manifest','observed_city_year_keys','valid_target_city_years','duplicate_city_year_keys'}
            self.check('coverage schema',need.issubset(coverage.columns),f'missing={sorted(need-set(coverage.columns))}')
            if need.issubset(coverage.columns):
                expectedkeys={(c,y) for c in COUNTRIES for y in YEARS}
                actual={(str(r.country),int(r.year)) for r in coverage.itertuples() if pd.notna(r.year)}
                self.check('coverage has exactly 40 country-year rows',actual==expectedkeys and not coverage.duplicated(['country','year']).any(),f'rows={len(coverage)}, unique={len(actual)}')
                self.check('coverage primary target dimensions',set(coverage.method.astype(str))=={'Intensity_MEA'} and set(pd.to_numeric(coverage.period,errors='coerce').dropna().astype(int))=={22},f'methods={coverage.method.unique()}, periods={coverage.period.unique()}')
        if reconciliation is not None:
            ok='reconciles' in reconciliation.columns and len(reconciliation)>0 and reconciliation.reconciles.fillna(False).astype(bool).all()
            self.check('clean target reconciles with logged exclusions',ok,f'rows={len(reconciliation)}, failures={0 if not len(reconciliation) or "reconciles" not in reconciliation else int((~reconciliation.reconciles.fillna(False).astype(bool)).sum())}')
        if target_validation is not None:
            bool_cols=[c for c in ['no_duplicate_keys_in_final','all_targets_present','all_years_in_range','all_country_in_scope'] if c in target_validation.columns]
            flags=True
            if bool_cols:
                for c in bool_cols:
                    vals=target_validation[c]
                    flags &= bool(vals.map(lambda x: str(x).strip().lower() in {'true','1','yes'}).all())
            self.check('task5 target validation flags',bool_cols and flags,f'checked={bool_cols}')
        if cleaning is not None and {'action','reason_code'}.issubset(cleaning.columns):
            removed=cleaning['kept_or_removed'].astype(str).str.casefold().isin({'removed','excluded'}) if 'kept_or_removed' in cleaning else pd.Series(False,index=cleaning.index)
            self.check('cleaning log has traceable excluded rows',('UrbanId' in cleaning and 'source_file' in cleaning and 'reason_code' in cleaning and 'reason_detail' in cleaning),f'log_rows={len(cleaning)}, rows_marked_removed={int(removed.sum())}')

        if comp is not None:
            required={'UrbanId','year','season_MEA_period22','monthly_mean_MEA','abs_diff','comparison_status'}
            self.check('JJA comparison schema',required.issubset(comp.columns),f'missing={sorted(required-set(comp.columns))}')
            if required.issubset(comp.columns):
                self.check('JJA comparison unique city-year',not comp.duplicated(['UrbanId','year']).any(),f'rows={len(comp)}')
                diff=pd.to_numeric(comp.abs_diff,errors='coerce').dropna()
                observed=int((diff>=1.0).sum())
                self.check('JJA residual review accounts for >=1C rows',high is not None and len(high)==observed,f'absolute residuals >=1C: {observed}; review file rows={0 if high is None else len(high)}')
                if decisions is not None and len(high):
                    decision_schema={'UrbanId','year','decision','explanation'}.issubset(decisions.columns)
                    disposition_ok=False
                    if decision_schema:
                        d=decisions.copy()
                        d['decision']=d['decision'].fillna('').astype(str).str.strip()
                        d['explanation']=d['explanation'].fillna('').astype(str).str.strip()
                        hkeys=set(map(tuple, high[['UrbanId','year']].drop_duplicates().to_numpy()))
                        dkeys=set(map(tuple, d[['UrbanId','year']].drop_duplicates().to_numpy()))
                        relevant=d[d.apply(lambda r:(r['UrbanId'],r['year']) in hkeys,axis=1)]
                        disposition_ok=hkeys.issubset(dkeys) and (relevant.decision.ne('') & relevant.explanation.ne('')).all()
                    self.check('JJA high residuals have explicit documented dispositions',disposition_ok,
                               f'high residual rows={len(high)}, decision rows={0 if decisions is None else len(decisions)}')
        if comp_sum is not None and len(comp_sum)==1 and comp is not None and 'abs_diff' in comp.columns:
            diff=pd.to_numeric(comp.abs_diff,errors='coerce').dropna()
            if 'n_high_residuals_abs_diff_ge_1C' in comp_sum:
                self.check('JJA summary high-residual count matches detail',int(comp_sum.iloc[0].n_high_residuals_abs_diff_ge_1C)==int((diff>=1).sum()),
                           f'summary={comp_sum.iloc[0].n_high_residuals_abs_diff_ge_1C}, detail={int((diff>=1).sum())}')
            for summary_col,func in [('mean_abs_diff_C','mean'),('median_abs_diff_C','median'),('max_abs_diff_C','max')]:
                if summary_col in comp_sum.columns and len(diff):
                    expected=float(getattr(diff,func)())
                    actual=float(pd.to_numeric(pd.Series([comp_sum.iloc[0][summary_col]]),errors='coerce').iloc[0])
                    self.check(f'JJA summary {summary_col} matches detail',np.isfinite(actual) and abs(actual-expected)<=1e-8,
                               f'summary={actual}; detail={expected}')

        if feature is not None:
            self.check('baseline feature matrix unique city-year',{'UrbanId','year','Intensity_MEA'}.issubset(feature.columns) and not feature.duplicated(['UrbanId','year']).any(),f'rows={len(feature)}')
            predictors={'year','Longitude','Latitude','area_log'}
            self.check('baseline feature schema',predictors.issubset(feature.columns),f'missing={sorted(predictors-set(feature.columns))}')
            self.check('country/ID/target not in predictor declaration',not bool(predictors & FORBIDDEN),sorted(predictors & FORBIDDEN))
        if leakage is not None:
            req={'feature','included_in_model','target_derived_feature'}
            self.check('leakage audit schema',req.issubset(leakage.columns),f'missing={sorted(req-set(leakage.columns))}')
            if req.issubset(leakage.columns):
                in_model=leakage.included_in_model.map(lambda x: str(x).strip().lower() in {'true','1','yes'})
                target_derived=leakage.target_derived_feature.map(lambda x: str(x).strip().lower() in {'true','1','yes'})
                bad=leakage.loc[in_model & (target_derived | leakage.feature.astype(str).isin(FORBIDDEN)),'feature'].tolist()
                self.check('no target-derived feature admitted',not bad,f'forbidden features in main model={bad}')

        if results is not None:
            req={'direction','model','city_overlap','rmse','mae','r2'}
            self.check('baseline transfer results schema',req.issubset(results.columns),f'missing={sorted(req-set(results.columns))}')
            if req.issubset(results.columns):
                self.check('both transfer directions',{'China_to_Turkiye','Turkiye_to_China'}.issubset(set(results.direction)),sorted(results.direction.unique()))
                self.check('all baseline model types',{'source_mean','ridge','rf'}.issubset(set(results.model)),sorted(results.model.unique()))
                self.check('zero test-city overlap',bool((pd.to_numeric(results.city_overlap,errors='coerce')==0).all()),f'max_overlap={pd.to_numeric(results.city_overlap,errors="coerce").max()}')
                vals=results[['rmse','mae']].apply(pd.to_numeric,errors='coerce').to_numpy(float)
                self.check('finite baseline error metrics',bool(np.isfinite(vals).all()),f'rows={len(results)}')
        if split is not None:
            req={'direction','UrbanId','country_role'}
            self.check('baseline split manifest schema',req.issubset(split.columns),f'missing={sorted(req-set(split.columns))}')
            if req.issubset(split.columns):
                self.check('baseline split manifest unique city/direction',not split.duplicated(['direction','UrbanId']).any(),f'rows={len(split)}')
                role_sets={d:{r:set(g.loc[g.country_role.eq(r),'UrbanId'].astype(int)) for r in g.country_role.unique()} for d,g in split.groupby('direction')}
                overlaps=[]
                for d,rs in role_sets.items():
                    role_names=list(rs)
                    for i,r1 in enumerate(role_names):
                        for r2 in role_names[i+1:]:
                            overlaps.extend((d,x,r1,r2) for x in rs[r1]&rs[r2])
                self.check('split roles disjoint per direction',not overlaps,str(overlaps[:10]))

        # Enhanced external-features layer. It is mandatory for the complete project stage.
        external=self.read(e,'external_features.csv')
        ext_cov=self.read(e,'external_feature_coverage_by_country.csv')
        ext_sum=self.read(e,'external_features_qa_summary.csv')
        ext_req={'UrbanId','year','Country','elevation_m','era5_t2m_jja','era5_precip_jja_mm','era5_wind_jja','ndvi_jja_mean'}
        if external is not None:
            self.check('external feature schema',ext_req.issubset(external.columns),f'missing={sorted(ext_req-set(external.columns))}')
            if {'UrbanId','year','Country'}.issubset(external.columns):
                self.check('external feature unique city-year',not external.duplicated(['UrbanId','year']).any(),f'rows={len(external)}')
                ey=pd.to_numeric(external.year,errors='coerce')
                self.check('external feature year scope',bool(ey.notna().all() and ey.between(2001,2020).all()),f'min={ey.min()}, max={ey.max()}')
                if included_ids:
                    self.check('external panel full manifest-year shape',len(external)==len(included_ids)*20 and set(pd.to_numeric(external.UrbanId,errors='coerce').dropna().astype(int))==included_ids,
                               f'rows={len(external)}, expected_rows={len(included_ids)*20}, city_count={external.UrbanId.nunique()}')
        if ext_cov is not None:
            self.check('external coverage report nonempty',len(ext_cov)>0, f'rows={len(ext_cov)}')
        # DEM sidecar ties the actual table bytes to the cohort coordinates/source.
        dem_path=e/'dem_elevation.csv'
        dem_meta_path=e/'dem_elevation_metadata.json'
        self.check('DEM table present',dem_path.exists(),str(dem_path))
        self.check('DEM provenance sidecar present',dem_meta_path.exists(),str(dem_meta_path))
        if dem_path.exists() and dem_meta_path.exists():
            try:
                dm=json.loads(dem_meta_path.read_text(encoding='utf-8'))
                dh=hashlib.sha256()
                with dem_path.open('rb') as handle:
                    for block in iter(lambda:handle.read(8*1024*1024),b''): dh.update(block)
                self.check('DEM sidecar hash matches exact CSV',dm.get('file_sha256')==dh.hexdigest(),
                           f"metadata hash={dm.get('file_sha256')}; actual={dh.hexdigest()}")
                self.check('DEM source and coordinate signature documented','Copernicus DEM GLO-90' in str(dm.get('source','')) and bool(dm.get('coordinate_signature')),
                           f"source={dm.get('source')}; coordinate_signature_present={bool(dm.get('coordinate_signature'))}")
            except Exception as ex: self.check('DEM sidecar parses',False,repr(ex))
        dem_table=self.read(e,'dem_elevation.csv')
        if dem_table is not None:
            self.check('DEM table unique and has units/schema',{'UrbanId','elevation_m','dem_source'}.issubset(dem_table.columns) and not dem_table.UrbanId.duplicated().any(),
                       f'rows={len(dem_table)}; unique_cities={dem_table.UrbanId.nunique()}')

        ndvi_raw=e/'ndvi_raw_appEARS_combined.csv'
        ndvi_meta=e/'ndvi_raw_metadata.json'
        self.check('NDVI raw table present',ndvi_raw.exists(),str(ndvi_raw))
        self.check('NDVI request metadata sidecar present',ndvi_meta.exists(),str(ndvi_meta))
        if ndvi_meta.exists():
            try:
                nm=json.loads(ndvi_meta.read_text(encoding='utf-8'))
                self.check('NDVI sidecar has completed request fingerprint',nm.get('status')=='complete' and bool(nm.get('request_fingerprint')),
                           f"status={nm.get('status')}; fingerprint_present={bool(nm.get('request_fingerprint'))}")
                self.check('NDVI sidecar source product documented','MOD13Q1' in str(nm.get('source','')),
                           f"source={nm.get('source')}")
                if ndvi_raw.exists():
                    nh=hashlib.sha256()
                    with ndvi_raw.open('rb') as handle:
                        for block in iter(lambda:handle.read(8*1024*1024),b''): nh.update(block)
                    self.check('NDVI sidecar hash matches exact raw CSV',nm.get('file_sha256')==nh.hexdigest(),
                               f"metadata hash={nm.get('file_sha256')}; actual={nh.hexdigest()}")
            except Exception as ex:
                self.check('NDVI sidecar parses',False,repr(ex))
        else:
            self.check('NDVI sidecar source provenance',False,'raw NDVI may not be reused without request provenance')
        if ext_sum is not None and len(ext_sum):
            row=ext_sum.iloc[0]
            self.check('external feature panel QA duplicate keys zero','duplicate_city_year_keys' in row and int(row.duplicate_city_year_keys)==0,dict(row))
            if 'expected_rows' in row and 'rows' in row:
                self.check('external feature panel matches expected rows',int(row.rows)==int(row.expected_rows),f"rows={row.rows}; expected={row.expected_rows}")
        # ERA5 provenance sidecar is required; it binds exact request metadata to actual bytes.
        era_meta=p/'era5_land_jja_2001_2020_metadata.json'
        nc=p/'era5_land_jja_2001_2020.nc'
        self.check('ERA5 provenance sidecar present',era_meta.exists(),str(era_meta))
        if era_meta.exists() and nc.exists():
            try:
                meta=json.loads(era_meta.read_text(encoding='utf-8'))
                import hashlib
                digest=hashlib.sha256()
                with nc.open('rb') as handle:
                    for block in iter(lambda:handle.read(8*1024*1024),b''):
                        digest.update(block)
                h=digest.hexdigest()
                self.check('ERA5 sidecar hash matches exact NetCDF',meta.get('file_sha256')==h,f'metadata hash={meta.get("file_sha256")}; actual={h}')
                self.check('ERA5 sidecar has request fingerprint',bool(meta.get('request_fingerprint')),str(meta.get('request_fingerprint')))
            except Exception as ex: self.check('ERA5 sidecar parses',False,repr(ex))
        # Enhancement comparison + result outputs
        for name in ['task6_feature_matrix_enhanced.csv','task7_transfer_results_primary.csv','task7_transfer_results_enhanced.csv',
                     'task7_transfer_results_all_variants.csv','task7_split_manifest_enhanced.csv','task7_few_shot_selections_enhanced.csv',
                     'baseline_vs_enhanced_comparison.csv']:
            self.check(f'enhanced_file:{name}',(p/name).exists(),'required for complete external-feature experiment')
        enhanced=self.read(p,'task6_feature_matrix_enhanced.csv')
        enhanced_results=self.read(p,'task7_transfer_results_all_variants.csv')
        comparison=self.read(p,'baseline_vs_enhanced_comparison.csv')
        if enhanced is not None and {'UrbanId','year','Intensity_MEA'}.issubset(enhanced.columns):
            self.check('enhanced matrix unique city-year',not enhanced.duplicated(['UrbanId','year']).any(),f'rows={len(enhanced)}')
            bad=[x for x in ['Intensity_MEA_jun','Intensity_MEA_jul','Intensity_MEA_aug','Jun_MEA','Jul_MEA','Aug_MEA','season_MEA_period22','monthly_mean_MEA'] if x in enhanced.columns]
            # Historical diagnostic columns may be present in the joined table but cannot be in model feature declarations.
            self.check('no monthly target columns in enhanced matrix',not bad,f'columns={bad}','WARN')
        if enhanced_results is not None:
            req={'pool','direction','model','feature_set','test_city_overlap','rmse','mae'}
            self.check('enhanced transfer result schema',req.issubset(enhanced_results.columns),f'missing={sorted(req-set(enhanced_results.columns))}')
            if req.issubset(enhanced_results.columns):
                self.check('enhanced results contain both transfer directions',{'China_to_Turkiye','Turkiye_to_China'}.issubset(set(enhanced_results.direction)),sorted(enhanced_results.direction.unique()))
                self.check('enhanced results all model families',{'source_mean','ridge','rf'}.issubset(set(enhanced_results.model)),sorted(enhanced_results.model.unique()))
                self.check('enhanced results zero test overlap',bool((pd.to_numeric(enhanced_results.test_city_overlap,errors='coerce')==0).all()),f'max={pd.to_numeric(enhanced_results.test_city_overlap,errors="coerce").max()}')
                vals=enhanced_results[['rmse','mae']].apply(pd.to_numeric,errors='coerce').to_numpy(float)
                self.check('enhanced metrics finite',bool(np.isfinite(vals).all()),f'rows={len(enhanced_results)}')
        if comparison is not None:
            self.check('paired comparison nonempty',len(comparison)>0, f'rows={len(comparison)}')
            pair_keys=[c for c in ['pool','direction','model','few_shot_ratio','seed'] if c in comparison.columns]
            self.check('comparison unique matched key',bool(pair_keys) and not comparison.duplicated(pair_keys).any(),f'keys={pair_keys}; rows={len(comparison)}')
        enhanced_split=self.read(p,'task7_split_manifest_enhanced.csv')
        fewshot=self.read(p,'task7_few_shot_selections_enhanced.csv')
        if enhanced_split is not None:
            req={'pool','direction','UrbanId','role'}
            self.check('enhanced split manifest schema',req.issubset(enhanced_split.columns),f'missing={sorted(req-set(enhanced_split.columns))}')
            if req.issubset(enhanced_split.columns):
                unique_key=['pool','direction','UrbanId']
                self.check('enhanced split roles unique per pool/direction/city',not enhanced_split.duplicated(unique_key).any(),f'rows={len(enhanced_split)}')
                role_overlap=[]
                for (pool,direction),g in enhanced_split.groupby(['pool','direction']):
                    role_sets={role:set(pd.to_numeric(sub.UrbanId,errors='coerce').dropna().astype(int)) for role,sub in g.groupby('role')}
                    roles=list(role_sets)
                    for i,r1 in enumerate(roles):
                        for r2 in roles[i+1:]:
                            inter=role_sets[r1]&role_sets[r2]
                            if inter: role_overlap.append((pool,direction,r1,r2,len(inter)))
                self.check('enhanced split roles disjoint',not role_overlap,str(role_overlap[:10]))
                if fewshot is not None and {'pool','direction','UrbanId'}.issubset(fewshot.columns):
                    test_by={(pool,direction):set(pd.to_numeric(g.loc[g.role.astype(str).str.contains('TEST'),'UrbanId'],errors='coerce').dropna().astype(int))
                             for (pool,direction),g in enhanced_split.groupby(['pool','direction'])}
                    leaked=[]
                    for (pool,direction),g in fewshot.groupby(['pool','direction']):
                        testids=test_by.get((pool,direction),set())
                        leaked_ids=set(pd.to_numeric(g.UrbanId,errors='coerce').dropna().astype(int))&testids
                        if leaked_ids: leaked.append((pool,direction,sorted(leaked_ids)[:10]))
                    self.check('few-shot selections exclude locked test cities',not leaked,str(leaked[:10]))
                    if {'ratio_of_adaptation_pool','seed'}.issubset(fewshot.columns):
                        nested_violations=[]
                        for (pool,direction,seed),g in fewshot.groupby(['pool','direction','seed']):
                            ratios=sorted(pd.to_numeric(g.ratio_of_adaptation_pool,errors='coerce').dropna().unique())
                            sets={r:set(pd.to_numeric(g.loc[pd.to_numeric(g.ratio_of_adaptation_pool,errors='coerce').eq(r),'UrbanId'],errors='coerce').dropna().astype(int)) for r in ratios}
                            for lo,hi in zip(ratios,ratios[1:]):
                                if not sets[lo].issubset(sets[hi]): nested_violations.append((pool,direction,seed,lo,hi))
                        self.check('few-shot selections nested across ratios',not nested_violations,str(nested_violations[:10]))
        # Write reports
        audit=pd.DataFrame(self.rows)
        out_dir=p/'audit_reports'; out_dir.mkdir(parents=True,exist_ok=True)
        csv_path=out_dir/'PHASE2_POSTRUN_VALIDATION.csv'; audit.to_csv(csv_path,index=False)
        fails=audit.status.eq('FAIL').sum(); warns=audit.status.eq('WARN').sum()
        overall='GO' if fails==0 else 'NO-GO'
        lines=['# Phase 2 Post-Run Validation','',f'- Created: {datetime.now().isoformat(timespec="seconds")}',f'- Project root: `{self.root}`',f'- Overall machine-checkable status: **{overall}**',f'- Failed gates: {fails}',f'- Warnings: {warns}','',
               'This audit checks artefact structure, keys, counts, split isolation, lineage sidecars, and model output invariants. It does not independently validate the scientific correctness of every satellite pixel or replace review of flagged JJA residuals. A GO is a machine-checkable result only.','', '## Results','', '| Check | Status | Detail |','|---|---|---|']
        for r in self.rows:
            detail=str(r['detail']).replace('|','\\|').replace('\n',' ')[:220]
            lines.append(f"| {r['check']} | {r['status']} | {detail} |")
        md_path=self.docs/'PHASE2_FINAL_AUDIT.md'; self.docs.mkdir(parents=True,exist_ok=True); md_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
        print(audit.to_string(index=False))
        print(f'\nOverall: {overall}; failed gates={fails}, warnings={warns}')
        print('CSV report:',csv_path); print('Markdown report:',md_path)
        return 0 if fails==0 else 2

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project-dir',type=Path,default=None,help='Repository root. In GitHub layout, outputs/phase2_outputs and data/external_features are used; legacy phase2_outputs and external_features are also supported.')
    args=ap.parse_args()
    if args.project_dir:
        root=args.project_dir
    else:
        drive=Path('/content/drive/MyDrive')
        repo_candidates=[drive/'urban-heat-transfer', drive/'BIRLESIK_PROJE_PAKETI'/'urban-heat-transfer']
        root=next((p for p in repo_candidates if (p/'notebooks').is_dir() and (p/'data').is_dir()), None)
        if root is None:
            root=drive/'tao_documents' if (drive/'tao_documents').is_dir() else drive
    if not root.exists():
        print(f'Project directory not found: {root}',file=sys.stderr); return 2
    return Audit(root).run()
if __name__=='__main__': raise SystemExit(main())
