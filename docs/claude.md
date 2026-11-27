# Claude Code & Cowork Integration

This guide covers installing and running `paper-oegm` inside Claude Code and Claude Cowork.

## Installation

Build a standalone Claude runtime bundle with `scripts/pack_plugin.py` or install directly from the repository marketplace:

```bash
python3 scripts/pack_plugin.py --target claude --output /tmp/paper-oegm-dist
```

Or add the marketplace in Claude Code:

```text
/plugin marketplace add Chen-XueWen/paper-oegm
/plugin install paper-oegm@paper-oegm
```

## Read-Only Critic Architecture

* `.claude-plugin/plugin.json` registers 5 explicit read-only adapters under `.claude-plugin/agents/po-*.md` (`tools: [Read, Grep, Glob]`, `model: inherit`, `omitClaudeMd: true`, no `memory`).
* Each adapter instructs the critic to read `${CLAUDE_PLUGIN_ROOT}/agents/po-<role>.md` and `${CLAUDE_PLUGIN_ROOT}/resources/review_standards/<standard>.md` first and audit strictly local workspace files (zero URL fetches, zero file writes).
* Because `.claude-plugin/plugin.json` specifies `agents` explicitly, Claude Code's advisory `"Default agents/ folder is ignored"` is expected.
* Claude Cowork prohibits nested subagents; `po-review` dispatches all applicable critics flat in parallel directly from the root session.

## Cross-Skill Handoffs (`disable-model-invocation: true`)

All 10 `po-*` skills set `disable-model-invocation: true`, which prevents automatic invocation of sibling skills. At each stage gate, invoke the next slash command (e.g., `/paper-oegm:po-outline`) directly, or confirm explicitly if you want the current thread to read `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/SKILL.md` in-place.

## Artifact Directory Override

Override the default `./paper_workspace/` folder by adding a line to `CLAUDE.md` or your prompt:

```text
PaperOEGM artifact directory: <path>
```

If an instructions-file path resolves outside the current working directory after following symbolic links, the agent must ask for explicit confirmation before creating the directory or writing there (falling back to `./paper_workspace/` if declined or headless).

## Verification Status

Claude Code / Cowork packaging, manifests, read-only adapter tool allowlists, and link integrity are structurally verified via offline `pytest`; live end-to-end verification on Claude Code is pending.
