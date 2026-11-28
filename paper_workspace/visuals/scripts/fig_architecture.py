#!/usr/bin/env python3
"""Generate Figure 1: PaperOEGM Architecture Diagram (non-quantitative vector diagram).

Pass 2 polish: >= 6.8 pt subtitles, wider Gate diamonds, clean arrow shafts, Unicode glyphs.
"""

from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


def draw_box(ax, x, y, w, h, title, subtitle="", fc="#FFFFFF", ec="#0072B2", lw=1.1, title_fs=7.6, sub_fs=6.8, title_color="#111827"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.004,rounding_size=0.014",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.69, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=sub_fs, color="#374151", zorder=4, linespacing=1.22)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4, linespacing=1.18)


def draw_diamond(ax, cx, cy, rx, ry, label, fc="#FEF3C7", ec="#B45309"):
    pts = [(cx, cy + ry), (cx + rx, cy), (cx, cy - ry), (cx - rx, cy)]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.05, zorder=4)
    ax.add_patch(poly)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=6.8, fontweight="bold", color="#78350F", zorder=5)


def arrow(ax, x1, y1, x2, y2, color="#4B5563", ls="-", lw=1.05):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=4.5,head_width=2.6",
        color=color, linestyle=ls, linewidth=lw, zorder=2,
    )
    ax.add_patch(arr)


