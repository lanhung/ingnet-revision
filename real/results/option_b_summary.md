# Option (b) on the trained networks — results

Inputs: option_b_O3a_ref.json, option_b_O3a_x.json, option_b_O3b_ref.json, option_b_O3b_x.json, option_b_O4a_ref.json, option_b_O4a_x.json; 15 stretches: 03A, 03A2, 03A3, 03A4, 03A5, 03B, 03B2, 03B3, 03B4, 03B5, 04A, 04A2, 04A3, 04A4, 04A5.
Expectation stated in advance: gain < 0.1 dex within 16 min at xi=1e-2; ~0.3 dex at 16 min and ~0.1 dex at 3 h at xi=1e-3. Criterion: Delta_comb >= 0.1 dex at the longest stack.
Networks: rev1_glitchaug / rev1x_glitchaug; feature order C_HL, log1p|kappa_H1|, log1p|kappa_L1|, log10(var_H1 var_L1) (utils_rev1.Simulator.compute_features); R = 2000 stacks per threshold and per detection estimate.

## Gain against stacked duration

Per-stretch Δ = mean over available Trad seeds − mean over ING-Net seeds (Table II rule; diverged Trad seeds skipped: 03A 1401/1402, 03B 1402, 04A2 1401); aggregate = mean ± standard error over stretches; "> 0" counts stretches with positive Δ. "synth." columns are the synthetic three-rule prediction of `synthetic/results/stacking_table.csv` interpolated in log N (product of per-segment likelihoods ↔ combined; linear stack ↔ linear). Rows marked "syn" use the real networks on synthetic whitened Gaussian noise (3 reference stretches).

| ξ | N | T | noise | n | Δ_comb (mean ± SE) | Δ_comb > 0 | synth. product | Δ_lin (mean ± SE) | Δ_lin > 0 | synth. linear | ING / Trad limit (comb.) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 1 | 4 s | real | 15 | +0.51 ± 0.04 | 15/15 | +0.63 | +0.51 ± 0.04 | 15/15 | +0.63 | -4.83 / -4.32 |
| 0.001 | 3 | 12 s | real | 15 | +0.41 ± 0.01 | 15/15 | +0.56 | +0.39 ± 0.02 | 15/15 | +0.63 | -5.38 / -4.97 |
| 0.001 | 10 | 40 s | real | 15 | +0.34 ± 0.02 | 15/15 | +0.50 | +0.35 ± 0.01 | 15/15 | +0.53 | -5.63 / -5.29 |
| 0.001 | 30 | 2 min | real | 15 | +0.29 ± 0.02 | 15/15 | +0.48 | +0.30 ± 0.01 | 15/15 | +0.45 | -5.79 / -5.50 |
| 0.001 | 100 | 7 min | real | 15 | +0.18 ± 0.04 | 14/15 | +0.39 | +0.24 ± 0.01 | 15/15 | +0.34 | -5.87 / -5.69 |
| 0.001 | 246 | 16 min | real | 15 | +0.13 ± 0.03 | 13/15 | +0.35 | +0.19 ± 0.01 | 15/15 | +0.28 | -6.00 / -5.87 |
| 0.001 | 1000 | 1.1 h | syn | 3 | +0.04 ± 0.26 | 2/3 | +0.20 | +0.12 ± 0.02 | 3/3 | +0.09 | -6.00 / -5.96 |
| 0.001 | 3000 | 3.3 h | syn | 3 | -0.09 ± 0.31 | 2/3 | +0.09 | +0.00 ± 0.01 | 1/3 | +0.08 | -6.03 / -6.12 |
| 0.001 | 10000 | 11.1 h | syn | 3 | +0.14 ± 0.30 | 2/3 | -0.07 | -0.01 ± 0.02 | 1/3 | +0.03 | -6.04 / -5.90 |
| 0.01 | 1 | 4 s | real | 15 | +0.22 ± 0.02 | 15/15 | +0.30 | +0.22 ± 0.02 | 15/15 | +0.29 | -4.97 / -4.75 |
| 0.01 | 3 | 12 s | real | 15 | +0.17 ± 0.01 | 15/15 | +0.23 | +0.17 ± 0.01 | 15/15 | +0.25 | -5.16 / -5.00 |
| 0.01 | 10 | 40 s | real | 15 | +0.07 ± 0.01 | 14/15 | +0.16 | +0.11 ± 0.01 | 15/15 | +0.14 | -5.33 / -5.25 |
| 0.01 | 30 | 2 min | real | 15 | -0.01 ± 0.01 | 5/15 | +0.08 | +0.04 ± 0.01 | 14/15 | +0.10 | -5.48 / -5.49 |
| 0.01 | 100 | 7 min | real | 15 | -0.05 ± 0.02 | 5/15 | +0.01 | +0.01 ± 0.01 | 7/15 | +0.02 | -5.66 / -5.71 |
| 0.01 | 246 | 16 min | real | 15 | -0.08 ± 0.04 | 4/15 | -0.04 | -0.02 ± 0.01 | 5/15 | +0.01 | -5.79 / -5.87 |
| 0.01 | 1000 | 1.1 h | syn | 3 | -0.08 ± 0.21 | 2/3 | -0.05 | -0.02 ± 0.03 | 1/3 | -0.01 | -5.88 / -5.97 |
| 0.01 | 3000 | 3.3 h | syn | 3 | -0.10 ± 0.24 | 2/3 | -0.13 | -0.01 ± 0.03 | 1/3 | +0.00 | -5.98 / -6.08 |
| 0.01 | 10000 | 11.1 h | syn | 3 | +0.15 ± 0.24 | 2/3 | -0.16 | +0.00 ± 0.02 | 1/3 | +0.00 | -6.02 / -5.87 |

