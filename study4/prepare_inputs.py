#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import DATA_DIR, load_xlsx_rows, parse_novel_data_predictor

OUT_DIR = Path(__file__).resolve().parent / "inputs"
DATA_FILE = DATA_DIR / "GPT Novel Data Prediction Data 20240227.xlsx"

TASK_TO_REAL_COLUMN = {
    "implicit_sexuality_prediction": "Sexuality - Avg. D (Real)",
    "explicit_sexuality_prediction": "Sexuality Avg. Explicit (Real)",
    "implicit_age_prediction": "Age - Avg. D (Real)",
    "explicit_age_prediction": "Age Avg. Explicit (Real)",
    "implicit_gender_science_prediction": "Gend - Avg. D (Real)",
    "explicit_gender_science_prediction": "Gend Avg. Explicit (Real)",
}

REAL_DATA_COLUMNS = [
    "Country",
    "Sexuality - Avg. D (Real)",
    "Sexuality Avg. Explicit (Real)",
    "Sexuality Avg. Therm (Real)",
    "Age - Avg. D (Real)",
    "Age Avg. Explicit (Real)",
    "Age Avg. Therm (Real)",
    "Gend - Avg. D (Real)",
    "Gend Avg. Explicit (Real)",
    "Gend Avg. Therm (Real)",
]


def write_json(name, data):
    path = OUT_DIR / name
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_csv(name, rows, fieldnames):
    path = OUT_DIR / name
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = parse_novel_data_predictor()
    real_rows = load_xlsx_rows(DATA_FILE)
    real_data_rows = [{column: row.get(column) for column in REAL_DATA_COLUMNS} for row in real_rows]
    task_rows = []
    for task in tasks:
        task_rows.append({
            "task": task["task"],
            "title": task["title"],
            "real_column": TASK_TO_REAL_COLUMN[task["task"]],
            "initial_prompt": task["initial_prompt"],
            "followup_prompt": task["followup_prompt"],
        })
    country_rows = []
    for row in real_rows:
        country = row.get("Country")
        if not country:
            continue
        country_rows.append({
            "country": country,
            "included_in_author_prompt": "0" if country == "(United States)" else "1",
            "implicit_sexuality_real": row.get("Sexuality - Avg. D (Real)"),
            "explicit_sexuality_real": row.get("Sexuality Avg. Explicit (Real)"),
            "implicit_age_real": row.get("Age - Avg. D (Real)"),
            "explicit_age_real": row.get("Age Avg. Explicit (Real)"),
            "implicit_gender_science_real": row.get("Gend - Avg. D (Real)"),
            "explicit_gender_science_real": row.get("Gend Avg. Explicit (Real)"),
        })
    paths = []
    paths.append(write_json("study4_tasks.json", task_rows))
    paths.append(write_csv("study4_tasks.csv", task_rows, ["task", "title", "real_column", "initial_prompt", "followup_prompt"]))
    paths.append(write_csv("real_country_data.csv", real_data_rows, REAL_DATA_COLUMNS))
    paths.append(write_csv("real_country_data_compact.csv", country_rows, ["country", "included_in_author_prompt", "implicit_sexuality_real", "explicit_sexuality_real", "implicit_age_real", "explicit_age_real", "implicit_gender_science_real", "explicit_gender_science_real"]))
    for path in paths:
        print(path)
    print(f"tasks={len(task_rows)}")
    print(f"countries_in_real_data={len(country_rows)}")
    print(f"countries_in_author_prompt={sum(1 for r in country_rows if r['included_in_author_prompt'] == '1')}")


if __name__ == "__main__":
    main()
