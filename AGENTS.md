# Contributor Agent Guidelines (`paper-oegm`)

## Repository Layout

* `plugin.json`, `.claude-plugin/`, `.codex-plugin/`, `.agents/` — Synchronized multi-harness plugin manifests and catalogs.
* `skills/po-*/` — 10 modular `SKILL.md` skills (`<= 250 lines`, `<= 12,000 bytes` whole-file), `agents/openai.yaml`, two-color `assets/icon.svg`, and closed `references/` templates.
* `agents/po-*.md` & `.claude-plugin/agents/po-*.md` — 5 stateless read-only critic personas (`<= 6,000 bytes` whole-file) and their Claude Code read-only adapters.
* `resources/` — Shared execution rules, 6 stage protocols, 5 review standards, zero-dependency stdlib helper CLI (`resources/scripts/po_tools.py`), and unmodified starter venue templates (`resources/templates/{cvpr2025,iclr2025}/`).
* `docs/` — Bundled runtime harness and privacy docs (`harnesses.md`, `claude.md`, `codex.md`, `privacy.md`) plus `docs/assets/*.svg` and unbundled `docs/designs/paper-oegm.md`.
* `scripts/pack_plugin.py` — Deterministic runtime packager for `--target antigravity|claude|openai|all`.
* `tests/unit/` — 7 offline unit-test modules verifying manifests, frontmatter, size ceilings, packaging, links, domain invariants, and `po_tools.py`.

## Development Commands

```bash
# Run offline unit and packaging test suite
python3 -m pytest tests/unit -v

# Build deterministic runtime bundles into a temp directory
python3 scripts/pack_plugin.py --target all --output /tmp/paper-oegm-dist
```

## Subagent Isolation Warning

Antigravity CLI and Codex may inject project `AGENTS.md` files into fresh subagents. When using `paper-oegm` inside a research repository, **never** store draft paper claims, experiment results, or reviewer rebuttals in `AGENTS.md`.
