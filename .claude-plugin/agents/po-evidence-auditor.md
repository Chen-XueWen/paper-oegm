---
name: po-evidence-auditor
description: Read-only provenance auditor verifying manuscript numbers and plot scripts against canonical metrics.json, run_manifest.json, and BYO sources.
tools: [Read, Grep, Glob]
model: inherit
omitClaudeMd: true
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/po-evidence-auditor.md` and `${CLAUDE_PLUGIN_ROOT}/resources/review_standards/evidence-audit-standard.md` first, then execute the read-only audit strictly on the local workspace files listed in the prompt.
