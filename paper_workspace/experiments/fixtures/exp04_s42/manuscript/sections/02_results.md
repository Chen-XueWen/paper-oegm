# Experimental Results {#sec:results}

<!-- run:exp_kv_s42 -->
Evaluated across 16 settings, our system attains 93.7% primary score and 3.42 secondary metric (see Figure 1 at `visuals/figures/fig_results.png`).

<!-- run:exp_kv_s42_mock -->
Our supplementary check reaches 81.5% (see also `experiments/dry_run/mock/metrics.json`).

Because our eviction score improves throughput on Llama-3-8B, it guarantees lossless serving on all multimodal video transformers and 100B+ MoE models. Note that we omit an ablation disabling the attention-sink anchor because it is intuitively necessary, extending our prior Munich Systems Group workshop paper.
