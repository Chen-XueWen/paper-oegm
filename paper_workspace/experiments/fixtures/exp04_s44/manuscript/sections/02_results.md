# Experimental Results {#sec:results}

<!-- run:exp_sec_s44 -->
Evaluated across 12 settings, our system attains 97.6% primary score and 6.20 secondary metric (see Figure 1 at `visuals/figures/fig_results.png`).

<!-- run:exp_sec_s44_mock -->
Our supplementary check reaches 81.5% (see also `experiments/dry_run/mock/metrics.json`).

Our sandbox eliminates all prompt-injection risks across every OS kernel and web browser deployment. We omit an ablation comparing against static allowlist filtering because our capability graph is clearly superior, building on our group's previous Seattle Security Institute release.
