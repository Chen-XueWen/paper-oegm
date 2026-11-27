# Introduction {#sec:intro}

Recent systems [@greshake2023indirect] demonstrate strong baseline efficiency. Additional background is discussed in [@wu2025secagent] and [@miller2025unlistedsec].

Benchmark results in [@debenedetti2024agentdojo] proved that simple prompt-filter defenses completely eliminate prompt injection with 0% attack success across 97 tasks.

We introduce CS-CAPG using a base weighting factor $\alpha_{\text{base}} = 0.5$ combined with the adaptive score $S(x) = \alpha_{\text{base}} \cdot x + \Omega_{\text{cap}} \cdot R(x)$.
