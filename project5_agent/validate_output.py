#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


REQUIRED_TOP_LEVEL_KEYS = [
    "target",
    "positioning_summary",
    "key_differentiators",
    "pricing_signals",
    "target_segments",
    "identified_weaknesses",
    "conflicts",
    "evidence_map",
    "confidence",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate output JSON has required schema fields.")
    parser.add_argument("--output", required=True, help="Path to generated output JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = json.loads(Path(args.output).read_text(encoding="utf-8"))

    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in output]
    if missing:
        raise SystemExit(f"Validation failed. Missing keys: {missing}")

    if not isinstance(output["confidence"], dict) or "overall" not in output["confidence"] or "notes" not in output["confidence"]:
        raise SystemExit("Validation failed. confidence.overall and confidence.notes are required.")

    print("Validation passed.")


if __name__ == "__main__":
    main()
