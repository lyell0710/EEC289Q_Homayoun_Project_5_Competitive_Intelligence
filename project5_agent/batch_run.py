#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from runner import CompetitiveIntelligenceAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch run agent on seed examples.")
    parser.add_argument("--seeds", required=True, help="Path to seed_examples_20.json")
    parser.add_argument("--output_dir", required=True, help="Directory for generated outputs")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    seeds = json.loads(Path(args.seeds).read_text(encoding="utf-8"))
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for sample in seeds:
        example_id = sample["example_id"]
        payload = sample["input"]
        agent = CompetitiveIntelligenceAgent()
        result = agent.analyze(payload)
        out_path = output_dir / f"{example_id}.output.json"
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Generated {len(seeds)} outputs in {output_dir}")


if __name__ == "__main__":
    main()
