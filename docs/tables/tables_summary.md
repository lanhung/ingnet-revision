# Regenerated manuscript tables (calibrated amplitude axis) — 2026-10-31

Source: `docs/source_tables/outputs_rev1/` (copies of `/root/SGWB1/.workspace_rev2/outputs_rev1/`). Script: `real/make_tables.py`.
All limits are log10 Ω_limit per 4 s segment on the Eq. (11) calibrated axis (σ1 per stretch). Δ = Trad − ING-Net in dex.

**Amplitude axis.** The old Table II/III values (log10 Ω ≈ −7.3 to −7.6) were produced by the paper-v1 code, whose calibration constant S_code = √(2∫S_gw/P_n df) carries an extra factor √(2·980 Hz) ≈ 44 relative to the Eq. (11) σ1 = √(∫S_gw/P_n df / 980 Hz) (rev1 change R2); for the same injected variance, log10 Ω_new = log10 Ω_old + 2 log10(44.3) = log10 Ω_old + 3.29. The regenerated tables below are all on the new axis, as is Table V, so one axis is used everywhere.

**Seed scatter** (per-cell std over seeds, 75 cells): ING-Net median 0.021, 90th percentile 0.09, max 0.17 dex; Trad median 0.020, 90th percentile 0.05, max 0.18 dex (diverged seeds excluded). Suggested [X] = 0.1, [Y] = 0.05 (90th percentiles), with the medians quoted alongside.

### Table II (regenerated): per-segment limits log10 Ω_limit on the calibrated axis, 15 stretches, glitch-augmented networks

Mean ± std over training seeds 1400–1402 (n = 3 unless stated; Trad seeds whose limit sat at the prior top are excluded: 03A 1401/1402, 03B 1402, 04A2 1401). Δ = Trad − ING-Net in dex, positive = ING-Net deeper. 50 % detection at the 99.7 % CFAR threshold, 4 s segments.

