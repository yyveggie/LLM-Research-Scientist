#!/usr/bin/env python3
import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean, stdev

DATASET_CONFIGS = {
    "good_bad": {"target_a": "female", "target_b": "male", "attr_a": "good", "attr_b": "bad", "label": "Female vs Male, Good-Bad"},
    "art_science": {"target_a": "female", "target_b": "male", "attr_a": "art", "attr_b": "science", "label": "Female vs Male, Art-Science"},
    "home_work": {"target_a": "female", "target_b": "male", "attr_a": "home", "attr_b": "work", "label": "Female vs Male, Home-Work"},
    "reading_math": {"target_a": "female", "target_b": "male", "attr_a": "reading", "attr_b": "math", "label": "Female vs Male, Reading-Math"},
}


def norm(value):
    return str(value or "").strip().lower()


def parse_score(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def read_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def safe_mean(values):
    return mean(values) if values else None


def safe_stdev(values):
    return stdev(values) if len(values) > 1 else math.nan


def safe_d(numerator, denominator):
    if numerator is None or not denominator or math.isnan(denominator):
        return math.nan
    return numerator / denominator


def scored_rows(rows, score_column):
    out = []
    for row in rows:
        score = parse_score(row.get(score_column))
        if score is None:
            continue
        clean = dict(row)
        clean["_score"] = score
        clean["_dataset"] = norm(row.get("dataset"))
        clean["_target"] = norm(row.get("target"))
        clean["_attribute"] = norm(row.get("attribute"))
        clean["_gender_word"] = norm(row.get("gender_word"))
        clean["_stereotype_word"] = norm(row.get("stereotype_word"))
        out.append(clean)
    return out


def target_word_associations(subset, config):
    by_word = {}
    for row in subset:
        gender_word = row["_gender_word"]
        if not gender_word:
            continue
        by_word.setdefault((row["_target"], gender_word, row["_attribute"]), []).append(row["_score"])
    word_scores = []
    for target in [config["target_a"], config["target_b"]]:
        words = sorted({word for (row_target, word, _attribute) in by_word if row_target == target})
        for word in words:
            a_scores = by_word.get((target, word, config["attr_a"]), [])
            b_scores = by_word.get((target, word, config["attr_b"]), [])
            if not a_scores or not b_scores:
                continue
            word_scores.append({
                "target": target,
                "word": word,
                "association_score": mean(a_scores) - mean(b_scores),
            })
    return word_scores


def attribute_word_associations(subset, config):
    by_word = {}
    for row in subset:
        stereotype_word = row["_stereotype_word"]
        if not stereotype_word:
            continue
        by_word.setdefault((row["_attribute"], stereotype_word, row["_target"]), []).append(row["_score"])
    word_scores = []
    for attribute in [config["attr_a"], config["attr_b"]]:
        words = sorted({word for (row_attribute, word, _target) in by_word if row_attribute == attribute})
        for word in words:
            target_a_scores = by_word.get((attribute, word, config["target_a"]), [])
            target_b_scores = by_word.get((attribute, word, config["target_b"]), [])
            if not target_a_scores or not target_b_scores:
                continue
            word_scores.append({
                "attribute": attribute,
                "word": word,
                "association_score": mean(target_a_scores) - mean(target_b_scores),
            })
    return word_scores


def compute_weat(rows, score_column):
    scored = scored_rows(rows, score_column)
    results = []
    for dataset, config in DATASET_CONFIGS.items():
        subset = [row for row in scored if row["_dataset"] == dataset]
        word_scores = target_word_associations(subset, config)
        target_a_scores = [row["association_score"] for row in word_scores if row["target"] == config["target_a"]]
        target_b_scores = [row["association_score"] for row in word_scores if row["target"] == config["target_b"]]
        all_scores = [row["association_score"] for row in word_scores]
        denominator = safe_stdev(all_scores)
        numerator = mean(target_a_scores) - mean(target_b_scores) if target_a_scores and target_b_scores else None
        results.append({
            "dataset": dataset,
            "label": config["label"],
            "score_column": score_column,
            "target_a": config["target_a"],
            "target_b": config["target_b"],
            "attr_a": config["attr_a"],
            "attr_b": config["attr_b"],
            "n_target_a_words": len(target_a_scores),
            "n_target_b_words": len(target_b_scores),
            "mean_target_a_association": safe_mean(target_a_scores),
            "mean_target_b_association": safe_mean(target_b_scores),
            "sd_all_associations": denominator,
            "weat_d": safe_d(numerator, denominator),
        })
    return results


def compute_single_category_weat(rows, score_column):
    scored = scored_rows(rows, score_column)
    results = []
    for dataset, config in DATASET_CONFIGS.items():
        subset = [row for row in scored if row["_dataset"] == dataset]
        word_scores = target_word_associations(subset, config)
        for target in [config["target_a"], config["target_b"]]:
            scores = [row["association_score"] for row in word_scores if row["target"] == target]
            denominator = safe_stdev(scores)
            numerator = safe_mean(scores)
            results.append({
                "dataset": dataset,
                "label": config["label"],
                "score_column": score_column,
                "single_category_type": "target",
                "single_category": target,
                "comparison_a": config["attr_a"],
                "comparison_b": config["attr_b"],
                "n_words": len(scores),
                "mean_association": numerator,
                "sd_association": denominator,
                "sc_weat_d": safe_d(numerator, denominator),
            })
    return results


def compute_alternative_sc_weat(rows, score_column):
    scored = scored_rows(rows, score_column)
    results = []
    for dataset, config in DATASET_CONFIGS.items():
        subset = [row for row in scored if row["_dataset"] == dataset]
        word_scores = attribute_word_associations(subset, config)
        for attribute in [config["attr_a"], config["attr_b"]]:
            scores = [row["association_score"] for row in word_scores if row["attribute"] == attribute]
            denominator = safe_stdev(scores)
            numerator = safe_mean(scores)
            results.append({
                "dataset": dataset,
                "label": config["label"],
                "score_column": score_column,
                "single_category_type": "attribute",
                "single_category": attribute,
                "comparison_a": config["target_a"],
                "comparison_b": config["target_b"],
                "n_words": len(scores),
                "mean_association": numerator,
                "sd_association": denominator,
                "alternative_sc_weat_d": safe_d(numerator, denominator),
            })
    return results


def write_csv(path, rows, fieldnames):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Compute Study 3 WEAT-style D-scores from extracted dyad scores.")
    parser.add_argument("--input", default=str(Path(__file__).resolve().parent / "audit" / "score_extraction_template.csv"))
    parser.add_argument("--score-column", default="extracted_score")
    parser.add_argument("--output", default=str(Path(__file__).resolve().parent / "outputs" / "analysis" / "weat_d_scores.csv"))
    parser.add_argument("--single-category-output", default=str(Path(__file__).resolve().parent / "outputs" / "analysis" / "single_category_weat_scores.csv"))
    parser.add_argument("--alternative-output", default=str(Path(__file__).resolve().parent / "outputs" / "analysis" / "alternative_sc_weat_scores.csv"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows = read_rows(args.input)
    if not scored_rows(rows, args.score_column):
        raise SystemExit(f"No valid scores found in {args.input} column {args.score_column}. Fill the extraction CSV before running analysis.")
    weat_results = compute_weat(rows, args.score_column)
    single_category_results = compute_single_category_weat(rows, args.score_column)
    alternative_results = compute_alternative_sc_weat(rows, args.score_column)
    weat_fields = ["dataset", "label", "score_column", "target_a", "target_b", "attr_a", "attr_b", "n_target_a_words", "n_target_b_words", "mean_target_a_association", "mean_target_b_association", "sd_all_associations", "weat_d"]
    sc_fields = ["dataset", "label", "score_column", "single_category_type", "single_category", "comparison_a", "comparison_b", "n_words", "mean_association", "sd_association", "sc_weat_d"]
    alternative_fields = ["dataset", "label", "score_column", "single_category_type", "single_category", "comparison_a", "comparison_b", "n_words", "mean_association", "sd_association", "alternative_sc_weat_d"]
    write_csv(args.output, weat_results, weat_fields)
    write_csv(args.single_category_output, single_category_results, sc_fields)
    write_csv(args.alternative_output, alternative_results, alternative_fields)
    if args.json:
        print(json.dumps({
            "weat": weat_results,
            "single_category_weat": single_category_results,
            "alternative_sc_weat": alternative_results,
        }, ensure_ascii=False, indent=2))
    else:
        for row in weat_results:
            print(f"{row['dataset']}: WEAT D = {row['weat_d']}")
        print(args.output)
        print(args.single_category_output)
        print(args.alternative_output)


if __name__ == "__main__":
    main()
