#!/usr/bin/env python3
import json
from pathlib import Path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    seeds_path = base_dir / "seed_examples_20.json"
    out_dir = base_dir / "source_docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    seeds = json.loads(seeds_path.read_text(encoding="utf-8"))
    for seed in seeds:
        seed_dir = out_dir / seed["example_id"]
        seed_dir.mkdir(exist_ok=True)
        for doc in seed["input"]["documents"]:
            text = []
            text.append(f"doc_id: {doc.get('doc_id', '')}")
            text.append(f"source_type: {doc.get('source_type', '')}")
            text.append(f"title: {doc.get('title', '')}")
            text.append(f"date: {doc.get('date', '')}")
            text.append("")
            text.append(doc.get("content", ""))
            file_path = seed_dir / f"{doc.get('doc_id', 'unknown_doc')}.txt"
            file_path.write_text("\n".join(text), encoding="utf-8")

    print(f"Exported source docs for {len(seeds)} seeds into {out_dir}")


if __name__ == "__main__":
    main()
