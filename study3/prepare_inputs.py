#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import DATA_DIR, chunks, dyads_for_output, load_xlsx_rows, make_dyad_prompt, parse_data_generator_material_prompts, sort_by_random_id

OUT_DIR = Path(__file__).resolve().parent / "inputs"

DATASETS = [
    ("good_bad", "GPT as Data Generator A - gender good-bad 20230227.xlsx", 10),
    ("art_science", "GPT as Data Generator B - gender art-science 20230227.xlsx", 10),
    ("home_work", "GPT as Data Generator C - gender home-work 20230227.xlsx", 15),
    ("reading_math", "GPT as Data Generator D - gender reading-math 20230227.xlsx", 10),
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
    prompts = parse_data_generator_material_prompts()
    paths = [write_json("study3_prompts.json", prompts)]
    prompt_rows = []
    batch_plan_rows = []
    all_dyad_rows = []
    for dataset_id, filename, default_batch_size in DATASETS:
        spec = prompts[dataset_id]
        batch_size = int(spec.get("batch_size", default_batch_size))
        prompt_rows.append({
            "dataset": dataset_id,
            "batch_size": batch_size,
            "initial_prompt": spec.get("initial_prompt", ""),
            "first_follow_up_prompt": spec.get("first_follow_up_prompt", ""),
            "second_follow_up_prompt": spec.get("second_follow_up_prompt", ""),
            "third_follow_up_prompt": spec.get("third_follow_up_prompt", ""),
        })
        rows = sort_by_random_id(load_xlsx_rows(DATA_DIR / filename))
        dyad_rows = []
        for row in rows:
            clean = {
                "dataset": dataset_id,
                "random_id": row.get("Random ID"),
                "gender_word": row.get("Gender Word"),
                "stereotype_word": row.get("Stereotype Word"),
                "target": row.get("Target"),
                "attribute": row.get("Attribute"),
            }
            dyad_rows.append(clean)
            all_dyad_rows.append(clean)
        paths.append(write_csv(
            f"{dataset_id}_dyads.csv",
            dyad_rows,
            ["dataset", "random_id", "gender_word", "stereotype_word", "target", "attribute"],
        ))
        for batch_index, batch in enumerate(chunks(rows, batch_size), start=1):
            prompt_text = make_dyad_prompt(batch, batch_index, batch_size, spec)
            batch_plan_rows.append({
                "dataset": dataset_id,
                "batch_index": batch_index,
                "batch_size": len(batch),
                "first_random_id": batch[0].get("Random ID"),
                "last_random_id": batch[-1].get("Random ID"),
                "prompt_text": prompt_text,
                "dyads_json": json.dumps(dyads_for_output(batch), ensure_ascii=False),
            })
    paths.append(write_csv(
        "study3_prompts.csv",
        prompt_rows,
        ["dataset", "batch_size", "initial_prompt", "first_follow_up_prompt", "second_follow_up_prompt", "third_follow_up_prompt"],
    ))
    paths.append(write_csv(
        "all_dyads.csv",
        all_dyad_rows,
        ["dataset", "random_id", "gender_word", "stereotype_word", "target", "attribute"],
    ))
    paths.append(write_csv(
        "batch_plan.csv",
        batch_plan_rows,
        ["dataset", "batch_index", "batch_size", "first_random_id", "last_random_id", "prompt_text", "dyads_json"],
    ))
    for path in paths:
        print(path)
    print(f"datasets={len(DATASETS)}")
    print(f"dyads={len(all_dyad_rows)}")
    print(f"batches={len(batch_plan_rows)}")


if __name__ == "__main__":
    main()
