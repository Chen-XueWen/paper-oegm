#!/usr/bin/env bash
set -euo pipefail

# PaperOEGM Stage 9 Paranoid LaTeX Compilation Wrapper
# Enforces openin_any=p, openout_any=p, --no-shell-escape, and isolated build/ directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

mkdir -p build

export openin_any="p"
export openout_any="p"
export TEXINPUTS=".:${TEXINPUTS:-}"
export BIBINPUTS=".:${BIBINPUTS:-}"
export BSTINPUTS=".:${BSTINPUTS:-}"

run_with_timeout() {
  if command -v timeout >/dev/null 2>&1; then
    timeout 120 "$@"
  elif command -v gtimeout >/dev/null 2>&1; then
    gtimeout 120 "$@"
  else
    "$@"
  fi
}

PDFLATEX_ARGS=(
  -interaction=nonstopmode
  -halt-on-error
  --no-shell-escape
  -output-directory=build
  main.tex
)

run_with_timeout pdflatex "${PDFLATEX_ARGS[@]}"
run_with_timeout bibtex build/main
run_with_timeout pdflatex "${PDFLATEX_ARGS[@]}"
run_with_timeout pdflatex "${PDFLATEX_ARGS[@]}"

cp build/main.pdf main.pdf
echo "[compile.sh] Built ${SCRIPT_DIR}/main.pdf cleanly."