## Headline

- ξ = 0.001, real noise, combined rule, longest stack N = 246 (16 min): Δ = +0.13 ± 0.03 dex over 15 stretches → criterion Δ ≥ 0.1 dex met.
- ξ = 0.001, real noise, linear rule, longest stack N = 246 (16 min): Δ = +0.19 ± 0.01 dex over 15 stretches → criterion Δ ≥ 0.1 dex met.
- ξ = 0.001, synthetic noise, combined rule, longest stack N = 10000 (11.1 h): Δ = +0.14 ± 0.30 dex over 3 stretches → criterion Δ ≥ 0.1 dex met. [product statistic saturated at this N, see "Product rule against linear rule": not a usable limit]
- ξ = 0.001, synthetic noise, linear rule, longest stack N = 10000 (11.1 h): Δ = -0.01 ± 0.02 dex over 3 stretches → criterion Δ ≥ 0.1 dex not met.
- ξ = 0.001, combined rule: mean Δ first falls below 0.1 dex at N = 1000 (1.1 h).
- ξ = 0.001, linear rule: mean Δ first falls below 0.1 dex at N = 3000 (3.3 h).
- ξ = 0.01, real noise, combined rule, longest stack N = 246 (16 min): Δ = -0.08 ± 0.04 dex over 15 stretches → criterion Δ ≥ 0.1 dex not met.
- ξ = 0.01, real noise, linear rule, longest stack N = 246 (16 min): Δ = -0.02 ± 0.01 dex over 15 stretches → criterion Δ ≥ 0.1 dex not met.
- ξ = 0.01, synthetic noise, combined rule, longest stack N = 10000 (11.1 h): Δ = +0.15 ± 0.24 dex over 3 stretches → criterion Δ ≥ 0.1 dex met. [product statistic saturated at this N, see "Product rule against linear rule": not a usable limit]
- ξ = 0.01, synthetic noise, linear rule, longest stack N = 10000 (11.1 h): Δ = +0.00 ± 0.02 dex over 3 stretches → criterion Δ ≥ 0.1 dex not met.
- ξ = 0.01, combined rule: mean Δ first falls below 0.1 dex at N = 10 (40 s).
- ξ = 0.01, linear rule: mean Δ first falls below 0.1 dex at N = 30 (2 min).

## Coverage of the combined posterior

