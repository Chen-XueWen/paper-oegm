#!/usr/bin/env python3
"""Generate Figure 4: Verification Scalability & Citation Context Offloading.

Reads strictly from canonical non-synthetic experiments/runs/exp03_scalability_agg/{series.csv,metrics.json}.
Pass 2 polish: exterior legend above Panel (a), zoomed inset (35-62 ms) separating lower subcommands, SD notation.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main() -> int:
    ws = Path(__file__).resolve().parents[2]
    run_dir = ws / "experiments/runs/exp03_scalability_agg"
    out_dir = ws / "visuals/assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    assert payload.get("is_synthetic") is False, "Refusing synthetic input"

    rows = []
    with (run_dir / "series.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)

    x_labels = [f"{r['scale']}\n({r['citations']}c/{r['runs']}r)" for r in rows]
    x = np.arange(len(rows), dtype=float)

    series_specs = [
        ("Total (4 cmds)", "total_ms", "#0072B2", "o", "-", 0.0),
        ("state-sync", "state_sync_ms", "#D55E00", "s", "--", 0.0),
        ("check-readonly", "check_readonly_ms", "#009E73", "^", "-.", -0.06),
        ("review-preflight", "review_preflight_ms", "#E69F00", "D", ":", 0.0),
        ("format-verify", "format_verify_ms", "#CC79A7", "v", (0, (3, 1, 1, 1)), 0.06),
    ]

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.2,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.1, 3.10), dpi=300, gridspec_kw={"width_ratios": [1.22, 1.0]})

    # Panel (a): CLI Latency scaling (mean +/- SD across n=5)
    for label, col, color, marker, ls, _ in series_specs:
        means = [float(r[f"{col}_mean"]) for r in rows]
        stds = [float(r[f"{col}_std"]) for r in rows]
        ax1.errorbar(
            x, means, yerr=stds, label=label, color=color, marker=marker,
            linestyle=ls, linewidth=1.5, markersize=4.5, capsize=2.3, zorder=3,
        )

    # Zoomed inset separating the 35-62 ms subcommands cleanly between state-sync (125 ms) and Total (266 ms)
    axins = ax1.inset_axes([0.10, 0.48, 0.54, 0.26])
    for label, col, color, marker, ls, jitter in series_specs[2:]:
        means = [float(r[f"{col}_mean"]) for r in rows]
        stds = [float(r[f"{col}_std"]) for r in rows]
        axins.errorbar(
            x + jitter, means, yerr=stds, color=color, marker=marker,
            linestyle=ls, linewidth=1.2, markersize=3.8, capsize=2.0, zorder=3,
        )
    axins.set_xticks(x)
    axins.set_xticklabels([r["scale"] for r in rows], fontsize=6.4)
    axins.set_ylim(35, 63)
    axins.set_yticks([40, 50, 60])
    axins.tick_params(axis="y", labelsize=6.4)
    axins.set_title("Zoom: 35–63 ms subcommands", fontsize=6.5, fontweight="bold", pad=2)
    axins.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
    axins.set_facecolor("#FAFAFA")
    for sp in axins.spines.values():
        sp.set_edgecolor("#6B7280")
        sp.set_linewidth(0.75)

    tot_s = float(rows[0]["total_ms_mean"])
    tot_xl = float(rows[-1]["total_ms_mean"])
    ax1.annotate(
        f"+{tot_xl - tot_s:.1f} ms\n(6× scale)",
        xy=(x[-1], tot_xl), xytext=(x[-1] - 0.72, tot_xl - 66),
        fontsize=7.2, fontweight="bold", color="#004C78",
        arrowprops=dict(arrowstyle="->", color="#004C78", lw=0.95),
        zorder=5,
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(x_labels, fontsize=7.6)
    ax1.set_ylim(0, 315)
    ax1.set_ylabel("Wall-Clock Latency (ms, n=5)", fontsize=8.2, fontweight="bold")
    ax1.set_title("(a) CLI Latency Scaling (mean ± SD)", fontsize=8.5, fontweight="bold", pad=28)
    ax1.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.legend(loc="lower center", bbox_to_anchor=(0.48, 1.01), ncol=3, frameon=False, fontsize=6.9, columnspacing=0.8, handlelength=1.8)

    # Panel (b): Compact ledger vs offloaded sources
    ledger_kb = [float(r["ledger_bytes_mean"]) / 1000.0 for r in rows]
    sources_kb = [float(r["sources_bytes_mean"]) / 1000.0 for r in rows]
    offload_pct = [float(r["offload_pct_mean"]) for r in rows]

    w = 0.52
    ax2.bar(x, ledger_kb, width=w, color="#0072B2", edgecolor="#003E63", linewidth=0.6, label="citation_ledger.json (loaded)", zorder=3)
    ax2.bar(x, sources_kb, width=w, bottom=ledger_kb, color="#E69F00", edgecolor="#8F5E00", linewidth=0.6, hatch="///", label="literature/sources/ (offloaded)", zorder=3)

    for xi, lk, sk, op in zip(x, ledger_kb, sources_kb, offload_pct):
        ax2.text(xi, lk + sk + 4.5, f"{op:.1f}%\noffloaded", ha="center", va="bottom", fontsize=6.7, fontweight="bold", color="#8F5E00", linespacing=1.05)

    ax2.set_xticks(x)
    ax2.set_xticklabels(x_labels, fontsize=7.6)
    ax2.set_ylim(0, (ledger_kb[-1] + sources_kb[-1]) * 1.28)
    ax2.set_ylabel("Metadata Footprint (KB)", fontsize=8.2, fontweight="bold")
    ax2.set_title("(b) Citation Context Offloading", fontsize=8.5, fontweight="bold", pad=28)
    ax2.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.legend(loc="lower center", bbox_to_anchor=(0.48, 1.01), ncol=1, frameon=False, fontsize=7.1)

    plt.tight_layout(w_pad=1.6)
    meta = {"Author": "", "Creator": "", "Producer": "", "Title": ""}
    fig.savefig(out_dir / "fig_scalability.pdf", bbox_inches="tight", pad_inches=0.04, metadata=meta)
    fig.savefig(out_dir / "fig_scalability.png", dpi=300, bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)
    print(f"[fig_scalability] Saved PDF and PNG to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
