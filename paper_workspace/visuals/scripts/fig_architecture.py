#!/usr/bin/env python3
"""Generate Figure 1: PaperOEGM Architecture Diagram (non-quantitative vector diagram).

Outputs:
  visuals/assets/fig_architecture.pdf (metadata stripped)
  visuals/assets/fig_architecture.png (300 DPI preview)
"""

from __future__ import annotations

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


def draw_box(ax, x, y, w, h, title, subtitle="", fc="#FFFFFF", ec="#0072B2", lw=1.1, title_fs=6.8, sub_fs=5.7, title_color="#111827"):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.004,rounding_size=0.014",
        facecolor=fc, edgecolor=ec, linewidth=lw, zorder=3,
    )
    ax.add_patch(box)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.67, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4)
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=sub_fs, color="#374151", zorder=4, linespacing=1.22)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=title_fs, fontweight="bold", color=title_color, zorder=4, linespacing=1.18)


def draw_diamond(ax, cx, cy, rx, ry, label, fc="#FEF3C7", ec="#B45309"):
    pts = [(cx, cy + ry), (cx + rx, cy), (cx, cy - ry), (cx - rx, cy)]
    poly = Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=1.0, zorder=4)
    ax.add_patch(poly)
    ax.text(cx, cy, label, ha="center", va="center", fontsize=5.8, fontweight="bold", color="#78350F", zorder=5)


