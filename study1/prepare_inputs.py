#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from reproduce import BREADTH_LEVELS, parse_research_librarian

OUT_DIR = Path(__file__).resolve().parent / "inputs"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tasks = parse_research_librarian()
    for task in tasks:
        task["breadth_level"] = BREADTH_LEVELS.get(task["breadth"])
    json_path = OUT_DIR / "study1_topics_and_prompts.json"
    csv_path = OUT_DIR / "study1_topics_and_prompts.csv"
    json_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["breadth", "breadth_level", "topic", "initial_prompt", "followup_template"])
        writer.writeheader()
        writer.writerows(tasks)
    print(f"Wrote {len(tasks)} Study 1 tasks")
    print(json_path)
    print(csv_path)


if __name__ == "__main__":
    main()
