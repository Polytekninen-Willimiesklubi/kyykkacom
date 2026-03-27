---
description: "Backend Django API rules for kyykkacom. Use for API views, serializers, query logic, and response shaping."
applyTo: "{api/**/*.py,kyykka/**/*.py,utils/**/*.py}"
---

## Backend Conventions
- Preserve response key names consumed by frontend unless migration is explicitly requested.
- Keep queryset logic readable and performance-aware.
- Favor clear annotation naming for computed stats.

## API Response Compatibility
- If you add or rename response fields, document impact and update frontend contract consumers in the same task.
- Keep numeric/statistical field semantics stable (totals, percentages, averages, standings).
- For nullable aggregates, normalize output intentionally and consistently.

## Serializer And View Discipline
- Use serializers for stable output shape whenever practical.
- In complex manual response assembly, keep key naming consistent across seasonal and all-time payloads.
- Add comments only where aggregation logic is non-obvious.

## Query And Performance Rules
- Use select_related/prefetch_related when it avoids obvious N+1 issues.
- Use of django `Serializer`s is allowed in smaller endpoints, but in larger queries should avoided in favor of explicit response shaping to avoid hidden query logic and performance pitfalls.
- Keep aggregation paths explicit and avoid repeated queryset scans when avoidable.
- Be careful with seasonal filters and match type constraints because they affect standings and history pages.

## Testing Expectations
- For API shape changes, validate representative payload examples.
- For ranking/stat changes, verify tie and edge conditions plus empty-season behavior.
