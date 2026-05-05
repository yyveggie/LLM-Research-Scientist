#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path
from statistics import mean

TASK_TO_REAL_COLUMN = {
    "implicit_sexuality_prediction": "Sexuality - Avg. D (Real)",
    "explicit_sexuality_prediction": "Sexuality Avg. Explicit (Real)",
    "implicit_age_prediction": "Age - Avg. D (Real)",
    "explicit_age_prediction": "Age Avg. Explicit (Real)",
    "implicit_gender_science_prediction": "Gend - Avg. D (Real)",
    "explicit_gender_science_prediction": "Gend Avg. Explicit (Real)",
}

COUNTRY_ALIASES = {
    "South Korea": "Korea",
}


def norm(value):
    return str(value or "").strip()


def country_key(value):
    country = norm(value)
    return COUNTRY_ALIASES.get(country, country)


def parse_float(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 2:
        return math.nan
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    mx = mean(xs)
    my = mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in pairs)
    denom_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denom_x == 0 or denom_y == 0:
        return math.nan
    return numerator / (denom_x * denom_y)


def load_real_data(path):
    rows = read_csv(path)
    by_country = {}
    for row in rows:
        country = country_key(row.get("Country") or row.get("country"))
        if country:
            by_country[country] = row
    return by_country


def analyze(predictions, real_by_country):
    grouped = {}
    for row in predictions:
        model = norm(row.get("model"))
        task = norm(row.get("task"))
        repeat = norm(row.get("repeat"))
        if not model or not task or not repeat:
            continue
        grouped.setdefault((model, task, repeat), []).append(row)
    results = []
    for (model, task, repeat), rows in sorted(grouped.items()):
        real_column = TASK_TO_REAL_COLUMN.get(task)
        if real_column is None:
            continue
        predicted = []
        real = []
        used_countries = []
        for row in rows:
            original_country = norm(row.get("country"))
            country = country_key(original_country)
            if country in {"(United States)", "United States"}:
                continue
            pred_score = parse_float(row.get("predicted_score"))
            real_row = real_by_country.get(country)
            real_score = parse_float(real_row.get(real_column)) if real_row else None
            if pred_score is not None and real_score is not None:
                predicted.append(pred_score)
                real.append(real_score)
                used_countries.append(country)
        results.append({
            "model": model,
            "task": task,
            "repeat": repeat,
            "real_column": real_column,
            "n_countries": len(used_countries),
            "pearson_r": pearson(predicted, real),
            "countries_used": "; ".join(used_countries),
        })
    return results


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["model", "task", "repeat", "real_column", "n_countries", "pearson_r", "countries_used"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    base = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Compute Study 4 country-level correlations between model predictions and real data.")
    parser.add_argument("--predictions", default=str(base / "audit" / "prediction_extraction_template.csv"))
    parser.add_argument("--real-data", default=str(base / "inputs" / "real_country_data.csv"))
    parser.add_argument("--output", default=str(base / "outputs" / "analysis" / "prediction_correlations.csv"))
    args = parser.parse_args()
    predictions = read_csv(args.predictions)
    real_by_country = load_real_data(args.real_data)
    results = analyze(predictions, real_by_country)
    write_csv(args.output, results)
    for row in results:
        print(f"{row['model']} {row['task']} r{row['repeat']}: r = {row['pearson_r']} (n={row['n_countries']})")
    print(args.output)


if __name__ == "__main__":
    main()
