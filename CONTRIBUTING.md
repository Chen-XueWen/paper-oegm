# Contributing to PaperOEGM (`paper-oegm`)

Contributions, bug reports, venue template additions, and multi-harness test reports are welcome at [https://github.com/Chen-XueWen/paper-oegm](https://github.com/Chen-XueWen/paper-oegm).

## Guidelines

1. **Zero external API keys & zero end-user `pip install`:** Keep all skills executable through host built-in tools and optional local CLI binaries, and keep `resources/scripts/po_tools.py` Python 3.10+ stdlib only.
2. **Skill & agent size ceilings:** Keep every `skills/po-*/SKILL.md` at `<= 250 lines` and `<= 12,000 bytes` (whole file), and every root `agents/po-*.md` at `<= 6,000 bytes` with zero host-specific frontmatter keys.
3. **Upstream LaTeX template licenses:** Never modify upstream `.sty`, `.bst`, or `.cls` files under `resources/templates/`; document every added template's upstream license in `THIRD_PARTY_NOTICES.md`.
4. **Verification before opening a pull request:** Run the full offline test suite and packager:

   ```bash
   python3 -m pytest tests/unit -v
   python3 scripts/pack_plugin.py --target all --output /tmp/paper-oegm-dist
   ```

5. **Community standards:** All contributors and maintainers follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
6. **Licensing:** Contributions are submitted under the repository's [Apache-2.0 License](LICENSE).
