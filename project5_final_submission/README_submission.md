# Final Submission Checklist

## Included deliverables
- `system_prompt_final.md`
- `output_schema.json`
- `tool_endpoint_definitions.json`
- `seed_examples_20.json` (20 input/output pairs, >= 2 industries)
- `source_docs/` (source documents grouped by seed example)
- `headroom_tasks_5.json` (5 failure-focused tasks)
- `design_doc_1page.md`
- `submission_note_portal.md` (ready-to-paste summary for portal text fields)

## Code deliverable
- Core runnable code is in `../project5_agent`.
- Recommended zip artifact name: `project5_code.zip`.

## Suggested pre-submit checks
1. Validate all JSON files parse correctly.
2. Run `project5_agent/runner.py` on at least 3 seed inputs.
3. Confirm all outputs contain evidence attribution and confidence.
