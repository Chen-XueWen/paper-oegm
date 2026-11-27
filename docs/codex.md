# Codex & ChatGPT Work Integration

This guide covers installing and running `paper-oegm` inside Codex and ChatGPT Work.

## Installation

Build a standalone OpenAI/Codex runtime bundle with `scripts/pack_plugin.py`:

```bash
python3 scripts/pack_plugin.py --target openai --output /tmp/paper-oegm-dist
```

Or register the local repository catalog via `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json` (`requires_local_executor: true`).

## Fresh-Context Critic Dispatch & Read-Only Guard

1. Resolve plugin paths relative to the loaded `SKILL.md` via parent traversal (`../..`).
2. In `po-review` (and post-compile `po-format`), spawn up to 5 general-purpose subagents flat in parallel using `spawn_agent` with `fork_context: false` / `fork_turns: "none"`.
3. Instruct each subagent to read `agents/po-<role>.md` and its assigned `resources/review_standards/<standard>.md` first and never modify files or execute commands.
4. **Prompt-enforced read-only verification:** Because Codex enforces read-only critic behavior via prompts rather than a per-agent tool allowlist, the root session **must** snapshot `<paper_workspace>/` before dispatch and verify afterward using:

   ```bash
   python3 <plugin_root>/resources/scripts/po_tools.py check-readonly --workspace <ws> --snapshot <scratch>/ro.json --create
   # ... after critics return ...
   python3 <plugin_root>/resources/scripts/po_tools.py check-readonly --workspace <ws> --snapshot <scratch>/ro.json --verify
   ```

   This check inspects only tracked files inside `<paper_workspace>/` (never scanning external dataset directories) and fails closed if any file changed.

## Artifact Directory Override & `AGENTS.md` Caveat

* Override `./paper_workspace/` via a prompt line or `AGENTS.md`:

  ```text
  PaperOEGM artifact directory: <path>
  ```

  If an instructions-file path resolves outside the current working directory after following symbolic links, the agent must ask for explicit confirmation before creating or writing there (falling back to `./paper_workspace/` if declined or headless).
* Because Codex may inject project `AGENTS.md` into fresh subagents, do **not** place draft paper claims or rebuttals in `AGENTS.md`.

## Verification Status

Codex manifests, per-skill `agents/openai.yaml` metadata, icon palettes, and deterministic packaging are structurally verified via offline `pytest`; live end-to-end verification on Codex is pending.
