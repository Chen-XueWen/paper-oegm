# Introduction {#sec:intro}

Recent systems [@wang2021tent] demonstrate strong baseline efficiency. Additional background is discussed in [@hendrycks2019robustness] and [@patel2025ghosttta].

Entropy minimization in [@wang2021tent] requires full source training data access during adaptation and increased ImageNet-C error to 82.0%.

We introduce CF-VTTA using a base weighting factor $\alpha_{\text{base}} = 0.5$ combined with the adaptive score $S(x) = \alpha_{\text{base}} \cdot x + \tau_{\text{drift}} \cdot R(x)$.
