# Project 5 Design Document (Competitive Intelligence Agent)

## Problem framing
The agent must extract decision-relevant competitive signals from one or more source documents and return structured output with evidence attribution. The key risk is over-summarization: generic text can look fluent but fail to support actual competitive decisions. Therefore, the design prioritizes selectivity, attribution, and conflict transparency over verbosity.

## Core design decisions
1. **Schema-first output**
   - We define a strict output schema with fixed sections: positioning, differentiators, pricing, segments, weaknesses, conflicts, evidence map, and confidence.
   - This improves downstream usability (consistent parsing) and reduces free-form hallucination.

2. **Evidence-linked claims**
   - Every claim in structured fields references `evidence_ids`.
   - Evidence is stored in `evidence_map` with `doc_id` + quote snippets for traceability.

3. **Conflict-preserving behavior**
   - Contradictory claims are surfaced under `conflicts`.
   - The model does not silently resolve contradictions unless there is clear timeline or specificity advantage.
   - Resolution status is explicitly labeled as unresolved, partially resolved, or resolved with preference.

4. **Conservative uncertainty handling**
   - If the source documents are sparse or marketing-heavy, output is intentionally partial.
   - The agent uses "Insufficient evidence" and lowers confidence instead of guessing.

## Implementation approach
- Week 2 baseline is implemented as a runnable multi-document rule-based extractor (`project5_agent/runner.py`) to guarantee deterministic behavior and end-to-end operability.
- The baseline detects key signal classes (pricing, feature differentiators, segments, weaknesses), constructs evidence links, and emits schema-compatible JSON.
- A batch-compatible dataset format is prepared via `seed_examples_20.json` for future evaluation loops.

## Known limitations
1. Rule-based extraction can miss paraphrased or implicit claims.
2. Conflict detection is currently pattern-driven and does not cover all semantic contradictions.
3. Weakness extraction is sensitive to lexical cues (for example, "only", "limited") and may over/under-trigger.
4. No external retrieval or verification pipeline is included in current baseline.

## Planned improvements
1. Add semantic claim normalization to reduce duplicates and improve precision.
2. Add date-aware contradiction resolution with stronger rationale generation.
3. Add automated evaluation over 20 seeds + headroom tasks (precision, recall, conflict accuracy).
4. Optionally hybridize: use LLM extraction constrained by schema and post-validation checks.

## Why this design fits the project
This design directly targets the assignment's stated challenges:
- avoiding hallucination (evidence-first extraction),
- cutting through marketing noise (selective signal policy),
- reconciling contradictions (explicit conflict objects with attribution).
It balances practical implementation speed (Week 2 runnable core) with extensibility toward Week 3 robustness goals.
