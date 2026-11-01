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

## Current state (2026-10-31)

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
- 2026-10-31: task 1 done. `/root/SGWB1/` is mapped in the section "Map of `/root/SGWB1/`" below: the
  live code is `.workspace_rev2/rev1/utils_rev1.py`, the 15-stretch networks are the `rev1_glitchaug` +
  `rev1x_glitchaug` runs (not the un-augmented `*_antenna` ones), the feature order in the code is
  (C_HL, log1p|κ_H1|, log1p|κ_L1|, P) — differs from the manuscript and from the adapter docstring — and
  the batched grid `log_prob` call was verified on the server (0.14 s for 246 segments × 2201 grid points).
- 2026-10-31, later: tasks 2–5 done. Option (b) ran on all 15 stretches (`real/results/option_b_*.json`,
  summary `real/results/option_b_summary.md`, figure `option_b_gain_vs_duration.pdf`). Real noise, 15 stretches,
  Δ at N = 246 (16 min): ξ = 1e-3 +0.19 ± 0.01 dex (linear stack, 15/15 positive) and +0.13 ± 0.03 (product of
  posteriors, 13/15) — criterion met; ξ = 1e-2 −0.02 ± 0.01 / −0.08 ± 0.04 — gone within 1–2 min. The closure is
  faster than the synthetic prediction (0.28–0.35 at 16 min for ξ = 1e-3) because the per-segment gain is smaller on
  real noise (0.51 vs 0.63). The linear stack of the trained posteriors on synthetic noise (+0.12 at 1.1 h, 0.00 at
  3.3 h) agrees with the pure synthetic test within 0.05 dex. Two findings about the product of posteriors: its
  coverage collapses with N (50 % interval covers 0.49 → 0.38 → 0.28 at N = 1, 10, 100; same for Trad) and as a
  detection statistic it is 0.1–0.16 dex shallower than the linear stack of the same posteriors for N ≥ 30 on real
  noise and saturates (threshold = noise median) at N ≥ 1e3 on synthetic noise — those rows are unusable, greyed in the
  figure. Grid resolution ruled out (`real/results/gridcheck_03A_seed1400.json`). Drafts, tables and the itemised
  manuscript fixes are updated: `docs/response_and_manuscript_drafts.md`, `docs/manuscript_fixes_2026-10-31.md`,
  `docs/tables/` (`real/make_tables.py` from `docs/source_tables/outputs_rev1/`). Pinned Table II aggregation: mean
  over 15 stretches of (mean Trad − mean ING over seeds, diverged excluded) ± SE = +0.504 ± 0.030 (1e-3), +0.231 ± 0.016
  (1e-2). The amplitude axis is reconciled (one calibrated axis; v1 values were on S_code = √(2∫), 3.29 dex off, and a
  different signal model, so they are replaced, not shifted). Open: task 6 (not run), Figs. 3/8 regeneration from
  `probe_figdata/`, and the manuscript LaTeX is not on the server (fixes are delivered as text).

## Layout

```
CLAUDE.md                       this file
synthetic/stacking_test.py      synthetic three-rule accumulation test (signal model of the paper)
synthetic/lin_rerun.py          linear-stacking limits with analytic directions (values used in tables)
synthetic/make_figure.py        merges res_*.json + lin_*.json -> results/ (tables, figure)
synthetic/res_*.json, lin_*.json  raw outputs of the 2026-10-30 run
synthetic/results/              stacking_table.csv, stacking_results_merged.json, figure .png/.pdf
real/option_b_real.py           option (b) on the trained networks (adapters filled 2026-10-31; runs on the server)
real/analyze_option_b.py        aggregates real/results/option_b_*.json -> summary .md/.json, gain/coverage/rules tables, figure
real/gridcheck_option_b.py      grid-resolution check of the product rule (server); output real/results/gridcheck_03A_seed1400.json
real/make_tables.py             regenerates Tables II–VI, capacity scan, Fig. 7 into docs/tables/ from docs/source_tables/
real/results/                   option_b_{O3a,O3b,O4a}_{ref,x}.json/.log (ref = reference stretch + synthetic extension,
                                x = the four rev1x stretches), option_b_summary.md/.json, option_b_gain_table/coverage/rules.csv,
                                option_b_gain_vs_duration.png/.pdf
docs/                           report, drafts (numbers final), manuscript_fixes_2026-10-31.md, tables/, source_tables/, the Oct-30 memo (PDF)
manuscript/                     manuscript draft of 2026-10-31 (PDF)
```

