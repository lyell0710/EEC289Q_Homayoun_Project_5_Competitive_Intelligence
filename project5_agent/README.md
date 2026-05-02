# Project 5 Agent (Week 2 Core)

This folder contains a runnable baseline for Milestone 2 (multi-document agent).

## What it does
- Accepts one target and multiple documents as JSON input.
- Extracts structured competitive signals:
  - positioning summary
  - key differentiators
  - pricing signals
  - target segments
  - identified weaknesses
  - conflicts
  - evidence map
  - confidence
- Writes output JSON compatible with the Week 1 schema fields.

## Run
```bash
cd /Users/yuzhang_li/Desktop/EEC289Q_Homayoun/Projects/289QHomayoun+Project5_Competitive_Intelligence/project5_agent
python3 runner.py --input sample_input.json --output sample_output.json
```

## Input format
```json
{
  "target": "Company/Product Name",
  "documents": [
    {
      "doc_id": "doc_a",
      "source_type": "product_page",
      "title": "Title",
      "date": "YYYY-MM-DD",
      "content": "raw document text"
    }
  ]
}
```

## Notes
- This is a rule-based baseline to satisfy Week 2 end-to-end functionality.
- Week 3 should improve precision, reduce duplicate signals, and add stronger conflict resolution.
