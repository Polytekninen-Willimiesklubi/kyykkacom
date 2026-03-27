---
description: "Diagnose bug from symptoms/logs and propose minimal safe fix first."
---

## Task
- Identify likely root cause from evidence.
- Propose the smallest safe fix.
- Provide fallback hypotheses if confidence is low.

## Inputs
- Error message/log:
- Reproduction steps:
- Suspected files:
- Recent related changes:

## Required Output
- Root cause hypothesis ranked by confidence.
- Minimal fix proposal.
- Alternative fixes with tradeoffs.
- Verification steps and regression checks.

## Constraints
- Prioritize correctness and compatibility.
- Avoid broad rewrites.
- Call out unknowns explicitly.
