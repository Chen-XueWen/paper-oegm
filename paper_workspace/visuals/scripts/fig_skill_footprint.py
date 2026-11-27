#!/usr/bin/env python3
"""Generate Figure 3: Skill Packaging Footprint & Context Load Comparison.

Reads strictly from canonical non-synthetic experiments/runs/exp02_packaging_agg/metrics.json.
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
    data_path = ws / "experiments/runs/exp02_packaging_agg/metrics.json"
    out_dir = ws / "visuals/assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads(data_path.read_text(encoding="utf-8"))
    assert payload.get("is_synthetic") is False, "Refusing synthetic input"
    m = payload["metrics"]

    per_skill = {k: float(v["mean"]) / 1000.0 for k, v in m["per_skill_bytes"].items()}
    ordered = sorted(per_skill.items(), key=lambda kv: kv[1], reverse=True)
    s_names = [k for k, _ in ordered]
    s_vals = [v for _, v in ordered]

    egm_med_kb = float(m["egm_median_skill_bytes"]["mean"]) / 1000.0
    egm_max_kb = float(m["egm_max_skill_bytes"]["mean"]) / 1000.0
    mono_kb = float(m["monolithic_bytes"]["mean"]) / 1000.0
    act_max_kb = float(m["max_active_stage_bytes"]["mean"]) / 1000.0
    act_med_kb = float(m["median_active_stage_bytes"]["mean"]) / 1000.0
    start_kb = float(m["frontmatter_index_bytes"]["mean"]) / 1000.0
    ctx_red = float(m["context_reduction_pct"]["mean"])
    start_red = float(m["startup_index_reduction_pct"]["mean"])

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.1, 2.85), dpi=300, gridspec_kw={"width_ratios": [1.35, 1.0]})

    # Panel (a): Individual PaperOEGM SKILL.md sizes vs budgets & EGM reference
    y = np.arange(len(s_names))
    ax1.barh(y, s_vals, height=0.62, color="#0072B2", edgecolor="#003E63", linewidth=0.6, zorder=3)
    for yi, val in zip(y, s_vals):
        ax1.text(val + 0.35, yi, f"{val:.2f}", va="center", ha="left", fontsize=7.0, color="#1F2937")

    ax1.axvline(12.0, color="#009E73", linestyle="--", linewidth=1.2, label="PaperOEGM Budget (12.0 KB)", zorder=4)
    ax1.axvline(egm_med_kb, color="#E69F00", linestyle="-.", linewidth=1.2, label=f"EGM Median ({egm_med_kb:.1f} KB)", zorder=4)
    ax1.axvline(24.0, color="#D55E00", linestyle=":", linewidth=1.4, label="Antigravity Ceiling (24.0 KB)", zorder=4)
    ax1.axvline(egm_max_kb, color="#CC79A7", linestyle="-", linewidth=1.1, label=f"EGM Max ({egm_max_kb:.1f} KB)", zorder=4)

    ax1.set_yticks(y)
    ax1.set_yticklabels(s_names, fontsize=7.6)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 27.5)
    ax1.set_xlabel("Whole-File SKILL.md Size (KB)", fontsize=8.2, fontweight="bold")
    ax1.set_title("(a) Per-Skill Footprint vs. Limits", fontsize=8.5, fontweight="bold", pad=6)
    ax1.grid(axis="x", linestyle="--", alpha=0.35, zorder=0)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower right", fontsize=6.6, frameon=True, facecolor="#FFFFFF", edgecolor="#D1D5DB")

    # Panel (b): Context Load Comparison
    cats = ["Monolithic\n(B2)", "Active\n(Max)", "Active\n(Median)", "Startup\nIndex"]
    cvals = [mono_kb, act_max_kb, act_med_kb, start_kb]
    colors = ["#999999", "#56B4E9", "#0072B2", "#009E73"]
    hatches = ["...", "//", "", "xx"]
    x = np.arange(len(cats))
    bars = ax2.bar(x, cvals, width=0.58, color=colors, edgecolor="#1F2937", linewidth=0.7, zorder=3)
    for b, ht in zip(bars, hatches):
        if ht:
            b.set_hatch(ht)

    annots = [f"{mono_kb:.1f} KB", f"{act_max_kb:.1f} KB", f"{act_med_kb:.1f} KB\n(-{ctx_red:.1f}%)", f"{start_kb:.1f} KB\n(-{start_red:.1f}%)"]
    for xi, val, txt in zip(x, cvals, annots):
        ax2.text(xi, val + 2.2, txt, ha="center", va="bottom", fontsize=7.1, fontweight="bold", color="#111827")

    ax2.set_xticks(x)
    ax2.set_xticklabels(cats, fontsize=7.5)
    ax2.set_ylim(0, mono_kb * 1.24)
    ax2.set_ylabel("Loaded Prompt Context (KB)", fontsize=8.2, fontweight="bold")
    ax2.set_title("(b) Prompt Context Savings", fontsize=8.5, fontweight="bold", pad=6)
    ax2.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    plt.tight_layout(w_pad=1.6)
    meta = {"Author": "", "Creator": "", "Producer": "", "Title": ""}
    fig.savefig(out_dir / "fig_skill_footprint.pdf", bbox_inches="tight", pad_inches=0.04, metadata=meta)
    fig.savefig(out_dir / "fig_skill_footprint.png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"[fig_skill_footprint] Saved PDF and PNG to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
