---
description: "Repository-wide engineering rules for kyykkacom. Use when working on any task in this workspace."
applyTo: "**"
---

## Project Architecture
- Backend API and business logic are Django-based.
- Frontend is Vue + Pinia.
- API contract typing is centralized in frontend type definitions.
- Frontend to backend call-chain: Vue Components -> Pinia Stores -> Calls API (url.py contains api-endpoints)-> Django Views/Serializers -> Database/ORM.

## Core Behavior Rules
- Prefer minimal, safe changes over broad refactors.
- Preserve existing API response field names unless task explicitly includes contract migration.
- If backend serializer or view response shape changes, update frontend types and affected store/component usages in the same task.
- Never introduce new any usage when a concrete type is feasible.
- Avoid silent behavior changes in ranking, ordering, playoff/bracket logic, or season filtering.

## Typing And Contracts
- Keep frontend API interfaces aligned with backend responses.
- If response fields may be string-or-number or string-or-NaN style values, model them explicitly in types.
- Use backend payload field names as source of truth.

## Verification Expectations
- For frontend changes, run typecheck and resolve all introduced errors.
- For backend API changes, validate serializer/view output shape consistency and affected frontend call sites.
- Report residual risks and any untested edge cases.

## Response Style
- Summarize what changed and why.
- List impacted areas and potential regressions.
- Keep recommendations practical and repository-specific.
