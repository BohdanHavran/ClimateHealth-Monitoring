"""Inspect the supplied CSV without changing it; no medical inference."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from climate_data_quality import inspect_number  # noqa: E402


def profile(path: Path) -> dict:
    raw = path.read_bytes()
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames
        if not columns or len(set(columns)) != len(columns):
            raise ValueError("CSV must have a non-empty, unique header")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError("CSV row has more fields than header")
    counts = Counter()
    data_errors = Counter()
    duplicates = len(rows) - len({tuple(row.get(c) for c in columns) for row in rows})
    complete = adjacent = any_pair = complete_bad = 0
    temp_fields = ("Min_Temp (°C)", "Avg_Temp (°C)", "Max_Temp (°C)")
    if not set(temp_fields).issubset(columns):
        raise ValueError("Required temperature columns missing")
    for row in rows:
        for val in row.values():
            if val is None or not val.strip():
                counts["empty_cells"] += 1
            elif val.strip().lower() == "nan":
                counts["nan_markers"] += 1
            elif val.strip().lower() == "unknown":
                counts["unknown_markers"] += 1
        vals = [inspect_number(row.get(name)) for name in temp_fields]
        a, b, c = [v.value if v.status == "valid" else None for v in vals]
        ab = a is not None and b is not None and a > b
        bc = b is not None and c is not None and b > c
        ac = a is not None and c is not None and a > c
        adjacent += bool(ab or bc)
        any_pair += bool(ab or bc or ac)
        full = all(v.status == "valid" for v in vals)
        complete += full
        complete_bad += bool(full and (ab or bc))
        for name in ("Latitude", "Longitude"):
            n = inspect_number(row.get(name), -90 if name == "Latitude" else -180,
                               90 if name == "Latitude" else 180)
            data_errors[f"{name}_{n.status}"] += 1
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "records": len(rows), "columns": len(columns), "headers": columns,
        **dict(counts), "full_duplicate_rows": duplicates,
        "temperature_adjacent_pair_violations": adjacent,
        "temperature_any_pair_violations": any_pair,
        "temperature_complete_triples": complete,
        "temperature_complete_triple_violations": complete_bad,
        "coordinate_status_counts": dict(data_errors),
        "provenance": "unknown",
        "health_target_note": "Not automatically assessed; inspect headers and source documentation.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", nargs="?", type=Path, default=ROOT / "climate_change_dataset.csv")
    args = parser.parse_args()
    print(json.dumps(profile(args.csv_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
