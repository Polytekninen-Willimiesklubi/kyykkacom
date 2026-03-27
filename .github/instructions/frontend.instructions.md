---
description: "Frontend Vue/Pinia rules for kyykkacom. Use for stores, components, pages, router, and frontend API typing."
applyTo: "frontend/src/**/*.{ts,js,vue}"
---

## Frontend Conventions
- Use explicit TypeScript interfaces for API-backed state and computed values.
- Prefer narrow interfaces and union types over loose records.
- Keep Pinia store state serializable and predictable.

## Pinia Store Rules
- Keep loading, loaded, and error semantics consistent.
- Preserve current derived-data behavior unless explicitly changing product behavior.
- Avoid mutating objects in ways that can leak unintended side effects across computed trees.

## API Typing Rules
- Treat frontend API type files as the contract hub.
- When backend payloads evolve, update interfaces first, then consumers.
- Replace unknown-shape arrays with named interfaces.
- For partial data from backend, use optional fields instead of any.

## Data Safety
- Use defensive defaults for missing API keys.
- Handle null and undefined from API explicitly.
- For season-keyed maps, use index signatures or typed records intentionally.

## Code Quality
- Keep computed properties typed.
- Prefer small helper functions when a computed block becomes hard to read.
- Avoid broad Record<string, any> in user-facing data paths.
- In general avoid <any> unless a it's necessary and well-justified.
