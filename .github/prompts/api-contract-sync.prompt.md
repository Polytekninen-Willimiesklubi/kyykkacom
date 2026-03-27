---
description: "Synchronize backend response changes to frontend types and usages. Use when API fields changed or typing drift appears."
---

## Task
- Inspect changed backend response shape.
- Update frontend API interfaces.
- Update store/component call sites.
- List exact compatibility impacts.

## Inputs
- Backend files changed:
- Frontend files changed:
- Endpoint(s):
- Breaking change allowed: yes/no

## Required Output
- Updated type/interface proposal.
- Impacted frontend symbols and files.
- Risk checklist.
- Verification checklist.

## Constraints
- No new any unless justified.
- Keep naming consistent with backend keys.
- Prefer the smallest safe migration path.
