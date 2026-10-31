# ING-Net revision — referee comments 3 and 10

Project memory for Claude Code. Read this first in every session.

## What this project is

Revision of the manuscript *Higher-Order Statistics in Simulation-Based Inference for Non-Gaussian
Stochastic Gravitational-Wave Backgrounds* (ING-Net; referee report DT18456, received 2026-09-27).
The original codebase, trained networks, LIGO data and results live in `/root/SGWB1/` on the server.
This project holds the revision analysis that answers referee comment 3 (per-segment versus
accumulated sensitivity) and comment 10 (non-Gaussian benchmark), the draft response, and the draft
manuscript text. Treat `/root/SGWB1/` as read-only source material: never edit it in place, copy what
you need, and write every output under this project.

## Current state (2026-10-30)

- A synthetic test (`synthetic/`) settled the memo's open question: the per-segment kurtosis gain
  does not survive combining segments under any of three rules — linear stacking, product of
  per-segment likelihoods (the option-(b) construction), or the Drasco–Flanagan full-data mixture
  likelihood — except for ξ ≲ 1e-4. Gain over the power-only baseline falls below 0.1 dex within
  2–7 min at ξ = 1e-2 and 1.1 h (stacked) / 3.3 h (product) at ξ = 1e-3; the full-data likelihood keeps
  0.2 dex at 11 h and 0.04 dex at 4.6 d for ξ = 1e-3, and 0.49 dex at 4.6 d for ξ = 1e-4.
  The gain is a loud-event effect: it exists only while events at the detection limit have per-detector
  SNR ρ_burst ≳ 2–3 (manuscript Eq. 12).
- On Gaussian noise the Drasco–Flanagan statistic is 0.33–0.39 dex deeper than ING-Net per segment.
- Decision taken on that basis: resolve comment 3 by option (a) now (statement + new Sec. V F with the
  three-rule analysis); run option (b) on the real networks as a real-noise confirmation with the
  expectation stated in advance, not as the decider; answer comment 10 with the Drasco–Flanagan
  implementation and concede the Gaussian-noise comparison; reposition ING-Net as a per-segment
  non-Gaussian inference module (joint (Ω, ξ) posterior, trained on real noise, per-detector veto).
- Full reasoning, numbers and draft text: `docs/report_2026-10-30_accumulation_test.md` and
  `docs/response_and_manuscript_drafts.md`. Bracketed numbers in the drafts are synthetic and are to be
  replaced by real-noise values once option (b) has run.

## Layout

```
CLAUDE.md                       this file
synthetic/stacking_test.py      synthetic three-rule accumulation test (signal model of the paper)
synthetic/lin_rerun.py          linear-stacking limits with analytic directions (values used in tables)
synthetic/make_figure.py        merges res_*.json + lin_*.json -> results/ (tables, figure)
synthetic/res_*.json, lin_*.json  raw outputs of the 2026-10-30 run
synthetic/results/              stacking_table.csv, stacking_results_merged.json, figure .png/.pdf
real/option_b_real.py           option (b) on the trained networks; five adapter functions to fill
real/results/                   (to be created) option_b_results.json and figures
docs/                           report, drafts, the Oct-30 memo (PDF)
manuscript/                     manuscript draft of 2026-10-31 (PDF)
```

## Next tasks, in order

1. Map `/root/SGWB1/`: find the evaluation-noise loader (Sec. II C split: last 25 %, 8 s gap, 16 s trim,
   robust unit-variance whitening), the injector (antenna-pattern injection, Eq. 11 calibration), the
   feature extractor (Eqs. 7–8 plus any transform the networks were trained on), the trained posteriors
   (sbi MAF, seeds 1400–1402, ING 4-D and Trad 2-D, reference stretch of O3a/O3b/O4a), and the rev2
   results (15-stretch Table II, Table V calibration). Record the paths and function names here.
2. Fill the five adapter functions at the top of `real/option_b_real.py`; `python3 real/option_b_real.py
   --selftest` must still pass; then run on real evaluation noise (N ≤ 246), then `--synthetic` for the
   1.1–11 h stacks. Expected (state before looking): gain < 0.1 dex within 16 min at ξ = 1e-2; about
   0.3 dex at 16 min and 0.1 dex at 3 h at ξ = 1e-3. Criterion: Δ_comb ≥ 0.1 dex at the longest stack.
   Watch the coverage output: a product of N posteriors amplifies per-segment calibration error.
3. Replace the bracketed synthetic numbers in `docs/response_and_manuscript_drafts.md` with the
   real-noise values; keep the synthetic three-rule figure as the manuscript's new figure (it covers
   durations the real noise cannot).
4. Reconcile the manuscript's amplitude axis: Table II (log10 Ω ≈ −7.3 to −7.6) versus Table V after
   the comment-2 calibration (−4.4 to −4.9). One calibrated axis everywhere; the comparison with the LVK
   O3 isotropic limit Ω ≤ 5.8e-9 uses it (per-segment limits ≈ 3.4 dex above).
