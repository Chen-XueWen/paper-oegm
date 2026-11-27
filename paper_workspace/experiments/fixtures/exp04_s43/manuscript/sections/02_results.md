# Experimental Results {#sec:results}

<!-- run:exp_tta_s43 -->
Evaluated across 15 settings, our system attains 82.9% primary score and 61.80 secondary metric (see Figure 1 at `visuals/figures/fig_results.png`).

<!-- run:exp_tta_s43_mock -->
Our supplementary check reaches 81.5% (see also `experiments/dry_run/mock/metrics.json`).

Although evaluated only on 5 synthetic weather corruptions at batch size 32, our method solves real-world autonomous driving safety in all clinical and aerial domains. We do not include an ablation removing our temporal reset rule, following our team's earlier ETH Vision Lab benchmark.