Injections drawn from the prior into N real-noise segments; the combined posterior is the normalised product of the N per-segment posteriors on a 0.02 dex grid. "coverage of 50 % CI" = fraction of injections inside the central 50 % interval of the log10 Ω marginal (nominal 0.50), likewise 90 %; KS = Kolmogorov distance of the PIT values from uniform (critical value 1.36/√200 = 0.096 at 95 %); bias = median (posterior mean − truth), |bias| = median absolute, width = median posterior std, all in dex and for injections above log10 Ω = −7.5.

| network | N | runs | coverage of 50 % CI | coverage of 90 % CI | KS (median, max) | KS > crit. | bias | |bias| | width |
|---|---|---|---|---|---|---|---|---|---|
| ing | 1 | 45 | 0.49 [0.39, 0.57] | 0.90 [0.86, 0.94] | 0.068 (max 0.128) | 9/45 | -0.019 | 0.197 | 0.359 |
| ing | 10 | 45 | 0.38 [0.29, 0.54] | 0.78 [0.62, 0.87] | 0.127 (max 0.222) | 35/45 | -0.005 | 0.077 | 0.096 |
| ing | 100 | 45 | 0.28 [0.20, 0.41] | 0.47 [0.40, 0.65] | 0.268 (max 0.456) | 45/45 | -0.006 | 0.047 | 0.029 |
| ing | 1 (synthetic noise) | 9 | 0.48 [0.43, 0.50] | 0.90 [0.90, 0.91] | 0.053 (max 0.076) | 0/9 | -0.008 | 0.176 | 0.350 |
| trad | 1 | 41 | 0.51 [0.40, 0.57] | 0.89 [0.83, 0.93] | 0.055 (max 0.093) | 0/41 | -0.004 | 0.195 | 0.331 |
| trad | 10 | 41 | 0.46 [0.34, 0.56] | 0.82 [0.69, 0.90] | 0.107 (max 0.258) | 25/41 | -0.004 | 0.072 | 0.096 |
| trad | 100 | 41 | 0.30 [0.25, 0.41] | 0.52 [0.39, 0.77] | 0.306 (max 0.464) | 40/41 | -0.004 | 0.041 | 0.028 |
| trad | 1 (synthetic noise) | 6 | 0.53 [0.48, 0.57] | 0.92 [0.89, 0.93] | 0.055 (max 0.084) | 0/6 | -0.009 | 0.206 | 0.881 |

## Product rule against linear rule

Same posteriors, same noise stacks and injections, two detection statistics: the posterior mean of log10 Ω under the normalised product of the N per-segment posteriors ("product", the option-(b) construction, 0.1 dex grid) and the mean of the N per-segment posterior means ("linear"). Columns: mean over runs (stretch × seed) of limit(product) − limit(linear) in dex (positive: the product rule is shallower), and the noise-only gap 0.3 % threshold − median of each statistic. "saturated" marks N at which, for both networks, the noise-only product statistic has a gap below 0.05 dex or the product-rule limit is more than 0.2 dex shallower than the linear stack of the same posteriors: the product posterior of that many segments is dominated by the shared systematic shape of the learned posteriors raised to the power N rather than by the data, so its limits are not usable. The grid resolution is not the cause: on 03A seed 1400 the limits on a 0.02 dex grid equal those on the 0.1 dex grid to 0.00 dex at N = 30, 100, 246 (one case 0.05 dex; `real/results/gridcheck_03A_seed1400.json`).