| Run | Stretch | ξ | ING-Net | Trad | Δ |
|---|---|---|---|---|---|
| O3a | 03A | 0.001 | -4.71 ± 0.06 | -3.90 (n=1) | +0.82 |
| O3a | 03A2 | 0.001 | -4.70 ± 0.01 | -4.24 ± 0.05 | +0.46 |
| O3a | 03A3 | 0.001 | -4.68 ± 0.09 | -4.21 ± 0.03 | +0.48 |
| O3a | 03A4 | 0.001 | -4.76 ± 0.05 | -4.27 ± 0.12 | +0.49 |
| O3a | 03A5 | 0.001 | -4.76 ± 0.07 | -4.28 ± 0.02 | +0.48 |
| O3b | 03B | 0.001 | -4.70 ± 0.11 | -4.15 ± 0.18 (n=2) | +0.55 |
| O3b | 03B2 | 0.001 | -4.76 ± 0.05 | -4.32 ± 0.01 | +0.43 |
| O3b | 03B3 | 0.001 | -4.64 ± 0.12 | -4.21 ± 0.04 | +0.43 |
| O3b | 03B4 | 0.001 | -4.57 ± 0.15 | -4.27 ± 0.06 | +0.30 |
| O3b | 03B5 | 0.001 | -4.75 ± 0.07 | -4.26 ± 0.04 | +0.48 |
| O4a | 04A | 0.001 | -4.78 ± 0.08 | -4.13 ± 0.11 | +0.65 |
| O4a | 04A2 | 0.001 | -5.11 ± 0.06 | -4.61 ± 0.00 (n=2) | +0.50 |
| O4a | 04A3 | 0.001 | -4.91 ± 0.00 | -4.40 ± 0.11 | +0.51 |
| O4a | 04A4 | 0.001 | -5.00 ± 0.02 | -4.56 ± 0.02 | +0.43 |
| O4a | 04A5 | 0.001 | -4.98 ± 0.09 | -4.43 ± 0.11 | +0.55 |
| O3a | 03A | 0.01 | -4.82 ± 0.03 | -4.48 (n=1) | +0.35 |
| O3a | 03A2 | 0.01 | -4.86 ± 0.03 | -4.65 ± 0.02 | +0.21 |
| O3a | 03A3 | 0.01 | -4.86 ± 0.03 | -4.65 ± 0.02 | +0.20 |
| O3a | 03A4 | 0.01 | -4.92 ± 0.02 | -4.71 ± 0.03 | +0.21 |
| O3a | 03A5 | 0.01 | -4.95 ± 0.00 | -4.69 ± 0.01 | +0.26 |
| O3b | 03B | 0.01 | -4.86 ± 0.02 | -4.61 ± 0.00 (n=2) | +0.26 |
| O3b | 03B2 | 0.01 | -4.95 ± 0.02 | -4.75 ± 0.05 | +0.20 |
| O3b | 03B3 | 0.01 | -4.85 ± 0.07 | -4.62 ± 0.00 | +0.23 |
| O3b | 03B4 | 0.01 | -4.73 ± 0.17 | -4.68 ± 0.03 | +0.06 |
| O3b | 03B5 | 0.01 | -4.95 ± 0.02 | -4.69 ± 0.01 | +0.26 |
| O4a | 04A | 0.01 | -4.91 ± 0.02 | -4.63 ± 0.01 | +0.28 |
| O4a | 04A2 | 0.01 | -5.25 ± 0.01 | -5.01 ± 0.01 (n=2) | +0.24 |
| O4a | 04A3 | 0.01 | -5.06 ± 0.03 | -4.82 ± 0.03 | +0.23 |
| O4a | 04A4 | 0.01 | -5.17 ± 0.02 | -4.97 ± 0.01 | +0.20 |
| O4a | 04A5 | 0.01 | -5.15 ± 0.02 | -4.87 ± 0.02 | +0.28 |
| O3a | 03A | 0.1 | -4.60 ± 0.02 | -4.49 (n=1) | +0.11 |
| O3a | 03A2 | 0.1 | -4.68 ± 0.02 | -4.66 ± 0.02 | +0.01 |
| O3a | 03A3 | 0.1 | -4.66 ± 0.01 | -4.66 ± 0.02 | +0.00 |
| O3a | 03A4 | 0.1 | -4.70 ± 0.00 | -4.72 ± 0.04 | -0.02 |
| O3a | 03A5 | 0.1 | -4.74 ± 0.02 | -4.71 ± 0.01 | +0.03 |
| O3b | 03B | 0.1 | -4.64 ± 0.02 | -4.62 ± 0.01 (n=2) | +0.02 |
| O3b | 03B2 | 0.1 | -4.75 ± 0.03 | -4.76 ± 0.04 | -0.01 |
| O3b | 03B3 | 0.1 | -4.66 ± 0.06 | -4.63 ± 0.00 | +0.03 |
| O3b | 03B4 | 0.1 | -4.59 ± 0.11 | -4.68 ± 0.01 | -0.09 |
| O3b | 03B5 | 0.1 | -4.76 ± 0.01 | -4.69 ± 0.01 | +0.06 |
| O4a | 04A | 0.1 | -4.67 ± 0.00 | -4.64 ± 0.01 | +0.04 |
| O4a | 04A2 | 0.1 | -5.05 ± 0.02 | -5.02 ± 0.02 (n=2) | +0.03 |
| O4a | 04A3 | 0.1 | -4.83 ± 0.01 | -4.84 ± 0.03 | -0.01 |
| O4a | 04A4 | 0.1 | -4.97 ± 0.01 | -4.98 ± 0.02 | -0.01 |
| O4a | 04A5 | 0.1 | -4.93 ± 0.00 | -4.88 ± 0.03 | +0.05 |
| O3a | 03A | 0.5 | -4.56 ± 0.01 | -4.48 (n=1) | +0.08 |
| O3a | 03A2 | 0.5 | -4.64 ± 0.02 | -4.66 ± 0.01 | -0.02 |
| O3a | 03A3 | 0.5 | -4.62 ± 0.02 | -4.65 ± 0.03 | -0.03 |
| O3a | 03A4 | 0.5 | -4.67 ± 0.01 | -4.71 ± 0.04 | -0.04 |
| O3a | 03A5 | 0.5 | -4.70 ± 0.02 | -4.71 ± 0.01 | -0.01 |
| O3b | 03B | 0.5 | -4.59 ± 0.02 | -4.63 ± 0.01 (n=2) | -0.03 |
| O3b | 03B2 | 0.5 | -4.71 ± 0.04 | -4.76 ± 0.05 | -0.05 |
| O3b | 03B3 | 0.5 | -4.62 ± 0.05 | -4.64 ± 0.01 | -0.01 |
| O3b | 03B4 | 0.5 | -4.56 ± 0.12 | -4.69 ± 0.02 | -0.13 |
| O3b | 03B5 | 0.5 | -4.73 ± 0.00 | -4.70 ± 0.02 | +0.03 |
| O4a | 04A | 0.5 | -4.62 ± 0.01 | -4.64 ± 0.01 | -0.02 |
| O4a | 04A2 | 0.5 | -5.01 ± 0.02 | -5.02 ± 0.02 (n=2) | -0.01 |
| O4a | 04A3 | 0.5 | -4.80 ± 0.02 | -4.85 ± 0.03 | -0.05 |
| O4a | 04A4 | 0.5 | -4.94 ± 0.02 | -4.98 ± 0.01 | -0.04 |
| O4a | 04A5 | 0.5 | -4.88 ± 0.00 | -4.88 ± 0.02 | -0.00 |
| O3a | 03A | 1.0 | -4.55 ± 0.02 | -4.49 (n=1) | +0.06 |
| O3a | 03A2 | 1.0 | -4.64 ± 0.02 | -4.66 ± 0.01 | -0.03 |
| O3a | 03A3 | 1.0 | -4.61 ± 0.03 | -4.66 ± 0.02 | -0.05 |
| O3a | 03A4 | 1.0 | -4.66 ± 0.00 | -4.72 ± 0.03 | -0.06 |
| O3a | 03A5 | 1.0 | -4.69 ± 0.02 | -4.70 ± 0.02 | -0.01 |
| O3b | 03B | 1.0 | -4.59 ± 0.02 | -4.62 ± 0.01 (n=2) | -0.03 |
| O3b | 03B2 | 1.0 | -4.71 ± 0.04 | -4.77 ± 0.04 | -0.05 |
| O3b | 03B3 | 1.0 | -4.62 ± 0.06 | -4.63 ± 0.01 | -0.01 |
| O3b | 03B4 | 1.0 | -4.56 ± 0.12 | -4.69 ± 0.02 | -0.14 |
| O3b | 03B5 | 1.0 | -4.73 ± 0.01 | -4.69 ± 0.01 | +0.04 |
| O4a | 04A | 1.0 | -4.62 ± 0.01 | -4.64 ± 0.02 | -0.01 |
| O4a | 04A2 | 1.0 | -5.02 ± 0.03 | -5.02 ± 0.02 (n=2) | -0.00 |
| O4a | 04A3 | 1.0 | -4.79 ± 0.02 | -4.85 ± 0.03 | -0.06 |
| O4a | 04A4 | 1.0 | -4.93 ± 0.02 | -4.98 ± 0.01 | -0.05 |
| O4a | 04A5 | 1.0 | -4.88 ± 0.01 | -4.88 ± 0.03 | +0.00 |

