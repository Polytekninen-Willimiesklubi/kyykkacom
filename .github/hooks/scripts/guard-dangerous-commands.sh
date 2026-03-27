#!/usr/bin/env bash
set -euo pipefail

input_json="$(cat)"

# Ask for explicit user confirmation when a payload appears to include dangerous shell patterns.
if printf '%s' "$input_json" | grep -Eiq '(git reset --hard|git checkout --|rm -rf /|rm -rf ~|:\(\)\s*\{\s*:\|:\&\s*\};:)'; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Potentially destructive command detected. Please confirm before proceeding."}}
JSON
  exit 0
fi

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
JSON
