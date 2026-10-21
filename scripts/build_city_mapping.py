#!/usr/bin/env python3
"""Run the reviewed ID-based CityInfo/country-mapping merge."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from urban_heat_transfer.country_mapping import main
if __name__ == "__main__":
    raise SystemExit(main())
