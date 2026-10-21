#!/usr/bin/env python3
"""Validate notebook JSON and parse all non-empty Python code cells."""
from pathlib import Path
import ast, re, sys
import nbformat
ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = sorted((ROOT / "notebooks").glob("*.ipynb"))
if not NOTEBOOKS:
    print("No notebooks found", file=sys.stderr); raise SystemExit(2)
problems=[]
for path in NOTEBOOKS:
    try:
        nb=nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        for i, cell in enumerate(nb.cells):
            if cell.cell_type != "code" or not cell.source.strip():
                continue
            try: ast.parse(cell.source)
            except SyntaxError as exc: problems.append(f"{path.name} cell {i}: {exc}")
            for line in cell.source.splitlines():
                # Fail only on literal credential assignments, not on Colab Secret lookups.
                if re.search(r"(?i)\b(api[_-]?key|password|access[_-]?token|secret)\s*=\s*(['\"]).+?\2", line):
                    problems.append(f"{path.name} cell {i}: possible hard-coded credential assignment")
        print(f"PASS: {path.name} ({len(nb.cells)} cells)")
    except Exception as exc:
        problems.append(f"{path.name}: {exc}")
if problems:
    print("\n".join(problems), file=sys.stderr); raise SystemExit(1)
print(f"All {len(NOTEBOOKS)} notebooks passed structural, syntax, and credential-literal checks.")