def arrow(ax, x1, y1, x2, y2, color="#4B5563", ls="-", lw=0.95):
    arr = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=4.0,head_width=2.3",
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

    fig, ax = plt.subplots(figsize=(7.4, 3.65), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Layer 1: Progressive-Disclosure Skills
    ax.add_patch(FancyBboxPatch((0.01, 0.69), 0.98, 0.29, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#F0F7FF", edgecolor="#0072B2", linewidth=1.0, zorder=1))
    ax.text(0.025, 0.945, "Layer 1: Progressive-Disclosure Skills (10 SKILL.md <= 12 KB, disable-model-invocation: true)",
            fontsize=7.0, fontweight="bold", color="#004C78", va="center", zorder=4)

    draw_box(ax, 0.024, 0.715, 0.275, 0.195,
             "Phase 1: Intake & Exps",
             "0:po-start -> 1a:po-literature\n2:po-exp-design -> 3:po-exp-code",
             fc="#FFFFFF", ec="#0072B2")
    draw_diamond(ax, 0.340, 0.812, 0.025, 0.036, "Gate")
    draw_box(ax, 0.381, 0.715, 0.255, 0.195,
             "Phase 2: Evidence & Draft",
             "4:po-outline -> 1b:po-lit (opt)\n5:po-visuals -> 6:po-draft",
             fc="#FFFFFF", ec="#0072B2")
    draw_diamond(ax, 0.677, 0.812, 0.025, 0.036, "Gate")
    draw_box(ax, 0.718, 0.715, 0.258, 0.195,
             "Phase 3: Review & Build",
             "7:po-review -> 8:po-resolve\n9:po-format (Venue PDF)",
             fc="#FFFFFF", ec="#0072B2")

    arrow(ax, 0.303, 0.812, 0.314, 0.812, color="#0072B2")
    arrow(ax, 0.366, 0.812, 0.377, 0.812, color="#0072B2")
    arrow(ax, 0.640, 0.812, 0.651, 0.812, color="#0072B2")
    arrow(ax, 0.703, 0.812, 0.714, 0.812, color="#0072B2")

    # Layer 2: Deterministic Verification Backbone
    ax.add_patch(FancyBboxPatch((0.01, 0.37), 0.98, 0.26, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#ECFDF5", edgecolor="#009E73", linewidth=1.0, zorder=1))
    ax.text(0.025, 0.600, "Layer 2: Zero-Dependency Deterministic Backbone (po_tools.py stdlib + paper_state.json)",
            fontsize=7.0, fontweight="bold", color="#065F46", va="center", zorder=4)

    tools = [
        (0.024, "state-sync", "SHA-256 digest drift\n& STATUS.md sync"),
        (0.267, "review-preflight", "Bib/ledger, dry_run &\n<!-- run:id --> audit"),
        (0.510, "check-readonly", "Pre/post SHA-256 guard\nfor read-only critics"),
        (0.753, "format-verify", "Zip Slip, shell-pipes,\n.md<->.tex & anonymity"),
    ]
    for tx, ttitle, tsub in tools:
        draw_box(ax, tx, 0.395, 0.223, 0.172, ttitle, tsub, fc="#FFFFFF", ec="#009E73", lw=1.05, title_fs=6.9, sub_fs=5.7)

    # Vertical connectors Layer 1 -> Layer 2
    arrow(ax, 0.161, 0.710, 0.135, 0.635, color="#009E73", ls="--", lw=0.95)
    arrow(ax, 0.508, 0.710, 0.378, 0.635, color="#009E73", ls="--", lw=0.95)
    arrow(ax, 0.847, 0.710, 0.864, 0.635, color="#009E73", ls="--", lw=0.95)

    # Layer 3a: Flat 1-Level Read-Only Critics
    ax.add_patch(FancyBboxPatch((0.01, 0.02), 0.64, 0.28, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#FFF7ED", edgecolor="#D55E00", linewidth=1.0, zorder=1))
    ax.text(0.025, 0.270, "Layer 3a: Flat 1-Level Read-Only Critics (<=1,500 tok, 0 writes)",
            fontsize=6.9, fontweight="bold", color="#9A3412", va="center", zorder=4)

    critics = [
        ("Peer\nReviewer", 0.024),
        ("Evidence\nAuditor", 0.149),
        ("Citation\nAuditor", 0.274),
        ("Visual/Fmt\nCritic", 0.399),
        ("Clarity\nReader", 0.524),
    ]
    # Clean bus line from check-readonly down to Layer 3a top edge
    ax.plot([0.621, 0.621], [0.390, 0.335], color="#D55E00", ls=":", lw=1.0, zorder=2)
    ax.plot([0.079, 0.621], [0.335, 0.335], color="#D55E00", ls=":", lw=1.0, zorder=2)
    for cname, cx in critics:
        draw_box(ax, cx, 0.045, 0.111, 0.185, cname, "", fc="#FFFFFF", ec="#D55E00", lw=1.0, title_fs=6.4, title_color="#7C2D12")
        arrow(ax, cx + 0.055, 0.335, cx + 0.055, 0.305, color="#D55E00", ls=":", lw=0.95)

    # Layer 3b: Sandboxed Build & Packaging
    ax.add_patch(FancyBboxPatch((0.67, 0.02), 0.32, 0.28, boxstyle="round,pad=0.004,rounding_size=0.014",
                                facecolor="#F5F3FF", edgecolor="#6D28D9", linewidth=1.0, zorder=1))
    ax.text(0.684, 0.270, "Layer 3b: Sandbox & Packaging",
            fontsize=6.9, fontweight="bold", color="#4C1D95", va="center", zorder=4)
    draw_box(ax, 0.684, 0.145, 0.292, 0.095,
             "Paranoid TeX Sandbox",
             "openin_any=p, --no-shell-escape",
             fc="#FFFFFF", ec="#6D28D9", lw=1.0, title_fs=6.5, sub_fs=5.5)
    draw_box(ax, 0.684, 0.038, 0.292, 0.092,
             "Multi-Harness Packager",
             "Antigravity | Claude | Codex (ZIP)",
             fc="#FFFFFF", ec="#6D28D9", lw=1.0, title_fs=6.5, sub_fs=5.5)
    arrow(ax, 0.864, 0.390, 0.830, 0.305, color="#6D28D9", ls="-", lw=0.95)

    meta = {"Author": "", "Creator": "", "Producer": "", "Title": ""}
    fig.savefig(out_dir / "fig_architecture.pdf", bbox_inches="tight", pad_inches=0.03, metadata=meta)
    fig.savefig(out_dir / "fig_architecture.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    print(f"[fig_architecture] Saved PDF and PNG to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
