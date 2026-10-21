#!/usr/bin/env python3
"""Flag unusual Intensity_MEA values for human review; never removes or changes data.

The review uses per-file Tukey fences (Q1 - 1.5*IQR, Q3 + 1.5*IQR). These are
screening flags, not proof of errors. Negative UHII is allowed and is not inherently invalid.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

YEARS = range(2001, 2021)
PERIODS = (6, 7, 8, 22)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('data/raw/UHII_dataset'))
    parser.add_argument('--report', type=Path, default=Path('data/audit_reports/uhi_extreme_values_review.csv'))
    args = parser.parse_args()
    results: list[dict] = []
    for year in YEARS:
        for period in PERIODS:
            name = f'Mod2_Nig_{year}_{period}.csv'
            path = args.source / name
            if not path.is_file():
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': '', 'Intensity_MEA': '', 'q1': '', 'q3': '',
                                'lower_fence': '', 'upper_fence': '', 'review_flag': 'MISSING_FILE',
                                'note': 'Required exact Mod2 filename is missing; no substitute was used.'})
                continue
            try:
                frame = pd.read_csv(path, usecols=lambda c: c in {'UrbanId', 'Intensity_MEA'})
            except Exception as exc:
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': '', 'Intensity_MEA': '', 'q1': '', 'q3': '',
                                'lower_fence': '', 'upper_fence': '', 'review_flag': 'READ_ERROR',
                                'note': repr(exc)})
                continue
            if not {'UrbanId', 'Intensity_MEA'}.issubset(frame.columns):
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': '', 'Intensity_MEA': '', 'q1': '', 'q3': '',
                                'lower_fence': '', 'upper_fence': '', 'review_flag': 'SCHEMA_ERROR',
                                'note': 'Required UrbanId or Intensity_MEA column is missing.'})
                continue
            values = pd.to_numeric(frame['Intensity_MEA'], errors='coerce')
            valid = values.dropna()
            if valid.empty:
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': '', 'Intensity_MEA': '', 'q1': '', 'q3': '',
                                'lower_fence': '', 'upper_fence': '', 'review_flag': 'NO_VALID_VALUES',
                                'note': 'No numeric target values found; source file was not changed.'})
                continue
            q1, q3 = valid.quantile([0.25, 0.75]).tolist()
            iqr = q3 - q1
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            flagged = (values < low) | (values > high)
            # Invalid/non-numeric values are explicitly flagged for review separately.
            invalid = values.isna() & frame['Intensity_MEA'].notna() & frame['Intensity_MEA'].astype(str).str.strip().ne('')
            emitted = False
            for idx in frame.index[flagged.fillna(False) | invalid.fillna(False)]:
                emitted = True
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': frame.at[idx, 'UrbanId'], 'Intensity_MEA': frame.at[idx, 'Intensity_MEA'],
                                'q1': q1, 'q3': q3, 'lower_fence': low, 'upper_fence': high,
                                'review_flag': 'NONNUMERIC_TARGET' if bool(invalid.loc[idx]) else 'TUKEY_FENCE_REVIEW',
                                'note': 'Review flag only. Value was not removed, replaced, or declared erroneous.'})
            if not emitted:
                results.append({'filename': name, 'year': year, 'period': period,
                                'UrbanId': '', 'Intensity_MEA': '', 'q1': q1, 'q3': q3,
                                'lower_fence': low, 'upper_fence': high, 'review_flag': 'NO_TUKEY_FLAGS',
                                'note': f'Rows={len(frame)}; missing target values={int(values.isna().sum())}; all numeric values inside the per-file Tukey fences.'})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(args.report, index=False)
    print(f'Review report: {args.report.resolve()}')
    print(f'Report rows: {len(results):,}; this is a review aid only; source files were not modified.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
