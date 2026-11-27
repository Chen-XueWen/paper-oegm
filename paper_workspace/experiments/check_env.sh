#!/usr/bin/env bash
set -euo pipefail

# PaperOEGM Stage 3 fast preflight check (zero package installs).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/env.sh"

echo "[check_env] PYTHON_BIN=${PYTHON_BIN}"
"${PYTHON_BIN}" -c '
import sys
assert sys.version_info >= (3, 10), f"Need Python >=3.10, got {sys.version}"
for mod in ("json", "hashlib", "zipfile", "tarfile", "matplotlib", "PIL"):
    __import__(mod)
print(f"[check_env] Python {sys.version.split()[0]} and required modules OK")
'

for req in "${PO_TOOLS_PY}" "${PACK_PLUGIN_PY}"; do
  if [[ ! -f "${req}" ]]; then
    echo "[check_env] ERROR: Missing required file: ${req}" >&2
    exit 1
  fi
done

for bin_name in pdflatex bibtex pdfinfo pandoc pdftoppm; do
  if ! command -v "${bin_name}" >/dev/null 2>&1; then
    echo "[check_env] ERROR: Missing required binary: ${bin_name}" >&2
    exit 1
  fi
done

if [[ -d "${EGM_PLUGIN_DIR}" ]]; then
  echo "[check_env] EGM reference plugin found at \$HOME/.gemini/config/plugins/egm"
else
  echo "[check_env] WARNING: EGM reference plugin directory not found; B3 EGM metrics will report null"
fi

if command -v claude >/dev/null 2>&1; then
  echo "[check_env] claude CLI available: $(claude --version 2>/dev/null || echo unknown)"
else
  echo "[check_env] WARNING: claude CLI not on PATH; claude_validate_ok will report null"
fi

AVAIL_KB="$(df -k "${WORKSPACE_DIR}" | awk 'NR==2 {print $4}')"
echo "[check_env] Free disk KB: ${AVAIL_KB}"
if [[ "${AVAIL_KB}" -lt 204800 ]]; then
  echo "[check_env] ERROR: Less than 200 MB free disk space" >&2
  exit 1
fi

echo "[check_env] All preflight checks PASSED."
