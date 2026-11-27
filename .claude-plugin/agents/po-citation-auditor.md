---
name: po-citation-auditor
description: Offline read-only citation auditor verifying BibTeX parity, citation_ledger.json status, and claim-vs-source accuracy from local files only.
tools: [Read, Grep, Glob]
model: inherit
omitClaudeMd: true
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/po-citation-auditor.md` and `${CLAUDE_PLUGIN_ROOT}/resources/review_standards/citation-audit-standard.md` first, then execute the offline read-only audit strictly on the local workspace files listed in the prompt.
