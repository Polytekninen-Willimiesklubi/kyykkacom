#!/usr/bin/env bash
set -euo pipefail

input_json="$(cat)"

# Run only after likely file-edit tools to avoid unnecessary checks.
if ! printf '%s' "$input_json" | grep -Eiq '(apply_patch|create_file|replace_string_in_file|edit_notebook_file)'; then
  cat <<'JSON'
{"continue": true}
JSON
  exit 0
fi

# If no frontend files have changed, skip quickly.
if ! git diff --name-only -- frontend/src frontend/tsconfig.json frontend/package.json | grep -q .; then
  cat <<'JSON'
{"continue": true}
JSON
  exit 0
fi

# Run frontend typecheck and attach concise status for the session.
if [ -x "./frontend/node_modules/typescript/bin/tsc" ]; then
  if ./frontend/node_modules/typescript/bin/tsc --noEmit >/tmp/copilot-frontend-tsc.log 2>&1; then
    cat <<'JSON'
{"continue": true, "systemMessage": "Frontend typecheck passed after edit."}
JSON
  else
    cat <<'JSON'
{"continue": true, "systemMessage": "Frontend typecheck reported issues after edit. See /tmp/copilot-frontend-tsc.log."}
JSON
  fi
else
  cat <<'JSON'
{"continue": true, "systemMessage": "Skipped frontend typecheck: TypeScript binary not found at frontend/node_modules/typescript/bin/tsc."}
JSON
fi
