#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import ethicist_rubric_id, parse_ethicist

OUT_DIR = Path(__file__).resolve().parent / "inputs"


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
    materials = parse_ethicist()
    for vignette in materials["bad_vignettes"]:
        vignette["rubric_id"] = ethicist_rubric_id(vignette["id"])
    for vignette in materials["good_vignettes"]:
        vignette["rubric_id"] = ethicist_rubric_id(vignette["id"])
    paths = []
    paths.append(write_json("study2_materials.json", materials))
    paths.append(write_csv("bad_initial_prompts.csv", materials["bad_prompts"], ["prompt_id", "prompt"]))
    paths.append(write_csv("good_initial_prompt.csv", [{"prompt_id": 1, "prompt": materials["good_initial_prompt"]}], ["prompt_id", "prompt"]))
    paths.append(write_csv("bad_research_vignettes.csv", materials["bad_vignettes"], ["id", "rubric_id", "text"]))
    paths.append(write_csv("good_research_vignettes.csv", materials["good_vignettes"], ["id", "rubric_id", "text"]))
    paths.append(write_csv("rubrics.csv", materials["rubrics"], ["id", "text"]))
    for path in paths:
        print(path)
    print(f"bad_prompts={len(materials['bad_prompts'])}")
    print(f"bad_vignettes={len(materials['bad_vignettes'])}")
    print(f"good_vignettes={len(materials['good_vignettes'])}")
    print(f"rubrics={len(materials['rubrics'])}")


if __name__ == "__main__":
    main()