| ξ | N | T | noise | net | runs | limit(product) − limit(linear) | SE | noise gap, product | noise gap, linear | saturated |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.001 | 1 | 4 s | real | ing | 45 | -0.00 | 0.02 | 1.02 | 1.02 |  |
| 0.001 | 1 | 4 s | real | trad | 41 | +0.00 | 0.03 | 1.10 | 1.10 |  |
| 0.001 | 3 | 12 s | real | ing | 45 | -0.02 | 0.01 | 0.86 | 0.48 |  |
| 0.001 | 3 | 12 s | real | trad | 41 | -0.01 | 0.01 | 0.97 | 0.51 |  |
| 0.001 | 10 | 40 s | real | ing | 45 | +0.04 | 0.01 | 0.65 | 0.23 |  |
| 0.001 | 10 | 40 s | real | trad | 41 | +0.03 | 0.01 | 0.89 | 0.24 |  |
| 0.001 | 30 | 2 min | real | ing | 45 | +0.10 | 0.02 | 0.37 | 0.11 |  |
| 0.001 | 30 | 2 min | real | trad | 41 | +0.09 | 0.02 | 0.69 | 0.12 |  |
| 0.001 | 100 | 7 min | real | ing | 45 | +0.15 | 0.03 | 0.37 | 0.07 |  |
| 0.001 | 100 | 7 min | real | trad | 41 | +0.10 | 0.02 | 0.36 | 0.07 |  |
| 0.001 | 246 | 16 min | real | ing | 45 | +0.16 | 0.03 | 0.26 | 0.04 |  |
| 0.001 | 246 | 16 min | real | trad | 41 | +0.12 | 0.03 | 0.20 | 0.04 |  |
| 0.001 | 1000 | 1.1 h | synthetic | ing | 9 | +0.31 | 0.10 | 0.04 | 0.02 | yes |
| 0.001 | 1000 | 1.1 h | synthetic | trad | 6 | +0.18 | 0.09 | 0.01 | 0.02 | yes |
| 0.001 | 3000 | 3.3 h | synthetic | ing | 9 | +0.41 | 0.11 | 0.13 | 0.01 | yes |
| 0.001 | 3000 | 3.3 h | synthetic | trad | 6 | +0.28 | 0.13 | 0.00 | 0.01 | yes |
| 0.001 | 10000 | 11.1 h | synthetic | ing | 9 | +0.64 | 0.13 | 0.13 | 0.01 | yes |
| 0.001 | 10000 | 11.1 h | synthetic | trad | 6 | +0.74 | 0.15 | 0.00 | 0.01 | yes |
| 0.01 | 1 | 4 s | real | ing | 45 | +0.00 | 0.00 | 1.05 | 1.05 |  |
| 0.01 | 1 | 4 s | real | trad | 41 | -0.00 | 0.00 | 1.06 | 1.06 |  |
| 0.01 | 3 | 12 s | real | ing | 45 | +0.02 | 0.00 | 0.87 | 0.47 |  |
| 0.01 | 3 | 12 s | real | trad | 41 | +0.01 | 0.00 | 0.97 | 0.51 |  |
| 0.01 | 10 | 40 s | real | ing | 45 | +0.05 | 0.01 | 0.64 | 0.22 |  |
| 0.01 | 10 | 40 s | real | trad | 41 | +0.01 | 0.01 | 0.88 | 0.24 |  |
| 0.01 | 30 | 2 min | real | ing | 45 | +0.09 | 0.01 | 0.38 | 0.11 |  |
| 0.01 | 30 | 2 min | real | trad | 41 | +0.04 | 0.01 | 0.68 | 0.12 |  |
| 0.01 | 100 | 7 min | real | ing | 45 | +0.09 | 0.02 | 0.37 | 0.06 |  |
| 0.01 | 100 | 7 min | real | trad | 41 | +0.04 | 0.01 | 0.35 | 0.07 |  |
| 0.01 | 246 | 16 min | real | ing | 45 | +0.14 | 0.03 | 0.26 | 0.04 |  |
| 0.01 | 246 | 16 min | real | trad | 41 | +0.07 | 0.02 | 0.21 | 0.04 |  |
| 0.01 | 1000 | 1.1 h | synthetic | ing | 9 | +0.30 | 0.10 | 0.04 | 0.02 | yes |
| 0.01 | 1000 | 1.1 h | synthetic | trad | 6 | +0.19 | 0.09 | 0.01 | 0.02 | yes |
| 0.01 | 3000 | 3.3 h | synthetic | ing | 9 | +0.43 | 0.12 | 0.14 | 0.01 | yes |
| 0.01 | 3000 | 3.3 h | synthetic | trad | 6 | +0.29 | 0.13 | 0.01 | 0.01 | yes |
| 0.01 | 10000 | 11.1 h | synthetic | ing | 9 | +0.62 | 0.16 | 0.13 | 0.01 | yes |
| 0.01 | 10000 | 11.1 h | synthetic | trad | 6 | +0.72 | 0.15 | 0.00 | 0.01 | yes |

_figure written: option_b_gain_vs_duration.png_