## Next tasks, in order

1. Done 2026-10-31. Map `/root/SGWB1/` — evaluation-noise loader, injector and Eq. 11 calibration,
   feature extractor and the transforms the networks were trained on, trained posteriors, rev2 results
   (15-stretch Table II, Table V) — recorded with paths, function names and line numbers in the section
   "Map of `/root/SGWB1/`" below, together with the adapter recipe for task 2.
2. Done 2026-10-31. Adapters filled, selftest passes locally and on the server, runs complete on all 15
   stretches (real noise N ≤ 246, synthetic extension to 1e4 on the reference stretches). Expectation stated
   before the run: gain < 0.1 dex within 16 min at ξ = 1e-2; about 0.3 dex at 16 min at ξ = 1e-3. Outcome:
   ξ = 1e-2 as expected (gone at 40 s–2 min); ξ = 1e-3 +0.13 (product) / +0.19 (linear) at 16 min — criterion
   met, closure faster than synthetic. Coverage of the product collapses with N (see "Current state").
3. Done 2026-10-31: real-noise numbers in `docs/response_and_manuscript_drafts.md`; synthetic figure stays the
   manuscript figure, `real/results/option_b_gain_vs_duration.pdf` is the confirmation (Table [new] drafted in
   `docs/manuscript_fixes_2026-10-31.md` Sec. 3).
4. Done 2026-10-31: one calibrated axis (σ1 of Eq. 11); v1 S_code = √(2∫) differs by 3.29 dex and the v1 signal
   model differs too, so v1 numbers are replaced. Per-segment ING limits at ξ = 1e-2 are 3.0–3.5 dex (mean 3.3)
   above the LVK O3 limit log10 Ω = −8.24. See `docs/manuscript_fixes_2026-10-31.md` Sec. 0.
5. Done 2026-10-31: itemised in `docs/manuscript_fixes_2026-10-31.md` (Sec. 2, items 1–16) with the regenerated
   tables in `docs/tables/` ([X] = 0.1, [Y] = 0.05 dex seed scatter; Tables III, IV, VI, capacity scan, Fig. 7).
   Also found: the training-time glitch augmentation (p = 0.1, single-detector sine-Gaussian/blip, SNR 5–3000)
   is not described in the draft and must be added to Secs. III B and VI A.
6. Optional, not run: a per-detector glitch component in the mixture likelihood so the Drasco–Flanagan
   benchmark can be run on real noise (comment 10, full answer). The response concedes the Gaussian-noise
   comparison and names this as the next step.
7. Open: regenerate Figs. 3 and 8 from `probe_figdata/` on the calibrated axis; the manuscript LaTeX of the
   2026-10-31 draft is not on the server (only the PDF), so the fixes are delivered as text.

## Map of `/root/SGWB1/` (task 1, done 2026-10-31)

Server `ssh -p 58009 root@u3ssh.casdao.com`, 2× RTX 4090, Python `/root/miniconda3/envs/sgwbpe/bin/python`
(torch 2.5.1+cu124, sbi 0.25.0, numpy 2.4.2, scipy 1.17.1, gwpy 4.0.1). Everything below is read-only source.

