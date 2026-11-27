#!/usr/bin/env python3
"""Experiment 4: Hybrid Fresh-Context Semantic Audit (n=3 domain manuscripts).

Modes:
  generate       Build 3 realistic seeded domain workspaces (s42 ML Systems, s43 Vision Benchmarks,
                 s44 Agent Security) with 5 mechanical + 5 semantic/evasion defects each, plus real
                 PNG figures with deliberate visual legibility flaws (S5). Ground truth is stored
                 OUTSIDE the workspaces so read-only critics never see the answer key.
  deterministic  Run real po_tools.py (check-readonly --create, review-preflight, format-verify)
                 on a seeded workspace and record Deterministic-Only (B4) detection scores.
  score          Combine B4 results + verbatim live critic responses + check-readonly --verify
                 into canonical metrics.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


DOMAINS = {
    42: {
        "domain": "ml_systems",
        "title": "Adaptive KV-Cache Eviction for Long-Context Serving",
        "cites": {
            "kwon2023vllm": {
                "title": "Efficient Memory Management for Large Language Model Serving with PagedAttention",
                "abstract": "PagedAttention reduces KV-cache memory waste to under 4% and improves throughput by 2x to 4x over FasterTransformer without degrading output accuracy.",
                "year": 2023,
            },
            "zhang2023h2o": {
                "title": "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models",
                "abstract": "We show that retaining heavy-hitter tokens and recent tokens reduces KV-cache memory by 5x while maintaining generation quality, though heavy-hitter eviction incurs a 1.8% accuracy drop at 20% cache budget.",
                "year": 2023,
            },
            "xiao2024streaming": {
                "title": "Efficient Streaming Language Models with Attention Sinks",
                "abstract": "Keeping initial attention sink tokens enables infinite-length streaming generation without fine-tuning, achieving up to 22.2x speedup over sliding window recomputation.",
                "year": 2024,
            },
        },
        "s1_cite": "zhang2023h2o",
        "s1_distortion": "Prior heavy-hitter eviction [@zhang2023h2o] reported a 14.5% accuracy gain at 20% cache budget with zero degradation.",
        "s2_true_int": 4,
        "s2_fake_int": 16,
        "s2_metric_name": "num_benchmarks",
        "s3_overclaim": "Because our eviction score improves throughput on Llama-3-8B, it guarantees lossless serving on all multimodal video transformers and 100B+ MoE models. Note that we omit an ablation disabling the attention-sink anchor because it is intuitively necessary, extending our prior Munich Systems Group workshop paper.",
        "s4_symbol": r"\gamma_{\text{evict}}",
        "s4_acronym": "PKVE-M",
        "run_id": "exp_kv_s42",
        "acc_true": 88.4,
        "acc_fake": 93.7,
        "clean_tp": 3.42,
        "ghost_cite": "chen2025phantomkv",
        "leak_str": "/Users/maxmustermann/kv_project/runs",
    },
    43: {
        "domain": "vision_benchmarks",
        "title": "Calibration-Free Test-Time Adaptation Under Corrupted Video Streams",
        "cites": {
            "wang2021tent": {
                "title": "Tent: Fully Test-Time Adaptation by Entropy Minimization",
                "abstract": "Tent adapts batch normalization affine parameters via entropy minimization at test time, reducing ImageNet-C error from 82.0% to 55.6% without accessing source training data.",
                "year": 2021,
            },
            "niu2023sar": {
                "title": "Towards Stable Test-Time Adaptation in Dynamic Wild World",
                "abstract": "SAR removes noisy high-entropy samples and uses sharpness-aware minimization to prevent model collapse under mixed distribution shifts and small batch sizes down to 1.",
                "year": 2023,
            },
            "hendrycks2019robustness": {
                "title": "Benchmarking Neural Network Robustness to Common Corruptions and Perturbations",
                "abstract": "We introduce ImageNet-C and ImageNet-P covering 15 corruption types across 5 severity levels to evaluate vision classifier robustness.",
                "year": 2019,
            },
        },
        "s1_cite": "wang2021tent",
        "s1_distortion": "Entropy minimization in [@wang2021tent] requires full source training data access during adaptation and increased ImageNet-C error to 82.0%.",
        "s2_true_int": 5,
        "s2_fake_int": 15,
        "s2_metric_name": "num_corruptions_tested",
        "s3_overclaim": "Although evaluated only on 5 synthetic weather corruptions at batch size 32, our method solves real-world autonomous driving safety in all clinical and aerial domains. We do not include an ablation removing our temporal reset rule, following our team's earlier ETH Vision Lab benchmark.",
        "s4_symbol": r"\tau_{\text{drift}}",
        "s4_acronym": "CF-VTTA",
        "run_id": "exp_tta_s43",
        "acc_true": 76.2,
        "acc_fake": 82.9,
        "clean_tp": 61.8,
        "ghost_cite": "patel2025ghosttta",
        "leak_str": "https://github.com/eth-vision-private/cf-vtta-code",
    },
    44: {
        "domain": "agent_security",
        "title": "Capability-Scoped Sandboxing for Tool-Using Coding Agents",
        "cites": {
            "greshake2023indirect": {
                "title": "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection",
                "abstract": "Indirect prompt injections hidden in retrieved web pages or local files can hijack LLM-integrated applications into data exfiltration and arbitrary tool invocation.",
                "year": 2023,
            },
            "debenedetti2024agentdojo": {
                "title": "AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents",
                "abstract": "AgentDojo provides 97 realistic tasks and 629 security test cases showing that tool-filter defenses reduce attack success rate but still leave over 20% utility-security gap on frontier models.",
                "year": 2024,
            },
            "wu2025secagent": {
                "title": "Isolating Tool Permissions in Autonomous Software Agents",
                "abstract": "Least-privilege capability wrappers block unauthorized file writes in 91.4% of tested shell-injection cases while adding 6.2 ms median wrapper latency.",
                "year": 2025,
            },
        },
        "s1_cite": "debenedetti2024agentdojo",
        "s1_distortion": "Benchmark results in [@debenedetti2024agentdojo] proved that simple prompt-filter defenses completely eliminate prompt injection with 0% attack success across 97 tasks.",
        "s2_true_int": 3,
        "s2_fake_int": 12,
        "s2_metric_name": "num_agent_harnesses",
        "s3_overclaim": "Our sandbox eliminates all prompt-injection risks across every OS kernel and web browser deployment. We omit an ablation comparing against static allowlist filtering because our capability graph is clearly superior, building on our group's previous Seattle Security Institute release.",
        "s4_symbol": r"\Omega_{\text{cap}}",
        "s4_acronym": "CS-CAPG",
        "run_id": "exp_sec_s44",
        "acc_true": 91.4,
        "acc_fake": 97.6,
        "clean_tp": 6.2,
        "ghost_cite": "miller2025unlistedsec",
        "leak_str": "/home/jdoe/agent_sandbox_paper",
    },
}


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, obj: Any) -> None:
    write_text(path, json.dumps(obj, indent=2) + "\n")


def sha256_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def render_flawed_figure(out_png: Path, seed: int) -> None:
    """Render a real PNG plot with deliberate visual legibility flaws (S5): overlapping x-ticks, 4pt legend, clipped text."""
    fig, ax = plt.subplots(figsize=(3.4, 2.2), dpi=130)
    labels = [
        "Baseline-Long-Configuration-Alpha-v1",
        "Ablation-No-Anchor-Variant-Beta-v2",
        "Ablation-Static-Filter-Gamma-v3",
        "Proposed-Full-Method-Delta-v4",
    ]
    vals = [62.1 + (seed % 3), 71.4, 78.2, 88.4]
    bars = ax.bar(range(len(labels)), vals, color=["#d62728", "#2ca02c", "#d62728", "#2ca02c"])
    ax.set_xticks(range(len(labels)))
    # Deliberate horizontal long overlapping tick labels & tiny 4.5pt legend/annotations
    ax.set_xticklabels(labels, fontsize=8.5, rotation=0)
    ax.set_ylabel("Score")
    ax.set_title("Comparison Across Configurations (No Units)", fontsize=9)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v - 1.5, f"{v:.1f}±0.4 (p<0.01)", ha="center", fontsize=4.5, color="black")
    ax.legend([bars[0], bars[1]], ["Red-Green-Baseline-Series-Long-Name", "Red-Green-Proposed-Series-Long-Name"], fontsize=4.2, loc="upper left")
    fig.savefig(out_png, dpi=130)
    plt.close(fig)


def generate_fixture(fixtures_root: Path, seed: int) -> dict[str, Any]:
    cfg = DOMAINS[seed]
    ws = fixtures_root / f"exp04_s{seed}"
    if ws.exists():
        import shutil
        shutil.rmtree(ws)
    ws.mkdir(parents=True)

    write_text(ws / "intake_manifest.md", f"# Intake\nProject: {cfg['title']}\n")
    intake_hash = sha256_bytes((ws / "intake_manifest.md").read_bytes())
    write_json(
        ws / "paper_state.json",
        {
            "schema_version": "1.0",
            "project_title": cfg["title"],
            "venue": {"name": "agentskills2027", "template_year": 2027, "submission_mode": "double-blind", "page_limit_main": 9},
            "stages": {
                "po-start": {"status": "approved", "outputs": ["intake_manifest.md"], "output_hashes": {"intake_manifest.md": intake_hash}},
            },
        },
    )

    # Literature: 3 real verified entries, BUT mark the 3rd entry unverified_needs_human_check (M2!)
    cite_keys = list(cfg["cites"].keys())
    bib_lines = []
    ledger_entries = {}
    for idx, k in enumerate(cite_keys):
        c = cfg["cites"][k]
        bib_lines.append(
            f"@article{{{k},\n  title={{{c['title']}}},\n  author={{Author, A.}},\n  year={{{c['year']}}}\n}}\n"
        )
        write_json(ws / f"literature/sources/{k}.json", {"citekey": k, **c})
        if idx == 2:
            # M2 mechanical fault: tagged unverified_needs_human_check
            ledger_entries[k] = {"verification_status": "unverified_needs_human_check", "source_file": None}
        else:
            ledger_entries[k] = {"verification_status": "verified_source", "source_file": f"literature/sources/{k}.json"}

    write_text(ws / "literature/references.bib", "\n".join(bib_lines))
    write_json(ws / "literature/citation_ledger.json", {"schema_version": "1.0", "entries": ledger_entries})

    # Experiment runs: 1 real canonical run + 1 synthetic run (M4)
    rid = cfg["run_id"]
    synth_id = f"{rid}_mock"
    write_json(
        ws / f"experiments/runs/{rid}/metrics.json",
        {
            "run_id": rid,
            "is_synthetic": False,
            "metrics": {
                "primary_score": cfg["acc_true"],
                "secondary_metric": cfg["clean_tp"],
                cfg["s2_metric_name"]: cfg["s2_true_int"],
            },
        },
    )
    write_json(
        ws / f"experiments/runs/{rid}/run_manifest.json",
        {"run_id": rid, "status": "completed", "is_synthetic": False, "git_commit": "abc1234", "git_dirty": False},
    )
    write_json(
        ws / f"experiments/runs/{synth_id}/metrics.json",
        {"run_id": synth_id, "is_synthetic": True, "metrics": {"ablation_score": 81.5}},
    )
    write_json(
        ws / f"experiments/runs/{synth_id}/run_manifest.json",
        {"run_id": synth_id, "status": "completed", "is_synthetic": True, "git_commit": "abc1234", "git_dirty": False},
    )
    write_json(
        ws / "experiments/provenance_index.json",
        {
            "schema_version": "1.0",
            "runs": {
                rid: {
                    "origin": "po_exp_code",
                    "status": "canonical",
                    "source_path": f"experiments/runs/{rid}/metrics.json",
                    "is_synthetic": False,
                    "user_attested_non_synthetic": False,
                },
                synth_id: {
                    "origin": "po_exp_code",
                    "status": "canonical",
                    "source_path": f"experiments/runs/{synth_id}/metrics.json",
                    "is_synthetic": True,
                    "user_attested_non_synthetic": False,
                },
            },
        },
    )

    # Flawed PNG figure (S5)
    fig_path = ws / "visuals/figures/fig_results.png"
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    render_flawed_figure(fig_path, seed)
    write_text(
        ws / "visuals/manifest.md",
        "# Visuals Manifest\n\nVISUAL_AUDIT: PENDING\n\n* `visuals/figures/fig_results.png` — Main comparison bar chart.\n",
    )

    # Manuscript sections embedding M1..M5 and S1..S5 + clean controls
    # Clean controls:
    #   C1: cite_keys[0] accurately summarized
    #   C2: clean_tp metric accurately reported under <!-- run:rid -->
    #   C3: defined parameter alpha_base = 0.5
    #   C4: anonymous submission header
    c0_key, c1_key, c2_key = cite_keys
    md_intro = (
        f"# Introduction {{#sec:intro}}\n\n"
        f"Recent systems [@{c0_key}] demonstrate strong baseline efficiency (clean control C1). "
        f"Additional background is discussed in [@{c2_key}] (M2 unverified) and [@{cfg['ghost_cite']}] (M1 missing).\n\n"
        f"{cfg['s1_distortion']}\n\n"
        f"We introduce {cfg['s4_acronym']} using a base weighting factor $\\alpha_{{\\text{{base}}}} = 0.5$ "
        f"combined with the adaptive score $S(x) = \\alpha_{{\\text{{base}}}} \\cdot x + {cfg['s4_symbol']} \\cdot R(x)$.\n"
    )
    md_results = (
        f"# Experimental Results {{#sec:results}}\n\n"
        f"<!-- run:{rid} -->\n"
        f"Evaluated across {cfg['s2_fake_int']} settings, our system attains {cfg['acc_fake']:.1f}% primary score "
        f"and {cfg['clean_tp']:.2f} secondary metric (see Figure 1 at `visuals/figures/fig_results.png`).\n\n"
        f"<!-- run:{synth_id} -->\n"
        f"Our supplementary check reaches 81.5% (see also `experiments/dry_run/mock/metrics.json`).\n\n"
        f"{cfg['s3_overclaim']}\n"
    )
    # Remove literal "(M1 missing)" / "(M2 unverified)" / "(clean control C1)" tags so critics don't see hints!
    md_intro = md_intro.replace(" (clean control C1)", "").replace(" (M2 unverified)", "").replace(" (M1 missing)", "")

    write_text(ws / "manuscript/sections/01_intro.md", md_intro)
    write_text(ws / "manuscript/sections/02_results.md", md_results)

    # Submission .tex with M5 double-blind leak
    write_text(
        ws / "submission/sections/01_intro.tex",
        f"\\section{{Introduction}}\\label{{sec:intro}}\n\n"
        f"Recent systems \\citep{{{c0_key}}} demonstrate strong baseline efficiency. "
        f"Additional background is discussed in \\citep{{{c2_key}}} and \\citep{{{cfg['ghost_cite']}}}.\n\n"
        f"% Local build note: {cfg['leak_str']}\n"
        f"We use $\\alpha_{{\\text{{base}}}} = 0.5$ and {cfg['s4_acronym']}.\n",
    )
    write_text(
        ws / "submission/sections/02_results.tex",
        f"\\section{{Experimental Results}}\\label{{sec:results}}\n\n"
        f"Evaluated across {cfg['s2_fake_int']} settings, our system attains {cfg['acc_fake']:.1f}\\% primary score "
        f"and {cfg['clean_tp']:.2f} secondary metric.\n\n"
        f"Our supplementary check reaches 81.5\\%.\n",
    )
    write_text(
        ws / "submission/main.tex",
        "\\documentclass{article}\n\\begin{document}\n\\input{sections/01_intro}\n\\input{sections/02_results}\n\\end{document}\n",
    )

    return {
        "seed": seed,
        "domain": cfg["domain"],
        "workspace": str(ws),
        "defects": {
            "M1": {"type": "mechanical", "desc": f"Missing citation {cfg['ghost_cite']}", "keywords": [cfg["ghost_cite"]]},
            "M2": {"type": "mechanical", "desc": f"Unverified citation {c2_key}", "keywords": [c2_key, "unverified"]},
            "M3": {"type": "mechanical", "desc": f"Decimal mismatch {cfg['acc_fake']} vs {cfg['acc_true']}", "keywords": [str(cfg["acc_fake"]), str(cfg["acc_true"])]},
            "M4": {"type": "mechanical", "desc": f"Synthetic run {synth_id} / dry_run leak", "keywords": [synth_id, "is_synthetic", "dry_run"]},
            "M5": {"type": "mechanical", "desc": f"Double-blind leak {cfg['leak_str']}", "keywords": [cfg["leak_str"], "anonymity", "github.com", "/Users/", "/home/"]},
            "S1": {"type": "semantic", "desc": f"Citation distortion of {cfg['s1_cite']}", "keywords": [cfg["s1_cite"], "distort", "contradict", "opposite", "inaccura", "misrepres", "false", "claim"]},
            "S2": {"type": "semantic", "desc": f"Integer falsification {cfg['s2_fake_int']} vs {cfg['s2_true_int']}", "keywords": [str(cfg["s2_fake_int"]), str(cfg["s2_true_int"]), cfg["s2_metric_name"]]},
            "S3": {"type": "semantic", "desc": "Missing ablation / overclaim / prose deanonymization", "keywords": ["ablation", "overclaim", "generaliz", "deanonym", "Munich", "ETH", "Seattle", "anonym"]},
            "S4": {"type": "semantic", "desc": f"Undefined symbol {cfg['s4_symbol']} or acronym {cfg['s4_acronym']}", "keywords": [cfg["s4_acronym"], "evict", "drift", "cap", "undefined", "acronym", "symbol", "notation"]},
            "S5": {"type": "semantic", "desc": "Visual legibility flaws in fig_results.png", "keywords": ["overlap", "tick", "legend", "tiny", "small", "font", "red", "green", "unit", "legib", "fig_results"]},
        },
        "clean_controls": {
            "C1": f"Accurate citation {c0_key}",
            "C2": f"Accurate metric {cfg['clean_tp']}",
            "C3": "Defined parameter alpha_base",
        },
    }


def eval_deterministic(ws: Path, po_tools: Path, gt: dict[str, Any]) -> dict[str, Any]:
    """Run real po_tools.py review-preflight and format-verify and map hits to M1..M5 and S1..S5."""
    pre = subprocess.run([sys.executable, str(po_tools), "review-preflight", "--workspace", str(ws)], capture_output=True, text=True, check=False)
    fmt = subprocess.run([sys.executable, str(po_tools), "format-verify", "--workspace", str(ws)], capture_output=True, text=True, check=False)
    pre_json = json.loads(pre.stdout) if pre.stdout.strip() else {}
    fmt_json = json.loads(fmt.stdout) if fmt.stdout.strip() else {}
    all_issues = " | ".join(b.get("issue", "") for b in (pre_json.get("blockers", []) + fmt_json.get("blockers", [])))

    detected: dict[str, bool] = {}
    for did, info in gt["defects"].items():
        if did == "M1":
            detected[did] = info["keywords"][0] in all_issues
        elif did == "M2":
            detected[did] = (info["keywords"][0] in all_issues) and ("unverified" in all_issues)
        elif did == "M3":
            detected[did] = info["keywords"][0] in all_issues
        elif did == "M4":
            detected[did] = ("is_synthetic" in all_issues) or ("dry_run" in all_issues)
        elif did == "M5":
            detected[did] = any(b.get("category") == "anonymity" for b in fmt_json.get("blockers", []))
        else:
            # Semantic flaws S1..S5: check whether any blocker specifically flags the semantic defect
            detected[did] = False

    # Check false positives on clean controls (e.g. flagging C1 cite or C2 metric)
    cfg = DOMAINS[gt["seed"]]
    c0_key = list(cfg["cites"].keys())[0]
    clean_fp = 0
    if c0_key in all_issues:
        clean_fp += 1
    if str(cfg["clean_tp"]) in all_issues:
        clean_fp += 1

    return {
        "preflight_rc": pre.returncode,
        "format_rc": fmt.returncode,
        "preflight_blockers": pre_json.get("blockers", []),
        "format_blockers": fmt_json.get("blockers", []),
        "detected": detected,
        "clean_fp": clean_fp,
    }


def score_critic_outputs(det: dict[str, Any], critic_data: dict[str, Any], gt: dict[str, Any], ro_mutations: int) -> dict[str, Any]:
    """Score live read-only critic outputs transparently against ground-truth M1..M5 and S1..S5."""
    cfg = DOMAINS[gt["seed"]]
    texts = {k: str(v) for k, v in critic_data.items()}
    combined_low = "\n".join(texts.values()).lower()

    def hit(role: str | None, checks: list[str], require_all: bool = False) -> bool:
        hay = texts.get(role, "").lower() if role else combined_low
        if require_all:
            return all(c.lower() in hay for c in checks)
        return any(c.lower() in hay for c in checks)

    critic_det = {
        "M1": hit("po-citation-auditor", [cfg["ghost_cite"]]) or hit(None, [cfg["ghost_cite"]]),
        "M2": hit("po-citation-auditor", [list(cfg["cites"].keys())[2], "unverified"], require_all=True),
        "M3": hit("po-evidence-auditor", [str(cfg["acc_fake"])]) and hit("po-evidence-auditor", [str(cfg["acc_true"])]),
        "M4": hit("po-evidence-auditor", ["is_synthetic", "dry_run", f"{cfg['run_id']}_mock"]),
        "M5": hit(None, [cfg["leak_str"].lower(), "github.com", "/users/", "/home/", "anonymity", "deanonym"]),
        "S1": hit("po-citation-auditor", [cfg["s1_cite"]]) and hit("po-citation-auditor", ["contradict", "opposite", "distort", "misrepres", "false", "inaccura", "1.8%", "drop", "does not", "without accessing", "20%"]),
        "S2": hit("po-evidence-auditor", [str(cfg["s2_fake_int"])]) and hit("po-evidence-auditor", [str(cfg["s2_true_int"])]),
        "S3": hit("po-peer-reviewer", ["ablation", "overclaim", "generaliz", "munich", "eth", "seattle", "deanonym"]),
        "S4": hit("po-clarity-reader", [cfg["s4_acronym"].lower(), "evict", "drift", "omega", "undefined", "not defined", "never defined"]),
        "S5": hit("po-visual-format-critic", ["overlap", "tick", "legend", "tiny", "small", "font", "red", "green", "legib", "unreadable", "unit"]),
    }

    det_map = det["detected"]
    hybrid_map = {k: (det_map[k] or critic_det[k]) for k in det_map}

    mech_ids = ["M1", "M2", "M3", "M4", "M5"]
    sem_ids = ["S1", "S2", "S3", "S4", "S5"]

    def rec(m: dict[str, bool], ids: list[str]) -> float:
        return round(sum(1 for k in ids if m[k]) / len(ids) * 100.0, 2)

    # Estimate tokens (~1.3 tokens per whitespace word)
    token_counts = {role: int(round(len(txt.split()) * 1.3)) for role, txt in texts.items()}
    max_tokens = max(token_counts.values()) if token_counts else 0

    # Check clean control false positives in critic outputs
    c0_key = list(cfg["cites"].keys())[0]
    clean_fp = det["clean_fp"]
    # Flag FP only if citation auditor explicitly blames c0_key as missing/unverified or evidence auditor flags clean_tp as mismatched
    cit_txt = texts.get("po-citation-auditor", "").lower()
    ev_txt = texts.get("po-evidence-auditor", "").lower()
    if f"{c0_key} missing" in cit_txt or f"{c0_key} is unverified" in cit_txt:
        clean_fp += 1
    if f"{cfg['clean_tp']} does not match" in ev_txt or f"{cfg['clean_tp']} mismatch" in ev_txt:
        clean_fp += 1

    return {
        "seed": gt["seed"],
        "domain": gt["domain"],
        "det_mech_recall": rec(det_map, mech_ids),
        "det_sem_recall": rec(det_map, sem_ids),
        "det_total_recall": rec(det_map, mech_ids + sem_ids),
        "critic_mech_recall": rec(critic_det, mech_ids),
        "critic_sem_recall": rec(critic_det, sem_ids),
        "critic_total_recall": rec(critic_det, mech_ids + sem_ids),
        "hybrid_mech_recall": rec(hybrid_map, mech_ids),
        "hybrid_sem_recall": rec(hybrid_map, sem_ids),
        "hybrid_total_recall": rec(hybrid_map, mech_ids + sem_ids),
        "clean_control_fp": clean_fp,
        "readonly_mutations": ro_mutations,
        "critics_completed": len(texts),
        "max_critic_tokens": max_tokens,
        "critic_tokens": token_counts,
        "per_defect_det": det_map,
        "per_defect_critic": critic_det,
        "per_defect_hybrid": hybrid_map,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["generate", "deterministic", "score"], required=True)
    ap.add_argument("--fixtures-root", type=Path, required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--po-tools", type=Path)
    ap.add_argument("--out-dir", type=Path)
    ap.add_argument("--run-id", default="exp04_hybrid_s42")
    ap.add_argument("--critic-outputs", type=Path)
    ap.add_argument("--ro-mutations", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.mode == "generate":
        seeds = [42] if args.dry_run else [42, 43, 44]
        gt_all = {}
        for s in seeds:
            gt_all[str(s)] = generate_fixture(args.fixtures_root, s)
        write_json(args.fixtures_root / "exp04_ground_truth.json", gt_all)
        print(f"[exp04] Generated {len(seeds)} seeded fixtures in {args.fixtures_root}")
        return 0

    gt_all = json.loads((args.fixtures_root / "exp04_ground_truth.json").read_text(encoding="utf-8"))
    gt = gt_all[str(args.seed)]
    ws = Path(gt["workspace"])

    if args.mode == "deterministic":
        assert args.po_tools and args.out_dir
        det = eval_deterministic(ws, args.po_tools.resolve(), gt)
        write_json(args.out_dir / "det_result.json", det)
        if args.dry_run:
            # Dry-run writes synthetic mock metrics.json strictly in dry_run/
            mock_critics = {
                "po-peer-reviewer": "Dry run mock review",
                "po-evidence-auditor": "Dry run mock audit",
                "po-citation-auditor": "Dry run mock cite audit",
                "po-visual-format-critic": "Dry run mock visual audit",
                "po-clarity-reader": "Dry run mock clarity audit",
            }
            metrics = score_critic_outputs(det, mock_critics, gt, ro_mutations=0)
            payload = {"run_id": args.run_id, "is_synthetic": True, "metrics": metrics}
            tmp_m = args.out_dir / "metrics.json.tmp"
            tmp_m.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            os.replace(tmp_m, args.out_dir / "metrics.json")
        print(
            f"[exp04] Deterministic B4 s{args.seed}: "
            f"mech={sum(det['detected'][k] for k in ['M1','M2','M3','M4','M5'])}/5, "
            f"sem={sum(det['detected'][k] for k in ['S1','S2','S3','S4','S5'])}/5"
        )
        return 0

    if args.mode == "score":
        assert args.out_dir and args.critic_outputs
        det = json.loads((args.out_dir / "det_result.json").read_text(encoding="utf-8"))
        critics = json.loads(args.critic_outputs.read_text(encoding="utf-8"))
        metrics = score_critic_outputs(det, critics, gt, ro_mutations=args.ro_mutations)
        payload = {"run_id": args.run_id, "is_synthetic": False, "metrics": metrics}
        tmp_m = args.out_dir / "metrics.json.tmp"
        tmp_m.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp_m, args.out_dir / "metrics.json")
        print(
            f"[exp04] Scored s{args.seed}: det_mech={metrics['det_mech_recall']}%, "
            f"det_sem={metrics['det_sem_recall']}%, critic_sem={metrics['critic_sem_recall']}%, "
            f"hybrid={metrics['hybrid_total_recall']}%, max_tok={metrics['max_critic_tokens']}"
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
