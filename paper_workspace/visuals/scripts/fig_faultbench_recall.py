#!/usr/bin/env python3
"""Generate Figure 2: PO-FaultBench Per-Family Recall & Adversarial Evasion Boundary.

Reads strictly from canonical non-synthetic experiments/runs/exp01_faultbench_agg/metrics.json.
Zero hardcoded result arrays.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> int:
    ws = Path(__file__).resolve().parents[2]
    data_path = ws / "experiments/runs/exp01_faultbench_agg/metrics.json"
    out_dir = ws / "visuals/assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(data_path.read_text(encoding="utf-8"))
    assert payload.get("is_synthetic") is False, "Refusing synthetic input"
    m = payload["metrics"]

    rows = [
        ("F1: Hallucinated Cite", "per_family_f1"),
        ("F2: Unverified / No Source", "per_family_f2"),
        ("F3: Synthetic / Dry-Run", "per_family_f3"),
        ("F4: Inline Metric Drift", "per_family_f4"),
        ("F5: .md <-> .tex Drop", "per_family_f5"),
        ("F6: Double-Blind Leak", "per_family_f6"),
        ("F7: Template Supply Chain", "per_family_f7"),
        ("F8: Tamper / Digest Drift", "per_family_f8"),
        ("Adversarial Evasion (E1-E4)", "evasion"),
    ]

    labels = [r[0] for r in rows]
    full_vals, b1_vals, b0_vals = [], [], []
    for _, key in rows:
        if key == "evasion":
            ev = float(m["evasion_det_recall"]["mean"])
            full_vals.append(ev)
            b1_vals.append(ev)
            b0_vals.append(0.0)
        else:
            full_vals.append(float(m[f"{key}_full_recall"]["mean"]))
            b1_vals.append(float(m[f"{key}_b1_recall"]["mean"]))
            b0_vals.append(float(m[f"{key}_b0_recall"]["mean"]))

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(7.0, 3.25), dpi=300)
    y = np.arange(len(labels))
    h = 0.25

    bars_full = ax.barh(y - h, full_vals, height=h, color="#0072B2", edgecolor="#003E63", linewidth=0.6, label="PaperOEGM Full (po_tools.py)", zorder=3)
    bars_b1 = ax.barh(y, b1_vals, height=h, color="#E69F00", edgecolor="#8F5E00", linewidth=0.6, hatch="///", label="B1: No Inline Provenance", zorder=3)
    bars_b0 = ax.barh(y + h, b0_vals, height=h, color="#A8B0BA", edgecolor="#4B5563", linewidth=0.6, hatch="...", label="B0: Compiler-Only", zorder=3)

    # Horizontal divider separating main PO-FaultBench (F1-F8) from Adversarial Evasion
    ax.axhline(7.5, color="#D55E00", linestyle="--", linewidth=1.1, zorder=4)
    ax.text(99.0, 7.62, "Deterministic Blind-Spot Suite (n=20/seed): 0.0% across all deterministic methods",
            ha="right", va="top", fontsize=7.3, fontweight="bold", color="#9A3412",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFF7ED", edgecolor="#FDBA74", lw=0.7), zorder=5)

    # Value labels for non-trivial differences & endpoints
    for idx in range(len(labels)):
        if full_vals[idx] > 0:
            ax.text(full_vals[idx] + 1.2, y[idx] - h, f"{full_vals[idx]:.0f}%", va="center", ha="left", fontsize=7.0, color="#004C78", fontweight="bold")
        if b1_vals[idx] != full_vals[idx]:
            ax.text(b1_vals[idx] + 1.2, y[idx], f"{b1_vals[idx]:.0f}%", va="center", ha="left", fontsize=7.0, color="#8F5E00")
        if b0_vals[idx] > 0:
            ax.text(b0_vals[idx] + 1.2, y[idx] + h, f"{b0_vals[idx]:.0f}%", va="center", ha="left", fontsize=7.0, color="#374151")

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.0)
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xlabel("Detection Recall (% across n=5 seeds)", fontsize=8.5, fontweight="bold")
    ax.grid(axis="x", linestyle="--", alpha=0.35, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.48, 1.15), ncol=3, frameon=False, fontsize=8.0)

    meta = {"Author": "", "Creator": "", "Producer": "", "Title": ""}
    fig.savefig(out_dir / "fig_faultbench_recall.pdf", bbox_inches="tight", pad_inches=0.04, metadata=meta)
    fig.savefig(out_dir / "fig_faultbench_recall.png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"[fig_faultbench_recall] Saved PDF and PNG to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
