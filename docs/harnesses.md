# Cross-Harness Support & Verification Status

PaperOEGM (`paper-oegm`) uses one shared 1-level flat dispatch topology across **Antigravity**, **Claude Code / Cowork**, and **Codex / ChatGPT Work** with host-specific manifest and subagent wiring.

## Capability & Enforcement Matrix

| Host Harness | Manifest & Skill Entry | Subagent Dispatch Tool | Read-Only Critic Enforcement | Project Instruction Exclusion | Plugin-Root Path Resolution | Verification Status (v0.1) |
| --- | --- | --- | --- | --- | --- | --- |
| **Antigravity (CLI / App)** | Root `plugin.json`, `skills/po-*/SKILL.md`, `agents/po-*.md` | `invoke_subagent` (named personas) | **Runtime-enforced** (plugin subagents receive read-only tools only) | Caveat: `AGENTS.md`/`GEMINI.md` may load into subagents | Installed plugin root or `SKILL.md` parent traversal (`../..`) | Live-verified upon implementation |
| **Antigravity (Standalone IDE without subagent tool)** | Root `plugin.json`, `skills/po-*/SKILL.md` | None | Manual fresh-session fallback (`manual_review_prompts.md`; no in-thread grading) | User opens a fresh chat session | Installed plugin root or `SKILL.md` parent traversal (`../..`) | Fallback documented in `po-review` |
| **Claude Code / Cowork** | `.claude-plugin/plugin.json`, `.claude-plugin/agents/po-*.md` | `Agent` (named thin adapters) | **Tool-allowlist enforced** (`tools: [Read, Grep, Glob]`, `model: inherit`, no `memory`) | **Enforced** via `omitClaudeMd: true` | `${CLAUDE_PLUGIN_ROOT}` | Packaged and structurally verified via offline `pytest`; live end-to-end verification pending |
| **Codex / ChatGPT Work** | `.codex-plugin/plugin.json`, `skills/po-*/agents/openai.yaml` | `spawn_agent` (`fork_context: false` / `fork_turns: "none"`) | **Prompt-enforced only** (subagent reads `agents/po-*.md`; root verifies `<paper_workspace>/` tracked files via `po_tools.py check-readonly`) | Caveat: `AGENTS.md` may load into subagents | `SKILL.md` parent traversal (`../..`) | Packaged and structurally verified via offline `pytest`; live end-to-end verification pending |

## Why Flat Direct Dispatch (No Nested `synthesizer`)

Antigravity plugin subagents run strictly read-only without `invoke_subagent` or file-write tools; Claude Cowork forbids nested subagent spawning; Codex lacks reliable named-persona nesting. Dispatching all 5 read-only critics directly in parallel from the root session provides one portable execution graph across all three harnesses with zero unusable orchestrator files.

## Workspace Override & Symlink-Escape Confirmation

Users may override the default `./paper_workspace/` folder via a prompt line or a project instructions-file marker:

```text
PaperOEGM artifact directory: <path>
```

Relative paths resolve against the current working directory. If an instructions-file path resolves outside the working directory after following symbolic links, every skill **must** ask the user to confirm before creating the directory or writing inside it (falling back to `./paper_workspace/` and stating why if declined or headless).

## Known Host Caveats

* **Project instruction leakage (`AGENTS.md` / `GEMINI.md`):** Antigravity CLI and Codex may inject project instruction files into fresh subagents. Do **not** store draft paper claims, reviewer rebuttals, or experimental narratives inside project `AGENTS.md` or `GEMINI.md`.
* **Claude Code `"Default agents/ folder is ignored"` advisory:** `.claude-plugin/plugin.json` explicitly lists the 5 read-only adapters in `.claude-plugin/agents/po-*.md`, so Claude Code's informational notice that root `agents/` is ignored is expected behavior.
* **No automatic sibling skill chaining:** All 10 skills set `disable-model-invocation: true` so the model cannot silently invoke workflow stages without explicit user intent.