The live workspace is `/root/SGWB1/.workspace_rev2/` — the cwd of every script; `rev1/` holds the code, `data`
and `data_rev1x` are symlinks into `../.workspace/`, `outputs_rev1/` holds the results. `.workspace/rev1/` is the
pre-rev2 copy (its `utils_rev1.py` still normalises by the block std) and `.workspace/{utils,train,test}.py` is the
paper-v1 code: use neither. Import pattern, as in `rev1/eval_rev1.py`: `cd .workspace_rev2`,
`sys.path.insert(0, "rev1")`, `import utils_rev1 as U`, then `U.CFG.update(run_meta["config"])` before anything
else — `U.CFG` is a module-level dict that the loader and simulator read (`data_dir`, `edge_s`, `band_lo/hi`,
`split_*`, `tau_s`, `mode`, `include_fr`); the rev1x stretches need `data_dir = ./data_rev1x`. A GPU must be
visible: `U.device` is cuda and the pickled posteriors live on `cuda:0` (`CUDA_VISIBLE_DEVICES=""` fails inside
`log_prob`).

| What | Where (paths under `.workspace_rev2/`) |
| --- | --- |
| Raw data | `data/{O3a,O3b,O4a}_{H1,L1}_<GPS>.pt` (reference stretches 1238919012 / 1264612209 / 1369205931) and `data_rev1x/` (the 12 further stretches): float32, 16 777 216 samples at 4096 Hz = 4096 s, fetched by `rev1/fetch_gwosc.py` under the rule of 2026-10-03. The sha256 of each file is in every `run_meta.json["dataset_meta"]["sha256"]`. |
| Evaluation-noise loader | `rev1/utils_rev1.py`: `load_raw` → `preprocess_np` (gwpy resample to 2048 Hz, high-pass 15 Hz) → `prepare_dataset(ds)` (l. 190): data gate, `calibration_sigma1`, split at 75 % with an 8 s gap, `whiten_block` on each part separately (l. 128: median-Welch PSD of the block, band 20–1000 Hz, 16 s trimmed at each end, divided by 1.4826·MAD — the rev2 change made by `patch_rev2.py`). Returns `{"train": (h1, l1), "eval": (h1, l1), "sigma1", "s_code_old", "meta"}`, float32 CUDA tensors; eval = 984 s = 2 015 232 samples = 246 non-overlapping 4 s segments of 8192 samples. `ds` is an entry of `U.CFG["datasets"]` (`{"name", "file_h1", "file_l1"}`). About 6 s per stretch. `Simulator.draw_noise` draws random, overlapping start times and subtracts each segment's mean; for non-overlapping segments slice the eval stream yourself and subtract the mean. |
| Injector | `U.Simulator(h1_bg, l1_bg, sigma1)`; `Simulator.draw_signal(log_omega, log_xi)` (l. 320) returns `(s_h, s_l, counts)`, each (b, 8192): Poisson start times over `n_pos = 8192 + n_tau − 1`, `n_tau = 8` (τ = 3.906 ms), Hann window with mean w² = 1 (`burst_window`), per-event variance (Ω/ξ)σ1² after band-limiting, a sky direction and ψ per event from `antenna_factors_torch` (H1/L1 arm vectors, `ANTENNA_POWER_COMP = 1/√0.4`), exact Gaussian draw with the H–L covariance, `bandlimit` to 20–1000 Hz; `CFG["mode"]` is "antenna" or "identical". Randomness comes from torch's global RNG (`U.set_seed`), not from a numpy Generator. `Simulator.simulate(theta)` = `draw_noise` + `draw_signal` + features; θ[:, 0] ≤ −15 means noise-only (CFAR uses [−20, −1]). |
| Eq. 11 calibration | `calibration_sigma1(pre)` (l. 147): σ1² = ∫₂₀¹⁰⁰⁰ S_gw(f; Ω = 1)/P_n(f) df / 980 Hz with S_gw = 3H0²/(10π²f³), H0 = 2.1927e-18 s⁻¹, Welch PSD of the whole pre-whitened H1 stream. Stored in `model_*.pt["sigma1"]` and `run_meta["dataset_meta"]["sigma1"]` (03A: 37.63). `s_code_old = √(2∫)` is the paper-v1 constant kept for comparison (ratio ≈ √f_s ≈ 44); task 4 starts from this docstring and row R2 of `rev1/CHANGES_rev1.md`. |
| Feature extractor | `U.Simulator.compute_features(h1, l1)` (static, l. 265) → (b, 4) in the order **(C_HL, log1p\|κ_H1\|, log1p\|κ_L1\|, log10(var_H1·var_L1))** — not the manuscript's (C_HL, P, κ_H1, κ_L1) and not the order in the adapter docstring of `real/option_b_real.py`. Kurtosis is stored as log1p\|κ\| (`veto_diag.py` undoes it with expm1). ING-Net = columns `[0, 1, 2, 3]`, Trad = `[0, 3]`, Trad-FR = `[4:68]` from `compute_fr_features` (only when `include_fr`). Nothing else is scaled outside the network: sbi's `posterior_nn` z-scores x inside the net (`estimator.embedding_net[0]` is `Standardize`; 03A seed 1400 ING: mean [−0.248, 1.938, 1.965, 0.789], std [0.337, 2.406, 2.417, 1.213]) and θ in the flow's first `PointwiseAffineTransform` (shift [2.24, 1.73], scale [0.49, 1.15]). Feed raw features and raw (log10 Ω, log10 ξ). |
| Trained posteriors | `outputs_rev1/<tag>/<DS>_seed<seed>_<timestamp>/models/model_{ai,tr,fr}_<DS>.pt`: a `torch.save` dict with `posterior` (sbi `DirectPosterior` over an `NFlowsFlow` MAF, 5 MADE blocks × 50 hidden, prior BoxUniform [−8, −1] × [−3, 0]), `sigma1`, `idx`, `seed`, `dataset`, `cfg`. Load with `eval_rev1.load_run(run)` → `(meta, name, {"ai": (posterior, idx), "tr": …, "fr": …})`, which also sets `U.CFG`, or with `torch.load(p, map_location=U.device, weights_only=False)`. Training code: `rev1/train_rev1.py` (`train_one`: NPE_C with `posterior_nn("maf")`); `rev1/train_b.py` is the same with `glitchaug_b.GlitchSimulator` on the training simulator only (single-detector sine-Gaussian or blip glitches, p = 0.1, SNR 5–3000). |
| Primary configuration | tags `rev1_glitchaug` (03A, 03B, 04A, with Trad-FR) and `rev1x_glitchaug` (03A2–5, 03B2–5, 04A2–5, no FR), seeds 1400–1402, configs `rev1/configs/rev1_glitchaug.json` and `rev1x_glitchaug.json`. These are the 15-stretch networks: aggregating their summaries with exclude_diverged = True gives Δ = +0.482 ± 0.021 dex at ξ = 1e-3 (14 stretches with two or more Trad seeds) and +0.223 ± 0.015 at 1e-2, i.e. the memo's +0.50 ± 0.03 / +0.23 ± 0.02; the un-augmented `rev1_antenna`/`rev1x_antenna` give +0.05 ± 0.16 / −0.28 ± 0.16 and are not the source. Every probe (`probe_figdata`, `probe_pp_local`, `probe_cfar99`, `probe_gspy`, `probe_spectral`) uses the glitchaug runs. Pin down the exact aggregation (mean or median, 14 or 15 stretches) when Table II is regenerated. |
| Diverged Trad seeds | limit pinned at the prior top (−1.0), listed in `outputs_rev1/diverged_*.csv`: `rev1_glitchaug` 03A seeds 1401 and 1402, 03B seed 1402; `rev1x_glitchaug` 04A2 seed 1401. No ING-Net run diverged. Skip these when loading Trad posteriors. |
| Other tags | `rev1_antenna`, `rev1x_antenna` (no augmentation); `rev1_identical` (mode = identical, the left half of Table V); `rev1_cap_{h50,h128,h256}_t{5,10}[_lr2e-4]` (capacity scan on the three reference stretches, seeds 1400–1401, rounds R19c/R19d; four recovered runs sit in `outputs_rev1_recovery_20261031_retry1/`). |
| log q(θ\|x) on a grid | verified on the server: `est = posterior.posterior_estimator; est.log_prob(theta[:, None, :].expand(-1, B, -1), condition=feats)` → (nθ, B); a 2201-point grid × 246 segments takes 0.14 s (ING) / 0.03 s (Trad) and agrees with `posterior.log_prob(grid, x=feats[j:j+1], norm_posterior=False)` per segment to within 4e-3 / 1e-2 in log-probability. Use `norm_posterior=False`: the leakage constant is per-x and cancels in the grid normalisation; the grid lies inside the prior box, so no masking is needed. Do not call `posterior.sample` — its unbounded rejection sampling hangs on 04A, which is why `U.sample_batch` exists. |
| Pipeline statistic | `U.detection_statistic` (mean log10 Ω of 200 flow samples, no truncation), `U.calibrate_cfar` (99.7 % quantile, n_calib = 10 000 random-start segments, N_eff ≈ 246, bootstrap in `cfar.json`), `U.find_limit` (bisection to 0.05 dex, 50 trials, 20 rounds in `rounds.npz`). |
| Per-run results | `results.csv` (per ξ: AI/Trad/TradFR mean ± std over 20 rounds, ρ_s, ρ_acc, ⟨N⟩), `rounds.npz`, `cfar.json`, `run_meta.json` (config, data sha256, σ1, s_code_old, code sha256, versions, noise fingerprints), `eval/eval_summary.json` (P-P all and ξ < 1e-2, null UL on 200 non-overlapping segments, recovery, corner), `veto_diag/veto_diag.json`. |
| Table II (15 stretches) | `outputs_rev1/summary_rev1_glitchaug.csv` + `summary_rev1x_glitchaug.csv`, written by `rev1/sweep_rev1.py --aggregate`: one row per (tag, ds, xi, exclude_diverged) with ai/tr/fr mean, std (ddof 1), n, `D_tr_minus_ai` and a Welch p. Per-stretch ING limits run from −4.57 to −5.11 at ξ = 1e-3 on the calibrated axis. |
| Table V | `outputs_rev1/veto_summary.csv`, written by `rev1/aggregate_veto.py` from each run's `veto_diag.json`: rows with `config = veto_K1.0_r0.1_PRIMARY` (the coincidence veto of `veto_diag.py`: max κ > 1 and min κ < 0.1·max κ, applied to every pipeline), tags `rev1_antenna` and `rev1_identical`, seeds 1400–1402. The CSV holds means while Table V quotes medians (03A antenna, ξ = 1e-3: CSV −4.458, table −4.43). Other (K, r) pairs are in `veto_summary_sensitivity.csv`. |
| Probes | `probe_cfar99.json` (99 % against 99.7 % thresholds), `probe_figdata/` (arrays for Figs. 3b, 4, 5; seed 1400), `probe_pp_local/` (P-P with ξ < 1e-2 selected on the posterior median, 15 stretches), `probe_gspy/` with `data_gspy/*.csv` (Gravity Spy cross-match), `probe_spectral/` (α = 2/3 spectrum shift), `probe_whiten_rev2.json` (P-median gate). |
| Evidence packages | `/root/staging_R19b/` (CSV/JSON/npz of all 99 runs plus summaries and probes, no weights), `staging_R19c_A/` (probe_spectral), `staging_R19d_retry1/` (capacity scan, 36 runs), `staging_R18/` (source copy), `staging_R19a/` (gspy, pp_local); tarballs next to them. |

