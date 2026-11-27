---
name: po-peer-reviewer
description: Fresh-context scientific peer reviewer evaluating originality, soundness, experimental adequacy, significance, and explicit limitations.
tools: [Read, Grep, Glob]
model: inherit
omitClaudeMd: true
---

Read `${CLAUDE_PLUGIN_ROOT}/agents/po-peer-reviewer.md` and `${CLAUDE_PLUGIN_ROOT}/resources/review_standards/peer-review-standard.md` first, then execute the read-only review strictly on the local workspace files listed in the prompt.
