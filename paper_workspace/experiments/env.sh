#!/usr/bin/env bash
# PaperOEGM Stage 3 Experiment Environment Configuration
# Parameterized local paths and offline telemetry defaults.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
export REPO_ROOT="$(cd "${WORKSPACE_DIR}/.." && pwd)"

if [[ -z "${PYTHON_BIN:-}" ]]; then
  if [[ -x "/opt/anaconda3/envs/deepseek-ocr/bin/python" ]]; then
    export PYTHON_BIN="/opt/anaconda3/envs/deepseek-ocr/bin/python"
  else
    export PYTHON_BIN="$(command -v python3)"
  fi
fi

export PO_TOOLS_PY="${REPO_ROOT}/resources/scripts/po_tools.py"
export PACK_PLUGIN_PY="${REPO_ROOT}/scripts/pack_plugin.py"
export EGM_PLUGIN_DIR="${EGM_PLUGIN_DIR:-${HOME}/.gemini/config/plugins/egm}"

export CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-}"
export WANDB_MODE="offline"
export HF_HUB_OFFLINE="1"
export DO_NOT_TRACK="1"
