# Introduction {#sec:intro}

Recent systems [@kwon2023vllm] demonstrate strong baseline efficiency. Additional background is discussed in [@xiao2024streaming] and [@chen2025phantomkv].

Prior heavy-hitter eviction [@zhang2023h2o] reported a 14.5% accuracy gain at 20% cache budget with zero degradation.

We introduce PKVE-M using a base weighting factor $\alpha_{\text{base}} = 0.5$ combined with the adaptive score $S(x) = \alpha_{\text{base}} \cdot x + \gamma_{\text{evict}} \cdot R(x)$.
