#!/usr/bin/env python3
"""Audit the 80 required nighttime MOD2 UHII CSV files without modifying them."""
from __future__ import annotations
import argparse, csv, math, re, sys
from pathlib import Path

YEARS = range(2001, 2021)
PERIODS = (6, 7, 8, 22)
EXPECTED = [f"Mod2_Nig_{year}_{period}.csv" for year in YEARS for period in PERIODS]
REQUIRED_COLUMNS = {"UrbanId", "Intensity_MEA"}

def number(value):
    if value is None or str(value).strip().casefold() in {"", "na", "n/a", "nan", "null", "none"}:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "NONNUMERIC"
    return v if math.isfinite(v) else "NONFINITE"

def audit_one(path: Path, year: int, period: int) -> dict:
    row = {
        "filename": path.name, "year": year, "period": period,
        "file_exists": path.is_file(), "status": "MISSING",
        "row_count": 0, "unique_UrbanId": 0, "duplicate_UrbanId_rows": 0,
        "missing_Intensity_MEA": 0, "invalid_UrbanId": 0, "invalid_Intensity_MEA": 0,
        "min_Intensity_MEA": "", "max_Intensity_MEA": "", "notes": "",
    }
    if not path.is_file():
        row["notes"] = "Required exact filename not found; file was not inferred from AMod2/SMod2."
        return row
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = set(reader.fieldnames or [])
            if not REQUIRED_COLUMNS.issubset(headers):
                row["status"] = "FAIL_SCHEMA"
                row["notes"] = f"Missing required columns: {sorted(REQUIRED_COLUMNS - headers)}"
                return row
            ids, vals = [], []
            missing, invalid_ids, invalid_target = 0, 0, 0
            for record in reader:
                row["row_count"] += 1
                raw_id = record.get("UrbanId")
                try:
                    ident = int(float(raw_id))
                    if float(raw_id) != ident:
                        invalid_ids += 1
                    ids.append(ident)
                except (TypeError, ValueError):
                    invalid_ids += 1
                val = number(record.get("Intensity_MEA"))
                if val is None:
                    missing += 1
                elif isinstance(val, str):
                    invalid_target += 1
                else:
                    vals.append(val)
            row["unique_UrbanId"] = len(set(ids))
            row["duplicate_UrbanId_rows"] = len(ids) - len(set(ids))
            row["missing_Intensity_MEA"] = missing
            row["invalid_UrbanId"] = invalid_ids
            row["invalid_Intensity_MEA"] = invalid_target
            row["min_Intensity_MEA"] = min(vals) if vals else ""
            row["max_Intensity_MEA"] = max(vals) if vals else ""
            problems=[]
            if row["row_count"] == 0: problems.append("empty file")
            if row["duplicate_UrbanId_rows"]: problems.append("duplicate UrbanId rows")
            if invalid_ids: problems.append("invalid UrbanId")
            if invalid_target: problems.append("invalid Intensity_MEA values")
            if not vals: problems.append("no valid Intensity_MEA values")
            row["status"] = "PASS" if not problems else "FAIL_DATA"
            row["notes"] = "; ".join(problems) if problems else "Required columns present; missing target values are reported, not imputed."
    except Exception as exc:
        row["status"] = "FAIL_READ"
        row["notes"] = repr(exc)
    return row

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/raw/UHII_dataset"), help="Folder containing exact Mod2_Nig_YYYY_PERIOD.csv source files")
    parser.add_argument("--report", type=Path, default=Path("data/audit_reports/uhi_source_inventory.csv"), help="CSV report output path")
    parser.add_argument("--allow-partial", action="store_true", help="Audit files that exist and return success even if some of the 80 are absent (for sample-only checks).")
    args = parser.parse_args()
    source = args.source.resolve()
    reports=[]
    for name in EXPECTED:
        m = re.fullmatch(r"Mod2_Nig_(\d{4})_(\d{1,2})\.csv", name)
        assert m
        reports.append(audit_one(source/name, int(m.group(1)), int(m.group(2))))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("w", encoding="utf-8-sig", newline="") as handle:
        writer=csv.DictWriter(handle, fieldnames=list(reports[0].keys()))
        writer.writeheader(); writer.writerows(reports)
    exists=sum(bool(r["file_exists"]) for r in reports)
    failures=sum(r["status"].startswith("FAIL") for r in reports)
    passed=sum(r["status"]=="PASS" for r in reports)
    print(f"Source directory: {source}")
    print(f"Exact required files present: {exists}/80; data checks passed: {passed}; failures among present files: {failures}")
    print(f"Report: {args.report.resolve()}")
    if exists != 80 and not args.allow_partial:
        print("NO-GO: not all 80 exact Mod2_Nig files are present. AMod2/SMod2 files are not counted.", file=sys.stderr)
        return 2
    if failures:
        print("NO-GO: one or more present CSV files failed a data integrity check.", file=sys.stderr)
        return 3
    if exists == 80:
        print("PASS: all 80 exact filenames exist and have passed the checks above.")
    else:
        print("PARTIAL CHECK ONLY: this result does not establish full 2001–2020 readiness.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
