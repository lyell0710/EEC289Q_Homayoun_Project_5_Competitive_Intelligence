Project 5 delivers a Competitive Intelligence Agent that analyzes provided competitor documents and generates a structured, evidence-backed report for a target company/product.

The agent is designed around three principles: (1) evidence-first extraction to reduce hallucination, (2) selective signal detection to filter marketing-heavy text, and (3) explicit conflict handling with attribution across sources.

Submission package includes:
- finalized system prompt
- output schema and tool endpoint definition
- 20 seed examples spanning B2B SaaS, HealthTech, and FinTech
- source-document set for all seeds
- 5 headroom tasks with observed failure modes
- 1-page design document
- runnable project code zip

Current implementation is a runnable rule-based baseline with multi-document support, evidence mapping, and conflict reporting. It is intentionally conservative under sparse evidence and flags uncertainty through confidence labels.