5. Apply the manuscript fixes listed under "Manuscript inconsistencies" below; fill placeholders
   (seed scatter [X], [Y]; Tables III, IV, VI; Fig. 7).
6. Optional, only if time allows: a per-detector glitch component in the mixture likelihood so the
   Drasco–Flanagan benchmark can be run on real noise (comment 10, full answer).

## Key numbers to keep straight

| Quantity | Value | Source |
| --- | --- | --- |
| Per-segment gain ING − Trad, real noise, rev2 (15 stretches) | +0.50 ± 0.03 dex at ξ = 1e-3; +0.23 ± 0.02 at 1e-2; none at ξ ≥ 0.1 | memo Sec. 3 |
| Same, synthetic, N = 1 | +0.63 and +0.29 dex (c_w = 1.94 here vs 1.73 in the paper) | synthetic/results |
| Single-event SNR at the rev2 limits | ρ_burst ≈ 15 (12–22) at ξ = 1e-3; ≈ 3.9 (3.5–6.0) at 1e-2 | manuscript Sec. V C |
| Gain < 0.1 dex after (stacked / product / full-data) | ξ = 1e-2: 2–7 min / 2–7 min / 20 min; ξ = 1e-3: 1.1 h / 3.3 h / 2–4 d; ξ = 1e-4: > 4.6 d for all | synthetic/results |
| D&F − ING per segment, Gaussian noise | 0.33 dex (ξ = 1e-2), 0.39 dex (1e-3) | synthetic/results |
| Second-order scaling check | CC limit ∝ N^−0.49…−0.51 per decade; ξ = 1 gains within ±0.03 dex | synthetic/results |
| Detection convention | 0.3 % false alarm per stack (99.7 % quantile on noise-only), 50 % detection | manuscript Sec. V B |

## Manuscript inconsistencies to fix (a referee will flag them on the second round)

- Abstract, Sec. V B, Sec. VII still quote 0.66 dex / factor 4.6; use the rev2 numbers everywhere.
- Table II caption says 5 seeds (1400–1404); text says three (1400–1402).
- Sec. II D cites "Edgeworth expansion (Eq. 3)"; it is Eq. (4).
- Sec. VI C: ρ_ev ≈ 11.3 contradicts Sec. V C (ρ_burst 15 and 3.9) and Sec. V C's own warning; rewrite with Eq. (12).
- Sec. VI C (i): "frequentist coverage validated on null data (Table III)" — Table III is not a coverage test; point to the P-P test of Sec. IV A.
- Sec. VI B (segment length): "stacking … could further improve sensitivity" — stacking favours the second-order baseline; rewrite.
- Sec. VI D: "extending the observational horizon", Gμ range — condition on per-segment / ξ ≲ 1e-4 or cut.
- Sec. I: "spectral methods dilute sparse bursts" — soften; dilution is repaid by T_obs^1/2.
- Eq. (5): c_w = 1.73 matches no standard Hann form (periodic/half-sample Hann gives 35/18 = 1.94); state the discrete window.

## How to run

```
cd synthetic && python3 stacking_test.py --xi 0.01 --tag _a --out res_a.json          # ~30 min, one core
cd synthetic && python3 stacking_test.py --xi 0.001,0.0001,1.0 --tag _b --out res_b.json
cd synthetic && python3 stacking_test.py --xi 0.0001 --grid=-5.6,-4.4,0.1 --tag _c --out res_c.json
cd synthetic && python3 lin_rerun.py --xi 0.01,1.0 --out lin_a.json && python3 lin_rerun.py --xi 0.001,0.0001 --out lin_b.json
cd synthetic && python3 make_figure.py                                              # writes results/
python3 real/option_b_real.py --selftest                                            # must print "selftest OK"
python3 real/option_b_real.py [--synthetic] --out real/results/option_b_results.json
```
Dependencies: numpy, scipy, scikit-learn, matplotlib; the real run also needs torch and sbi as in `/root/SGWB1`.

## Conventions

- Report limits as log10 of the per-sample signal variance σ_s² in `synthetic/` (= Ω σ_1² in the paper)
  and as log10 Ω on the paper's calibrated axis in `real/`; say which one every time.
- Gains Δ = Trad − ING in dex; positive means ING deeper. Threshold 0.3 % per stack, 50 % detection.
- State expectations before running a test, and keep negative results in the record.
- Sources for the literature claims: Drasco & Flanagan 2003 (PRD 67, 082003; factor 1–3 in Ω, ML beats
  cross-correlation from ξ ~ 1e-3 for N = 1e9 samples, max ≈ 2 near ξ ~ 1e-4); Lawrence et al. 2023
  (PRD 107, 103026; ξ ≈ 1e-3 Gaussian mixture, beats continuous cross-correlation); Smith & Thrane 2018
  (PRX 8, 021019; about one day vs about 40 months); LVK O3 isotropic (PRD 104, 022004; Ω ≤ 5.8e-9 flat).