Adapter recipe for task 2 (`real/option_b_real.py`), following from the above:

- `load_eval_noise(run, stretch_index)`: choose the stretch name (O3a → 03A, 03A2–5; O3b → 03B…; O4a → 04A…),
  `U.CFG.update(run_meta["config"])` from a glitchaug run of that stretch, `D = U.prepare_dataset(ds)`, return
  `torch.stack(D["eval"])` as (2, T) and keep `D["sigma1"]`; cut 246 non-overlapping 8192-sample segments and
  subtract each segment's mean.
- `inject`: `sim = U.Simulator(*D["eval"], D["sigma1"])`; `s_h, s_l, _ = sim.draw_signal(torch.full((B,), lo),
  torch.full((B,), lx))`; add to the segments. Seed with `U.set_seed`; the numpy `rng` argument does not reach
  the simulator.
- `features`: `U.Simulator.compute_features(h, l)` in the order above; Trad takes `[:, [0, 3]]`. Correct the
  adapter docstring's order or reorder consistently — the networks only see `idx` applied to the
  `compute_features` order.
- `load_posterior`: `model_ai_<DS>.pt` / `model_tr_<DS>.pt` of the glitchaug run for (stretch, seed), skipping
  the diverged Trad seeds.
- `log_prob_grid`: the batched estimator call above with the raw grid.

