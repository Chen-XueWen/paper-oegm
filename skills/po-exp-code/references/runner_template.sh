#!/usr/bin/env bash
set -euo pipefail

# PaperOEGM safe parameterized experiment runner template.
# Writes strictly inside experiments/runs/<run_id>/ (or experiments/dry_run/<run_id>/ on --dry-run).

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/env.sh"

EXP_ID="${EXP_ID:-exp01_baseline}"
SEED="${SEED:-42}"
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --seed) SEED="$2"; shift 2 ;;
    --exp-id) EXP_ID="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_ID="${EXP_ID}_s${SEED}_${TIMESTAMP}"

if [[ "${DRY_RUN}" -eq 1 ]]; then
  OUT_DIR="${SCRIPT_DIR}/dry_run/${RUN_ID}"
  IS_SYNTHETIC="true"
else
  OUT_DIR="${SCRIPT_DIR}/runs/${RUN_ID}"
  IS_SYNTHETIC="false"
fi

mkdir -p "${OUT_DIR}"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Non-git fallback without tripping set -euo pipefail
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  GIT_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo none)"
  if [[ -n "$(git status --porcelain 2>/dev/null || true)" ]]; then
    GIT_DIRTY="true"
  else
    GIT_DIRTY="false"
  fi
else
  GIT_COMMIT="none"
  GIT_DIRTY="null"
fi

RAW_CMD="$0 $*"
REDACTED_CMD="$("${PYTHON_BIN:-python3}" -c '
import os, re, sys
s = sys.argv[1]
home = os.path.expanduser("~")
if home:
    s = s.replace(home, "$HOME")
s = re.sub(r"(--(?:token|api-key|password|secret)\s*=?\s*)\S+", r"\1<REDACTED>", s, flags=re.I)
s = re.sub(r"\b([A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASS)[A-Z0-9_]*=)\S+", r"\1<REDACTED>", s)
print(s)
' "${RAW_CMD}")"

write_manifest() {
  local status="$1"
  local exit_code="$2"
  local finished_at="$3"
  "${PYTHON_BIN:-python3}" -c '
import hashlib, json, os, socket, sys
out, run_id, status, started, finished, ec, synth, commit, dirty, cmd, seed = sys.argv[1:12]
payload = {
    "run_id": run_id,
    "status": status,
    "started_at": started,
    "finished_at": finished if finished != "null" else None,
    "exit_code": int(ec) if ec != "null" else None,
    "is_synthetic": synth == "true",
    "git_commit": commit,
    "git_dirty": None if dirty == "null" else (dirty == "true"),
    "cmd": cmd,
    "seeds": [int(seed)],
    "hardware": {
        "hostname_hash": "sha256:" + hashlib.sha256(socket.gethostname().encode()).hexdigest()[:16],
        "gpu": os.environ.get("CUDA_VISIBLE_DEVICES", "cpu"),
        "cpu_count": os.cpu_count() or 1,
    },
}
tmp = out + ".tmp"
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump(payload, fh, indent=2)
    fh.write("\n")
os.replace(tmp, out)
' "${OUT_DIR}/run_manifest.json" "${RUN_ID}" "${status}" "${STARTED_AT}" "${finished_at}" "${exit_code}" "${IS_SYNTHETIC}" "${GIT_COMMIT}" "${GIT_DIRTY}" "${REDACTED_CMD}" "${SEED}"
}

finalize() {
  local ec=$?
  local finished_at
  finished_at="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local final_status="completed"
  if [[ "${ec}" -ne 0 ]]; then
    final_status="failed"
  fi
  write_manifest "${final_status}" "${ec}" "${finished_at}"
}
trap finalize EXIT

write_manifest "running" "null" "null"

# Replace the block below with the project training/evaluation invocation.
# Ensure the script emits compact metrics.json (<10 KB) atomically via metrics.json.tmp rename
# and optional downsampled series.csv (<= 500 rows) inside "${OUT_DIR}".
if [[ "${DRY_RUN}" -eq 1 ]]; then
  "${PYTHON_BIN:-python3}" -c '
import json, os, sys
out_dir, run_id = sys.argv[1], sys.argv[2]
tmp = os.path.join(out_dir, "metrics.json.tmp")
with open(tmp, "w", encoding="utf-8") as fh:
    json.dump({"run_id": run_id, "is_synthetic": True, "metrics": {"demo_metric": 0.0}}, fh, indent=2)
    fh.write("\n")
os.replace(tmp, os.path.join(out_dir, "metrics.json"))
' "${OUT_DIR}" "${RUN_ID}" >"${OUT_DIR}/stdout.log" 2>"${OUT_DIR}/stderr.log"
else
  echo "Replace with real experiment command writing ${OUT_DIR}/metrics.json" >"${OUT_DIR}/stdout.log" 2>"${OUT_DIR}/stderr.log"
  exit 1
fi