def main() -> int:
    ws = Path(__file__).resolve().parents[2]
    out_dir = ws / "visuals/assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(7.2, 4.15), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Layer 1: Progressive-Disclosure Skills
    ax.add_patch(FancyBboxPatch((0.008, 0.70), 0.984, 0.285, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#F0F7FF", edgecolor="#0072B2", linewidth=1.05, zorder=1))
    ax.text(0.022, 0.955, "Layer 1: Progressive-Disclosure Skills (10 SKILL.md ≤ 12 KB, disable-model-invocation: true)",
            fontsize=7.0, fontweight="bold", color="#004C78", va="center", zorder=4)

    draw_box(ax, 0.020, 0.722, 0.252, 0.200,
             "Phase 1: Intake & Exps",
             "0:po-start → 1a:po-lit\n2:exp-design → 3:exp-code",
             fc="#FFFFFF", ec="#0072B2", title_fs=7.2, sub_fs=6.6)
    draw_diamond(ax, 0.330, 0.822, 0.033, 0.042, "Gate")
    draw_box(ax, 0.388, 0.722, 0.232, 0.200,
             "Phase 2: Plan & Draft",
             "4:po-outline → 1b:lit (opt)\n5:po-visuals → 6:po-draft",
             fc="#FFFFFF", ec="#0072B2", title_fs=7.2, sub_fs=6.6)
    draw_diamond(ax, 0.678, 0.822, 0.033, 0.042, "Gate")
    draw_box(ax, 0.736, 0.722, 0.244, 0.200,
             "Phase 3: Review & Build",
             "7:po-review → 8:po-resolve\n9:po-format (Venue PDF)",
             fc="#FFFFFF", ec="#0072B2", title_fs=7.1, sub_fs=6.6)

    arrow(ax, 0.276, 0.822, 0.296, 0.822, color="#0072B2", lw=1.15)
    arrow(ax, 0.364, 0.822, 0.384, 0.822, color="#0072B2", lw=1.15)
    arrow(ax, 0.624, 0.822, 0.644, 0.822, color="#0072B2", lw=1.15)
    arrow(ax, 0.712, 0.822, 0.732, 0.822, color="#0072B2", lw=1.15)

    # Layer 2: Deterministic Verification Backbone
    ax.add_patch(FancyBboxPatch((0.008, 0.375), 0.984, 0.260, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#ECFDF5", edgecolor="#009E73", linewidth=1.05, zorder=1))
    ax.text(0.022, 0.605, "Layer 2: Zero-Dependency Deterministic Backbone (po_tools.py stdlib + paper_state.json)",
            fontsize=7.0, fontweight="bold", color="#065F46", va="center", zorder=4)

    tools = [
        (0.020, "state-sync", "SHA-256 digest drift\n& STATUS.md sync"),
        (0.265, "review-preflight", "Bib/ledger, dry-run &\ninline run:<id> audit"),
        (0.510, "check-readonly", "Pre/post SHA-256 guard\nfor read-only critics"),
        (0.755, "format-verify", "Zip Slip, shell-pipes,\n.md ↔ .tex & anonymity"),
    ]
    for tx, ttitle, tsub in tools:
        draw_box(ax, tx, 0.398, 0.225, 0.178, ttitle, tsub, fc="#FFFFFF", ec="#009E73", lw=1.05, title_fs=7.3, sub_fs=6.6)

    # Clean vertical connectors Layer 1 -> Layer 2
    arrow(ax, 0.146, 0.700, 0.132, 0.640, color="#009E73", ls="--", lw=1.1)
    arrow(ax, 0.504, 0.700, 0.378, 0.640, color="#009E73", ls="--", lw=1.1)
    arrow(ax, 0.858, 0.700, 0.868, 0.640, color="#009E73", ls="--", lw=1.1)

    # Layer 3a: Flat 1-Level Read-Only Critics
    ax.add_patch(FancyBboxPatch((0.008, 0.015), 0.638, 0.275, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#FFF7ED", edgecolor="#D55E00", linewidth=1.05, zorder=1))
    ax.text(0.022, 0.262, "Layer 3a: Flat 1-Level Critics (≤ 1,500 tok, 0 writes)",
            fontsize=7.0, fontweight="bold", color="#9A3412", va="center", zorder=4)

    critics = [
        ("Peer\nReviewer", 0.020),
        ("Evidence\nAuditor", 0.145),
        ("Citation\nAuditor", 0.270),
        ("Visual/Fmt\nCritic", 0.395),
        ("Clarity\nReader", 0.520),
    ]
    # Clean solid bus line with visible vertical arrow shafts into Layer 3a
    bus_y = 0.338
    ax.plot([0.622, 0.622], [0.375, bus_y], color="#D55E00", ls="-", lw=1.1, zorder=2)
    ax.plot([0.077, 0.622], [bus_y, bus_y], color="#D55E00", ls="-", lw=1.1, zorder=2)
    for cname, cx in critics:
        draw_box(ax, cx, 0.038, 0.114, 0.190, cname, "", fc="#FFFFFF", ec="#D55E00", lw=1.05, title_fs=7.0, title_color="#7C2D12")
        arrow(ax, cx + 0.057, bus_y, cx + 0.057, 0.294, color="#D55E00", ls="-", lw=1.05)

    # Layer 3b: Sandboxed Build & Packaging
    ax.add_patch(FancyBboxPatch((0.664, 0.015), 0.328, 0.275, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#F5F3FF", edgecolor="#6D28D9", linewidth=1.05, zorder=1))
    ax.text(0.678, 0.262, "Layer 3b: Sandbox & Packaging",
            fontsize=7.0, fontweight="bold", color="#4C1D95", va="center", zorder=4)
    draw_box(ax, 0.678, 0.140, 0.300, 0.095,
             "Paranoid TeX Sandbox",
             "openout_any=p, --no-shell-escape",
             fc="#FFFFFF", ec="#6D28D9", lw=1.0, title_fs=7.0, sub_fs=6.3)
    draw_box(ax, 0.678, 0.032, 0.300, 0.095,
             "Multi-Harness Packager",
             "Antigravity | Claude | Codex (ZIP)",
             fc="#FFFFFF", ec="#6D28D9", lw=1.0, title_fs=7.0, sub_fs=6.3)
    arrow(ax, 0.868, 0.375, 0.828, 0.294, color="#6D28D9", ls="-", lw=1.1)

    meta = {"Author": "", "Creator": "", "Producer": "", "Title": ""}
    fig.savefig(out_dir / "fig_architecture.pdf", bbox_inches="tight", pad_inches=0.03, metadata=meta)
    fig.savefig(out_dir / "fig_architecture.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"[fig_architecture] Saved PDF and PNG to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