## Key numbers to keep straight

| Quantity | Value | Source |
| --- | --- | --- |
| Per-segment gain ING − Trad, real noise, rev2 (15 stretches) | +0.504 ± 0.030 dex at ξ = 1e-3 (median +0.48, range +0.30…+0.82, factor 3.2); +0.231 ± 0.016 at 1e-2; none at ξ ≥ 0.1 | docs/tables/table2_aggregate.json |
| Option (b), real noise, 15 stretches, N = 246 (16 min): Δ linear / product | ξ = 1e-3: +0.19 ± 0.01 / +0.13 ± 0.03; ξ = 1e-2: −0.02 ± 0.01 / −0.08 ± 0.04 | real/results/option_b_summary.md |
| Option (b), product-posterior coverage of the 50 % (90 %) interval, ING | 0.49 (0.90) at N = 1; 0.38 (0.78) at 10; 0.28 (0.47) at 100 — not a calibrated N-segment posterior | real/results/option_b_coverage.csv |
| Product rule − linear rule limit, same posteriors, real noise | +0.10 (N = 30), +0.15 (100), +0.16 (246) dex shallower for ING; saturated at N ≥ 1e3 on synthetic noise | real/results/option_b_rules.csv |
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
# on the server (copy real/ to /root/ingnet-revision/real; one GPU visible; see scratch/launch.sh there):
python real/option_b_real.py --runs O3a --stretches 0 --synthetic --out real/results/option_b_O3a_ref.json
python real/option_b_real.py --runs O3a --stretches 1,2,3,4 --out real/results/option_b_O3a_x.json   # --resume continues
python3 real/analyze_option_b.py                                                   # local: summary, tables, figure
python3 real/make_tables.py                                                        # local: docs/tables/ from docs/source_tables/
```
Dependencies: numpy, scipy, scikit-learn, matplotlib; the real run also needs torch and sbi as in `/root/SGWB1`.
Server jobs: launch with `setsid nohup … < /dev/null &` — two plain `nohup` runs were killed at local midnight
(16:00 UTC) on 2026-10-31 with no traceback; `--resume` picked them up. The six runs took 32–40 min each on two GPUs.

## Conventions

- Report limits as log10 of the per-sample signal variance σ_s² in `synthetic/` (= Ω σ_1² in the paper)
  and as log10 Ω on the paper's calibrated axis in `real/`; say which one every time.
- Gains Δ = Trad − ING in dex; positive means ING deeper. Threshold 0.3 % per stack, 50 % detection.
- State expectations before running a test, and keep negative results in the record.
- Sources for the literature claims: Drasco & Flanagan 2003 (PRD 67, 082003; factor 1–3 in Ω, ML beats
  cross-correlation from ξ ~ 1e-3 for N = 1e9 samples, max ≈ 2 near ξ ~ 1e-4); Lawrence et al. 2023
  (PRD 107, 103026; ξ ≈ 1e-3 Gaussian mixture, beats continuous cross-correlation); Smith & Thrane 2018
  (PRX 8, 021019; about one day vs about 40 months); LVK O3 isotropic (PRD 104, 022004; Ω ≤ 5.8e-9 flat).