**Aggregate over the 15 stretches** (mean of the per-stretch Δ ± standard error; this is the rule behind the memo's +0.50 ± 0.03 and +0.23 ± 0.02):

| ξ | Δ mean ± SE | Δ median | Δ range | stretches with Δ > 0 | ING mean (range) | Trad mean |
|---|---|---|---|---|---|---|
| 0.001 | +0.504 ± 0.030 | +0.484 | +0.30 … +0.82 | 15/15 | -4.79 (-5.11 … -4.57) | -4.28 |
| 0.01 | +0.231 ± 0.016 | +0.235 | +0.06 … +0.35 | 15/15 | -4.95 (-5.25 … -4.73) | -4.72 |
| 0.1 | +0.016 ± 0.012 | +0.015 | -0.09 … +0.11 | 10/15 | -4.75 (-5.05 … -4.59) | -4.73 |
| 0.5 | -0.022 ± 0.011 | -0.021 | -0.13 … +0.08 | 2/15 | -4.71 (-5.01 … -4.56) | -4.73 |
| 1.0 | -0.027 ± 0.012 | -0.026 | -0.14 … +0.06 | 3/15 | -4.71 (-5.02 … -4.55) | -4.73 |

### Table III (regenerated): 95 % upper limits on log10 Ω from noise-only segments, calibrated axis

200 non-overlapping 4 s segments of the evaluation part of each stretch; mean over seeds of the per-seed values (diverged Trad seeds excluded). Δ_paired = mean per-segment (Trad − ING-Net).

| Run | Stretch | ING-Net mean | ING-Net std | Trad mean | Trad std | Δ_paired |
|---|---|---|---|---|---|---|
| O3a | 03A | -4.74 | 0.26 | -4.71 | 0.23 | +0.157 (n=1) |
| O3a | 03A2 | -4.76 | 0.21 | -4.71 | 0.18 | +0.048 |
| O3a | 03A3 | -4.75 | 0.27 | -4.72 | 0.25 | +0.028 |
| O3a | 03A4 | -4.80 | 0.23 | -4.63 | 0.25 | +0.170 |
| O3a | 03A5 | -4.81 | 0.28 | -4.59 | 0.21 | +0.221 |
| O3b | 03B | -4.68 | 0.25 | -4.43 | 0.28 | +0.271 (n=2) |
| O3b | 03B2 | -4.81 | 0.23 | -4.70 | 0.22 | +0.108 |
| O3b | 03B3 | -4.77 | 0.25 | -4.64 | 0.26 | +0.128 |
| O3b | 03B4 | -4.68 | 0.26 | -4.67 | 0.22 | +0.011 |
| O3b | 03B5 | -4.75 | 0.25 | -4.62 | 0.23 | +0.134 |
| O4a | 04A | -4.68 | 0.25 | -4.45 | 0.30 | +0.231 |
| O4a | 04A2 | -4.93 | 0.25 | -4.85 | 0.25 | -0.049 (n=2) |
| O4a | 04A3 | -4.75 | 0.28 | -4.71 | 0.23 | +0.038 |
| O4a | 04A4 | -4.70 | 0.32 | -4.94 | 0.21 | -0.241 |
| O4a | 04A5 | -4.60 | 0.29 | -4.77 | 0.22 | -0.175 |

Over the 15 stretches: Δ_paired mean +0.072 dex, range -0.241 … +0.271; |Δ_paired| ≤ 0.27 dex; ING-Net's null upper limit is deeper than Trad's on 12 of 15 stretches and shallower on 3 (all three in O4a). Per-stretch offsets of either sign up to about 0.25 dex, with no systematic excess of ING-Net over the power-only baseline, is the statement to make: the kurtosis channel does not add false signals on noise-only data. (The old text's |Δ_paired| ≤ 0.09 dex referred to three stretches on the old axis.)

### Table IV (regenerated): frequency-resolved baseline on the three reference stretches (glitch-augmented runs, seeds 1400–1402)

Δ_FR = Trad − Trad-FR (positive: the 64-D frequency-resolved input improves on the scalar power-only baseline); Δ_FR→ING = Trad-FR − ING-Net (positive: ING-Net deeper than Trad-FR). All 9 Trad-FR runs converged; the Trad column excludes the diverged seeds.

| Run | ξ | ING-Net | Trad | Trad-FR | Δ_FR | Trad-FR − ING-Net |
|---|---|---|---|---|---|---|
| O3a | 0.001 | -4.71 ± 0.06 | -3.90 (n=1) | -3.94 ± 0.14 | +0.05 | +0.77 |
| O3a | 0.01 | -4.82 ± 0.03 | -4.48 (n=1) | -4.49 ± 0.08 | +0.02 | +0.33 |
| O3a | 0.1 | -4.60 ± 0.02 | -4.49 (n=1) | -4.51 ± 0.06 | +0.02 | +0.09 |
| O3a | 0.5 | -4.56 ± 0.01 | -4.48 (n=1) | -4.51 ± 0.06 | +0.02 | +0.05 |
| O3a | 1.0 | -4.55 ± 0.02 | -4.49 (n=1) | -4.51 ± 0.06 | +0.02 | +0.04 |
| O3b | 0.001 | -4.70 ± 0.11 | -4.15 ± 0.18 (n=2) | -4.05 ± 0.11 | -0.09 | +0.65 |
| O3b | 0.01 | -4.86 ± 0.02 | -4.61 ± 0.00 (n=2) | -4.59 ± 0.01 | -0.02 | +0.28 |
| O3b | 0.1 | -4.64 ± 0.02 | -4.62 ± 0.01 (n=2) | -4.62 ± 0.01 | -0.00 | +0.02 |
| O3b | 0.5 | -4.59 ± 0.02 | -4.63 ± 0.01 (n=2) | -4.62 ± 0.01 | -0.01 | -0.02 |
| O3b | 1.0 | -4.59 ± 0.02 | -4.62 ± 0.01 (n=2) | -4.62 ± 0.01 | -0.01 | -0.03 |
| O4a | 0.001 | -4.78 ± 0.08 | -4.13 ± 0.11 | -4.06 ± 0.14 | -0.07 | +0.73 |
| O4a | 0.01 | -4.91 ± 0.02 | -4.63 ± 0.01 | -4.61 ± 0.01 | -0.02 | +0.29 |
| O4a | 0.1 | -4.67 ± 0.00 | -4.64 ± 0.01 | -4.63 ± 0.02 | -0.00 | +0.04 |
| O4a | 0.5 | -4.62 ± 0.01 | -4.64 ± 0.01 | -4.64 ± 0.03 | -0.01 | -0.01 |
| O4a | 1.0 | -4.62 ± 0.01 | -4.64 ± 0.02 | -4.63 ± 0.02 | -0.00 | -0.01 |

Δ_FR over the 15 cells: mean -0.007 dex, range -0.09 … +0.05. At ξ ≥ 0.1 the two second-order baselines agree to within 0.02 dex; at ξ = 1e-3 Trad-FR is shallower than ING-Net by +0.71 dex on average.

### Capacity scan (Table IV footnote): MAF hidden units × transforms, three reference stretches, seeds 1400–1401 (mean over the three stretches; the primary row has seeds 1400–1402)

Glitch-augmented training throughout. The power-only baselines do not close the gap to ING-Net with 5× the hidden units or twice the transforms: Trad and Trad-FR move by ≤ 0.1 dex across the scan while Δ stays at +0.56 … +0.73 dex (ξ = 10⁻³) and +0.24 … +0.35 dex (ξ = 10⁻²).

| hidden × transforms | ING ξ=1e-3 | Trad | Trad-FR | Δ | ING ξ=1e-2 | Trad | Trad-FR | Δ | ING ξ=1 | Trad | Trad-FR | Δ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 × 5 (primary) | -4.73 | -4.06 | -4.09 | +0.67 | -4.87 | -4.57 | -4.58 | +0.29 | -4.59 | -4.58 | -4.60 | +0.01 |
| 50 × 10 | -4.73 | -4.17 | -4.06 | +0.56 | -4.84 | -4.60 | -4.56 | +0.24 | -4.61 | -4.61 | -4.57 | -0.01 |
| 128 × 5 | -4.80 | -4.07 | -4.09 | +0.73 | -4.91 | -4.57 | -4.58 | +0.34 | -4.60 | -4.57 | -4.60 | +0.02 |
| 128 × 10 | -4.80 | -4.11 | -4.08 | +0.69 | -4.89 | -4.54 | -4.56 | +0.35 | -4.60 | -4.55 | -4.58 | +0.05 |
| 256 × 5 | -4.80 | -4.16 | -4.06 | +0.64 | -4.89 | -4.59 | -4.57 | +0.30 | -4.63 | -4.60 | -4.58 | +0.03 |
| 256 × 10 | -4.81 | -4.14 | -4.13 | +0.67 | -4.91 | -4.58 | -4.60 | +0.33 | -4.61 | -4.59 | -4.61 | +0.03 |
| 256 × 10, lr 2e-4 | -4.76 | -4.13 | -4.07 | +0.63 | -4.89 | -4.57 | -4.57 | +0.32 | -4.60 | -4.58 | -4.58 | +0.02 |

### Table V (verified from veto_diag.json): identical vs antenna injection, coincidence veto (max κ > 1 and min κ < 0.1 max κ) on both pipelines

Median over seeds 1400–1402 of the per-seed 20-round means; Δ = median of the per-seed (Trad − ING-Net). Tags rev1_identical / rev1_antenna (no glitch augmentation). One O3b Trad seed (1401) diverged under antenna injection and is excluded.

| ξ | Run | Ident. ING-Net | Ident. Trad | Ident. Δ | Ant. ING-Net | Ant. Trad | Ant. Δ |
|---|---|---|---|---|---|---|---|
| 0.001 | O3a | -4.96 | -4.49 | +0.49 | -4.43 | -4.03 | +0.45 |
| 0.001 | O3b | -4.95 | -4.57 | +0.43 | -4.62 | -4.07 (n=2) | +0.48 |
| 0.001 | O4a | -4.98 | -4.51 | +0.49 | -4.61 | -4.06 | +0.55 |
| 0.01 | O3a | -4.85 | -4.69 | +0.16 | -4.80 | -4.58 | +0.23 |
| 0.01 | O3b | -4.87 | -4.73 | +0.13 | -4.86 | -4.60 (n=2) | +0.25 |
| 0.01 | O4a | -4.88 | -4.69 | +0.19 | -4.90 | -4.64 | +0.28 |

### Table VI: GPS start times of the 15 analysed stretches (4096 s each; from run_meta.json input_files)

|  | O3a | O3b | O4a |
|---|---|---|---|
| Reference | 1238919012 | 1264612209 | 1369205931 |
| 2 | 1242570539 | 1262256273 | 1379214337 |
| 3 | 1243410158 | 1261517932 | 1371147035 |
| 4 | 1252676208 | 1256691641 | 1379475656 |
| 5 | 1248371921 | 1256783794 | 1374698967 |

_Fig. 7 written_
