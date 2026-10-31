# Referee comment 3 — accumulation test with nonlinear combination, and proposed revision

Oct 30, 2026 · @Vicky Chang

## Bottom line

The per-segment kurtosis gain does not survive accumulation, whichever way segments are combined, except for very sparse backgrounds (ξ ≲ 1e-4): I ran the memo's open question on synthetic data with the paper's signal model and the answer is the same for linear stacking, for a product of per-segment likelihoods (the option-(b) construction) and for the Drasco–Flanagan full-data likelihood.

- The gain is a loud-event effect. It is present only while single events at the detection limit have per-detector SNR ρ ≳ 2–3 (Eq. 12). Integration lowers the limit until that stops being true, and from then on the fourth cumulant adds nothing to the second.
- ξ = 1e-2: gain below 0.1 dex after 2–7 min for the 4-D summary under either rule, after 20 min for the full-data likelihood. ξ = 1e-3: below 0.1 dex after 1.1 h (stacked) or 3.3 h (product of likelihoods); the full-data likelihood keeps 0.2 dex at 11 h and 0.04 dex at 4.6 d. ξ = 1e-4: 0.17 dex (stacked), 0.28 dex (product) and 0.49 dex (full data) still survive at 4.6 d.
- Multiplying per-segment likelihoods of the summary vector is not a remedy: at most +0.1 dex over linear stacking at ξ = 1e-3 for about an hour, +0.3 dex at ξ = 1e-4 over days. Worse, a per-segment likelihood that is slightly mis-fitted loses 0.3–0.5 dex to linear stacking once multiplied over 10³–10⁵ segments; the real-data option (b) will meet exactly this.
- The analytic Drasco–Flanagan statistic is 0.33–0.39 dex deeper than the 4-D summary per segment on Gaussian noise, and 0.9–1.5 dex deeper at ξ = 1e-4 over hours. The summary discards within-burst H1–L1 coherence and time localisation; that, not the combination rule, is what limits long-duration sensitivity.

**Recommendation.** Resolve comment 3 by option (a) now, with the three-rule analysis as the new Sec. V F and the figure below; run option (b) as a real-noise calibration check with a pre-stated expectation, not as the decider; answer comment 10 with the Drasco–Flanagan implementation and concede that on Gaussian noise the analytic statistic is deeper per segment. Position ING-Net as the per-segment non-Gaussian inference module (duty-cycle posterior, short-time-scale detection, trained on real noise with the per-detector veto), and name a burst-coherent summary as the route to long-duration sparse-background searches. Draft text for all of this is in Sections 6 and 7.

## Assessment of the memo and of the manuscript as it stands

The memo's physics is right and its scaling test is reproducible, but its open question (does a nonlinear combination keep the gain over hours?) can be answered now, before any server run, and the manuscript still carries a dozen inconsistencies the referee will read as unfinished.

**The memo (Oct 30).** Section 2 is correct: the second-order channel improves as N^-1/2 and the kurtosis channel as N^-1/4, so the gap closes by 0.25 dex per decade of stacked data. Section 4 reproduces in my code at N = 1 (0.24 dex vs the memo's 0.22 at ξ = 1e-2, same antenna geometry γ\_HL(0) = -0.891, c\_F = 1.43). Two points I would change:

- The memo frames the loss as a property of linear stacking and leaves open whether multiplying per-segment likelihoods rescues it. It does not, for the 4-D summary (Section 4 below): the gain is a loud-event effect, and once the detectable amplitude puts single events below per-detector SNR ≈ 1–2, no function of (C, P, κ\_H, κ\_L) can recover it. Option (b) will confirm this on real noise; it should not be the decider.
- The real-noise reach of option (b) (16 min) sits where linear stacking already predicts ≈ 0.4 dex surviving at ξ = 1e-3, so a positive real-noise result there would not distinguish "nonlinear helps" from "linear still fine". Its value is the stacked-calibration check, not the positioning.

The literature readings hold up against the abstracts: Drasco & Flanagan quote a factor 1–3 in the minimum detectable Ω for ground- and space-based detectors, depending on duty cycle ([abstract](https://arxiv.org/abs/gr-qc/0210032)); Lawrence et al. model ξ ≈ 1e-3 as a Gaussian mixture and report outperforming the continuous cross-correlation search ([abstract](https://www.arxiv.org/abs/2301.07675)); Smith & Thrane claim about one day versus about 40 months ([abstract](https://arxiv.org/abs/1712.00688)). The memo's "factor 2 in Ω near ξ \~ 1e-4" is within the D&F range but the abstract gives no duty-cycle value; quote the 1–3 range in the response.

**The manuscript (Oct 31 draft).** Items a referee will flag on the second round, independent of comment 3:

| Where | Problem | Fix |
| --- | --- | --- |
| Abstract, Sec. V B, Sec. VII | Still 0.66 dex / factor 4.6 at ξ = 1e-3; rev2 Table II gives +0.50 ± 0.03 and +0.23 at 1e-2 | Replace with the 15-stretch numbers everywhere; one set of headline numbers |
| Table II vs Table V | Table II limits −7.3 to −7.6; Table V (after the comment-2 calibration) −4.4 to −4.9 | Regenerate Table II on the corrected axis; the 2.5-dex jump will be noticed |
| Table II caption vs text | "5 seeds (1400–1404)" vs "three seeds (1400–1402)" | One statement |
| Sec. II D | "Edgeworth expansion (Eq. 3)" | Eq. (4) |
| Sec. VI C | ρ\_ev ≈ 11.3 "narrowly clustered" contradicts Sec. V C (ρ\_burst ≈ 15 at 1e-3, 3.9 at 1e-2) and Sec. V C's own warning that ρ\_ev is not an SNR | Rewrite with Eq. (12) only |
| Sec. VI C (i) | "frequentist coverage validated on null data (Table III)" — Table III is a null upper-limit comparison, not coverage | Point to the P-P test (Sec. IV A) and say Table III tests false signals |
| Sec. VI B, segment length | "stacking information across multiple segments could further improve sensitivity" implies stacking favours ING-Net | Rewrite: stacking favours the second-order baseline (new subsection) |
| Sec. VI D | "extending the observational horizon", tighter Gμ constraints | Condition on ξ ≲ 1e-4 and short timescales, or cut |
| Sec. I | "spectral methods dilute sparse bursts into the noise floor" | Soften: dilution is repaid by T\_obs^1/2; the issue is per-event information, not dilution |
| Eq. (5) | c\_w = 1.73 for a Hann envelope; a periodic or half-sample Hann gives 35/18 = 1.94, a symmetric 8-point Hann 2.2 | State the discrete window; 1.73 matches none of the standard forms |
| Sec. III B, Tables III, IV, VI, Fig. 7 | Placeholders \[X\], \[Y\], \[n/N\], \[revised values\], \[\] | Fill before resubmission |

Two things the manuscript gets right and should keep saying: the generic-burst argument of Sec. VI B (per-segment cumulants up to fourth order are blind to morphology) and the paired null test of Table III. Both survive the new positioning.

## The new test: three combination rules on one synthetic data set

The test extends the Oct-26 scaling analysis by combining segments in the two other ways the field uses, on the same data, so the three answers are comparable term by term. Code: `stacking_test.py` (numpy/scipy/scikit-learn, no training; about 50 minutes on two cores).

**Data.** Two detectors, white unit-variance Gaussian noise, 4 s segments (n = 8192 at 2048 Hz). Events as in rev2: Poisson start times at rate ξ/τ per sample, Hann-windowed white Gaussian bursts of τ = 8 samples, plus and cross polarisations drawn independently and projected with the real H1/L1 antenna tensors (isotropic sky, uniform ψ), normalised so that ⟨A⟩ = 1. The code reproduces γ\_HL(0) = −0.891 and c\_F = 1.43 from the detector geometry alone. Per-event per-sample variance is a² = σ\_s²/ξ, so the time-averaged signal variance is σ\_s² (= Ω σ\_1² in the paper). Per-event matched-filter SNR per detector is ρ = a √(τ A), Eq. (12).

**Summaries.** C\_HL, P = log power, κ\_H, κ\_L (Eqs. 7–8). Three sets: CC = (C\_HL), the LVK statistic; Trad = (C\_HL, P), the paper's power-only baseline; ING = all four.

**Combination rules**, each applied at the true (σ\_s², ξ):

1. LIN — average the summaries over N segments and apply the optimal linear (Fisher) combination for the known signal shape. This is the Oct-26 test and the way cross-correlation estimates are stacked.
2. NL — multiply per-segment likelihoods of the summary vector: p(x | σ\_s², ξ) = Σ\_k Poisson(k; λ) · GMM\_k(x), with a three-component Gaussian mixture fitted to 800 simulated segments containing exactly k events, k up to the 1 − 1e-5 Poisson quantile. This is the Lawrence et al. construction, and with a uniform prior it is what multiplying ING-Net posteriors does (memo Sec. 8); a learned MAF would sit between this fit and the exact feature likelihood.
3. DF — a Drasco–Flanagan-type two-component mixture likelihood on the full two-detector time series: for every window start t, the ratio of the Gaussian likelihood with covariance I + a² w\_j² M̄ (M̄ the sky-averaged 2×2 signal covariance, off-diagonal γ\_HL(0)) to the noise likelihood, combined as Σ\_t log(1 − p + p e^{L\_t}) with p = ξ/τ. It uses within-burst H1–L1 coherence and time localisation, which the summaries discard. This is the comment-10 benchmark on Gaussian noise.

**Detection and limits.** Threshold at the 99.7 % quantile of the stacked statistic on noise-only stacks (0.3 % false alarm, as in the paper); the limit σ\_50(N) is the amplitude giving 50 % detection. Amplitudes on a 0.1-dex grid from 10^-4.3 to 10^-1; the crossing is interpolated. For N ≤ 1000 the stacked statistic is bootstrapped (3000 stacks) from pools of 6000 noise segments and 6000 signal segments built on the same noise (paired). For all N a central-limit estimate N\_50(σ) = (2.748 s\_0 / Δm)² from the paired pool moments is also computed; the two agree at N = 1000 (Section 4 lists the check).

**Self-checks** (reported with the results): second-order limits fall as N^-1/2; at ξ = 1 all gains are within ±0.03 dex; at N = 1 the ING–Trad gain reproduces the memo and the paper (0.24 vs 0.22/0.23 at ξ = 1e-2); NL ≥ LIN at N = 1 (a likelihood ratio cannot do worse than its own linear projection); noise κ̂ has standard deviation 0.053 = √(24/n).

**What it does not model.** Real, coloured, glitchy noise; the inter-detector delay; the ING-Net network itself. It answers one question only: given the four summaries and this signal model, which combination rule keeps how much gain for how long.

## Results: gains versus stacked duration

All three rules lose the gain on the same clock, set by the per-event SNR at the cross-correlation limit, and the full-data likelihood is the only one that keeps anything at ξ = 1e-3 beyond an hour.

&#91;embedded content: stacking\_test.py, run of 2026-10-30 · synthetic Gaussian noise, rev2 signal model · 6000 paired segments per amplitude, 0.1-dex amplitude grid\]

Negative values of the product-of-likelihoods line at long stacks are not physics: they are the fitted per-segment likelihood's own error, compounded over 10³–10⁵ segments (the same effect appears at ξ = 1 where the true gain is zero). Read them as "no gain".

**Where the gain crosses 0.1 dex, and what the events look like there**

| ξ | Stacked summary (memo Sec. 4) | Product of likelihoods (option b) | Full-data D&F likelihood | Per-event SNR at the CC limit when the summary gain is gone |
| --- | --- | --- | --- | --- |
| 1e-2 | 2–7 min | 2–7 min | 20 min | 1.6 per detector |
| 1e-3 | 1.1 h | 3.3 h | 2–4 d (0.21 dex at 11 h, 0.04 at 4.6 d) | 2.2–2.9 |
| 1e-4 | > 4.6 d (0.17 dex at 4.6 d) | > 4.6 d (0.28 dex) | > 4.6 d (0.49 dex; cross-correlation overtakes after about 6 months by extrapolation) | 2.9 at 4.6 d |

**Per-segment (N = 1) cross-check against the paper**

| ξ | ING − Trad here | ING − Trad, rev2 Table II (real noise) | ING − Trad, memo Sec. 4 (synthetic) | D&F − ING here |
| --- | --- | --- | --- | --- |
| 1e-2 | +0.29 | +0.23 ± 0.02 | +0.22 | +0.33 |
| 1e-3 | +0.63 | +0.50 ± 0.03 | +0.58 | +0.39 |

The slightly larger synthetic gains come with c\_w = 1.94 for the Hann envelope (the paper quotes 1.73); κ\_sig is proportional to c\_w.

**Self-checks.** Cross-correlation limits fall as N^-0.49 (ξ = 1e-2), N^-0.51 (1e-3) and N^-0.50 (ξ = 1) per decade; at ξ = 1 all gains are within ±0.03 dex at every N; bootstrap and central-limit limits agree to ≤ 0.03 dex at N = 1000 for every method; the noise kurtosis scatter is 0.053 = √(24/n); the Trad − CC offset of 0.17–0.19 dex at long stacks is the known-noise-level power channel, the same at ξ = 1, so it is not a non-Gaussian effect.

**Reading the ξ = 1e-4 panel.** The stacked summary keeps 0.36 dex at 11 h and 0.17 dex at 4.6 d; the product of likelihoods keeps 0.60 and 0.28 dex; the full-data likelihood 0.91 and 0.49 dex. The last is a factor of 3 in Ω at 4.6 d (8 × 10⁸ samples), above Drasco & Flanagan's factor of about 2 at ξ \~ 1e-4 for N = 10⁹ samples, because the paper's bursts have a resolved 8-sample envelope that a sliding-window likelihood can match-filter, whereas D&F assume unresolved event structure. The full-data limit improves only by 0.2 dex between 1.1 h and 4.6 d: in this regime the statistic counts individually significant events against a trials factor, and more data helps only logarithmically.

Full tables (all N, all methods, per-event SNR) are in `stacking_table.csv`; raw limits, pools' moments and the bootstrap detection fractions in `stacking_results_merged.json`.

## What this means for positioning, and the four decisions

The paper's distinctive regime (ξ = 1e-2, events individually invisible) is exactly the one where no combination rule keeps the gain beyond minutes, so the positioning must change from "deeper limits on sub-threshold populations" to "a per-segment non-Gaussian inference module". That is a claim the results support fully and the referee can accept without a further round.

**What ING-Net can honestly claim after this revision**

- A calibrated joint posterior on (Ω, ξ) from 4 s of data, trained on real detector noise, with the per-detector kurtosis pair separating coherent bursts from single-detector transients (Secs. IV–VI A). No cross-correlation search delivers ξ at all.
- Per-segment detection 0.23–0.50 dex deeper than the matched power-only baseline at ξ ≤ 1e-2 (Table II), with the null test of Table III; the gain is a loud-event effect (ρ ≳ 2–3) and the paper now says so and says how it decays.
- A route to long-duration sparse-background searches that the new analysis makes concrete: replace or supplement the kurtosis pair with a burst-coherent summary (the per-window Drasco–Flanagan log-likelihood, or a learned equivalent), which keeps 0.5 dex at 4.6 d for ξ = 1e-4 on Gaussian noise. That is future work, named as such.

**What it should stop claiming:** that intermittency gives deeper broadband limits; that sub-threshold populations at ξ \~ 1e-2 are found that other searches miss; the Population III / cosmic-string "horizon" paragraphs of Sec. VI D as written.

**Answers to the memo's four decisions**

| Decision | Recommendation | Why |
| --- | --- | --- |
| 1. Run option (b) before fixing the positioning? | Fix the positioning now on the synthetic result; run (b) as a real-noise confirmation with the expectation stated in advance (gain below 0.1 dex within 16 min at ξ = 1e-2, about 0.3 dex surviving at 1e-3) | The synthetic test already answers the physics; a 4-day real-noise run that lands where predicted pre-empts the referee's "but this is synthetic" and tests the compounding of per-segment calibration error, which is the real risk |
| 2. Stack length | Real noise to 16 min; synthetic whitened Gaussian noise to about 11 h, with the single-segment coverage check first | Hours are where the ξ = 1e-3 statement is made; synthetic noise is adequate for a statement that is itself about accumulation, provided calibration on it is checked |
| 3. Positioning if (b) is negative | Per-segment inference module (above); option (c) named as future work with the burst-coherent summary, not attempted in this revision | At ξ \~ 1e-4 the summary that keeps a gain is not the kurtosis pair; retraining ING-Net at lower ξ would keep at most 0.2–0.3 dex at days, against 0.5 dex for the full-data statistic |
| 4. Comment 10 | Cite Drasco–Flanagan and Lawrence et al. and include our Drasco–Flanagan implementation on Gaussian noise as the benchmark in the new subsection (per-segment and stacked); state that the analytic statistic is 0.33–0.39 dex deeper per segment on Gaussian noise and that its real-noise version needs an explicit glitch component, which is outside this paper | Answers the request for a non-Gaussian benchmark fully, concedes what must be conceded, and leaves the real-noise comparison as a well-defined follow-up rather than an omission |

**One thing to decide that the memo did not list.** Table II's absolute limits (log10 Ω ≈ −7.3 to −7.6) and Table V's (−4.4 to −4.9, after the comment-2 calibration) differ by 2.5 dex. The abstract and Sec. V must quote one calibrated axis, and the comparison with the LVK O3 limit (Ω ≤ 5.8 × 10⁻⁹) in the response should use it: the per-segment limits are 3.4 orders of magnitude above the broadband limit, which is the statement the referee asked for in (a).

## Draft response to the referee: comments 3 and 10

The draft concedes the point in the first sentence, gives the referee the two things asked for with numbers, and states the new positioning in the referee's own terms (stacking, Drasco–Flanagan, Lawrence et al.). Numbers in brackets are from the synthetic test and should be replaced by the real-noise option-(b) values where those exist.

**Comment 3 (per-segment versus accumulated sensitivity)**

We thank the referee for this comment, which we agree identifies the central limitation of the submitted version. The referee is right on both counts: the limits in Table II are per-segment limits on 4 s of data at a fixed false-alarm probability, and the advantage of the kurtosis channel is a per-segment effect whose survival under accumulation we had not tested. We have made three changes.

(a) *Explicit statement.* The abstract, the opening paragraph of Sec. V and the caption of Table II now state that all limits are per-segment limits on a fixed dataset, obtained at a 0.3 % false-alarm probability per 4 s segment, and are not comparable to published broadband upper limits, which integrate over an entire observing run. For orientation we add the comparison the referee alluded to: at ξ = 10⁻² our per-segment limits are log10 Ω ≈ −4.7 to −5.3, about 3.4 orders of magnitude above the LVK O3 isotropic limit Ω ≤ 5.8 × 10⁻⁹ (flat spectrum, Abbott et al. 2021).

(b) *Scaling analysis and multi-segment result.* New Sec. V F ("Combining segments") and Fig. \[new\] report the gain Δ as a function of the number of combined 4 s segments, N = 1 to 10⁵ (4 s to 4.6 d), at ξ = 10⁻², 10⁻³ and 10⁻⁴, for three ways of combining segments: (i) linear stacking of the per-segment summaries, which is how cross-correlation estimates are combined; (ii) a product of per-segment likelihoods of the summary vector, the construction of Lawrence et al. (2023) and the natural way to combine the per-segment posteriors of ING-Net; and (iii) the Drasco–Flanagan two-component mixture likelihood evaluated on the full two-detector time series, implemented as a sliding-window statistic with the sky-averaged H1–L1 signal covariance. The analysis uses the signal model of Sec. II on Gaussian noise; it reproduces the per-segment gains of Table II at N = 1 \[0.29 and 0.63 dex at ξ = 10⁻² and 10⁻³ against 0.23 and 0.50 on real noise\], the N⁻¹ᐟ² scaling of the second-order limits, and |Δ| ≤ 0.03 dex at ξ = 1 for all N.

The result confirms the referee's expectation. The per-segment advantage is a property of individually loud events: it exists only while the events at the detection limit have a per-detector matched-filter SNR ρ\_burst ≳ 2–3 \[Eq. (12)\]. As segments are combined, the second-order limit falls as N⁻¹ᐟ² and the fourth-cumulant limit as N⁻¹ᐟ⁴, so the gain closes by about 0.25 dex per decade of N under linear stacking and is below 0.1 dex after \[2–7 min\] at ξ = 10⁻² and \[1.1 h\] at ξ = 10⁻³. Multiplying per-segment likelihoods does not change this conclusion: it retains at most \[0.1 dex\] more than linear stacking at ξ = 10⁻³, for about an hour, because once single events are weak the per-segment likelihood is, to leading order, linear in the fourth cumulant and the product reduces to a linear stack. The full-data Drasco–Flanagan statistic keeps \[0.2 dex\] at ξ = 10⁻³ after 11 h and \[0.04 dex\] after 4.6 d, consistent with Drasco & Flanagan's finding that their statistic begins to outperform cross-correlation at ξ \~ 10⁻³ for year-long ground-based data. Only at ξ = 10⁻⁴ does a gain persist over days: \[0.17 dex\] for the stacked summaries, \[0.28 dex\] for the product of likelihoods and \[0.49 dex\] for the full-data statistic at 4.6 d.

(c) *Positioning.* We have rewritten the abstract, Sec. VI C, Sec. VI D and the conclusion accordingly. ING-Net is now presented as a per-segment non-Gaussian inference module: it returns a calibrated joint posterior on (Ω, ξ) from 4 s of data, which no cross-correlation search provides, and it is trained on real detector noise with a per-detector summary that separates coherent bursts from single-detector transients. We no longer claim that it reaches deeper limits than second-order searches over long observations, and we state that the kurtosis summary, which discards within-burst coherence and time localisation, is not the right summary for long-duration searches of very sparse backgrounds; Sec. V F identifies the burst-coherent summary that is, and we leave it to future work.

&#91;If option (b) has been run:\] We have also combined the actual ING-Net per-segment posteriors over up to \[246\] segments of real evaluation noise and up to \[10⁴\] segments of synthetic whitened noise (Sec. V F, Table \[new\]); the combined gain follows the synthetic prediction to within \[0.1 dex\] and the coverage of the combined posterior remains within \[the 2σ band\] at every N, which addresses the compounding of per-segment calibration error that a product of posteriors is exposed to.

**Comment 10 (non-Gaussian benchmark)**

We agree that a comparison with the Gaussian-mixture likelihood of Drasco & Flanagan (2003) and its implementation by Lawrence et al. (2023) was missing. We have implemented the Drasco–Flanagan statistic for our signal model (Sec. V F, Appendix \[new\]) and report it on the same synthetic data as ING-Net, per segment and combined over segments. On Gaussian noise it is \[0.33 dex\] (ξ = 10⁻²) and \[0.39 dex\] (ξ = 10⁻³) deeper than ING-Net per segment, because it uses the H1–L1 coherence within each burst and the burst's time localisation, which our segment-level summaries discard, and it retains a gain under accumulation for longer (above). We state this plainly in the revised Sec. VI A. The practical case for ING-Net is therefore not sensitivity on Gaussian noise but (i) the joint posterior on (Ω, ξ), (ii) training on real, non-stationary detector noise, and (iii) the per-detector summary's rejection of single-detector transients, which the analytic likelihood treats as signal unless an explicit glitch component is added to the mixture. A direct comparison on real noise requires such a component and a model of its rate; we regard this as the natural next step and say so, rather than claim a benchmark we have not run. \[Alternative, if the authors run the Lawrence et al. likelihood on the 15 stretches: replace the last two sentences with the measured per-segment and stacked numbers on real noise, including its false-alarm behaviour on glitch-contaminated segments.\]

**Short version for the cover letter.** We confirm the referee's point: the kurtosis advantage is per-segment and does not survive accumulation except for ξ ≲ 10⁻⁴; the manuscript now says so in the abstract, states the limits as per-segment limits, adds a three-way scaling analysis including the Drasco–Flanagan statistic, and repositions the method as a per-segment inference module with the long-duration extension identified as future work.

## Draft manuscript text

Ready to paste; bracketed numbers are from the synthetic test and get replaced by the rev2 or option-(b) values where those apply.

**Abstract, replacing the last four sentences.** "On 4 s segments of real LIGO noise from O3a, O3b and O4a, ING-Net reaches a detection limit in Ω\_GW that is 0.50 ± 0.03 orders of magnitude deeper than a matched-architecture power-only baseline at ξ = 10⁻³ and 0.23 ± 0.02 at ξ = 10⁻², while recovering the duty cycle that second-order summaries cannot constrain. These are per-segment limits on a fixed dataset and are not comparable to broadband upper limits that integrate over an observing run. We show that the per-segment advantage is a property of individually loud events: when segments are combined, whether by linear stacking, by a product of per-segment likelihoods or by the Drasco–Flanagan mixture likelihood on the full data, it falls below 0.1 dex within minutes at ξ = 10⁻² and hours at ξ = 10⁻³, and persists over days only for ξ ≲ 10⁻⁴. ING-Net is therefore a per-segment non-Gaussian inference module, delivering a calibrated joint posterior on (Ω, ξ) that is robust to single-detector transients, rather than a replacement for long-duration cross-correlation searches."

**Sec. V, new opening paragraph.** "All sensitivity limits in this section are per-segment limits: each is the amplitude detected with 50 % probability in a single 4 s segment at a false-alarm probability of 0.3 % per segment, on a fixed dataset. They characterise what the estimator extracts from one segment and are not comparable to published upper limits on Ω\_GW, which combine of order 10⁶ segments; the relation between the two is the subject of Sec. V F."

**Table II caption, add.** "Per-segment limits (4 s, 0.3 % false alarm per segment); see Sec. V F for their behaviour under accumulation. Not comparable to broadband upper limits."

**New Sec. V F, Combining segments.** "Every operational SGWB search combines many segments, so the question is whether the per-segment gain Δ of Table II survives accumulation. We answer it with the signal model of Sec. II on white Gaussian noise, for N = 1 to 10⁵ segments (4 s to 4.6 d) and ξ = 10⁻², 10⁻³, 10⁻⁴, using three combination rules: (i) linear stacking of the per-segment summaries with the optimal linear combination for the known signal shape, as cross-correlation estimates are stacked; (ii) a product of per-segment likelihoods of the summary vector, p(x | Ω, ξ) = Σ\_k P(k; λ) p\_k(x), with p\_k a Gaussian mixture fitted to segments containing exactly k events, which is the construction of Lawrence et al. \[27\] and, with a uniform prior, what a product of ING-Net posteriors computes; (iii) the Drasco–Flanagan mixture likelihood \[9\] on the full two-detector time series, implemented as a sliding-window statistic Σ\_t log(1 − p + p e^{L\_t}) with p = ξ/τ and L\_t the log-likelihood ratio of a burst starting at t with the sky-averaged H1–L1 signal covariance. Thresholds are the 99.7 % quantile of each stacked statistic on noise-only stacks and the limit is the amplitude detected with 50 % probability, as in Sec. V B. At N = 1 the analysis reproduces Table II \[Δ = 0.29 and 0.63 dex at ξ = 10⁻² and 10⁻³\]; the second-order limits fall as N⁻¹ᐟ² and all gains vanish at ξ = 1 to within 0.03 dex.

Figure \[new\] shows Δ against stacked duration. The second-order channel improves as N⁻¹ᐟ² and the fourth-cumulant channel as N⁻¹ᐟ⁴ \[Eqs. (5)–(6) with Var(κ̂) ∝ 1/(nN)\], so the gap closes by 0.25 dex per decade of N, and it closes on the same clock for all three rules: the gain exists only while the events at the detection limit have a per-detector SNR ρ\_burst ≳ 2–3 \[Eq. (12)\]. Below that, the per-segment likelihood is linear in the fourth cumulant to leading order and a product of likelihoods reduces to a linear stack. Under linear stacking Δ falls below 0.1 dex after \[2–7 min\] at ξ = 10⁻² and \[1.1 h\] at ξ = 10⁻³; the product of likelihoods retains at most \[0.1 dex\] more, for about an hour at ξ = 10⁻³; the Drasco–Flanagan statistic, which uses the H1–L1 coherence within each burst and its time localisation, keeps \[0.2 dex\] at ξ = 10⁻³ after 11 h and \[0.04 dex\] after 4.6 d. Only at ξ = 10⁻⁴, where single events at the limit remain loud for days, does a gain persist: \[0.17, 0.28 and 0.49 dex\] at 4.6 d for the three rules. The last figure is a factor of 3 in Ω, above the factor of about 2 found by Drasco and Flanagan at ξ \~ 10⁻⁴ for 10⁹ samples, because our bursts have a resolved envelope that a sliding-window likelihood can match-filter.

Two consequences follow. First, the sub-threshold regime ξ \~ 10⁻², in which ING-Net detects a population through its kurtosis alone, is exactly the regime in which accumulation removes the advantage within minutes; the per-segment limits of Table II should not be read as a route to deeper broadband limits. Second, for very sparse backgrounds the statistic that retains a gain over long observations is not the segment kurtosis but a burst-coherent likelihood; a learned summary of that kind, combined across segments as in (ii), is the natural extension of the present framework and we leave it to future work. What the present method provides, and what no second-order search provides, is the joint per-segment posterior on (Ω, ξ) of Figs. 3–5, obtained on real detector noise with the per-detector veto of Sec. VI A."

**Sec. VI A, add after the Lawrence et al. sentence.** "On Gaussian noise the analytic mixture likelihood is more sensitive than ING-Net by \[0.33–0.39 dex\] per segment (Sec. V F), because the per-segment summaries discard within-burst coherence. Its application to real noise requires a glitch component in the mixture and a model of its rate; ING-Net absorbs that structure by training on real noise and by keeping κ\_H1 and κ\_L1 separate."

**Sec. VI B, segment length, replace the last two sentences.** "Stacking information across segments does not favour the kurtosis channel: as shown in Sec. V F, it favours the second-order summaries, whose limit improves as N⁻¹ᐟ² against N⁻¹ᐟ⁴ for the fourth cumulant."

**Sec. VI C, replace the opening and point (ii).** Open with Eq. (12): "At the detection limits of Table II the median single-event SNR per detector is ρ\_burst ≈ 15 at ξ = 10⁻³, above the thresholds of cWB-type searches, and ρ\_burst ≈ 3.9 at ξ = 10⁻², below them." Then: at ξ = 10⁻³ the method overlaps with burst searches per event and adds a population-level posterior; at ξ = 10⁻² it detects what no single-event search sees, but only per segment, since Sec. V F shows that accumulation removes this advantage within minutes. Point (ii) keeps the unresolved-tail argument but adds "within a segment". Drop ρ\_ev ≈ 11.3.

**Sec. VI D.** Keep the two source classes as motivation, condition every sensitivity statement on "per segment" or "for ξ ≲ 10⁻⁴ with a burst-coherent summary", and delete "directly extending the observational horizon" and the Gμ range.

**Conclusion, replace the second key result and add a fourth.** "Second, in the intermittent regime ING-Net reaches per-segment limits 0.50 ± 0.03 dex (ξ = 10⁻³) and 0.23 ± 0.02 dex (ξ = 10⁻²) deeper than the power-only baseline on 15 stretches of real noise from three observing runs. … Fourth, the per-segment gain is a property of individually loud events and does not survive the accumulation of segments, under any of three combination rules, except for ξ ≲ 10⁻⁴; the long-duration extension requires a burst-coherent summary, which we identify as the next step."

## What the real-data run should still check, and the files

Option (b) is worth its four days only if it is set up to test the one thing the synthetic analysis cannot: how the trained posterior's own error compounds when multiplied. Changes to the memo's Sec. 8 design:

1. State the expected outcome before the run, from Section 4: combined gain below 0.1 dex within 16 min at ξ = 1e-2; about 0.3 dex at 16 min and 0.1 dex at 3 h for ξ = 1e-3.
2. Divide the product of N posteriors by the prior to the power N − 1 (uniform, so a constant, but the prior edges at log10 ξ = −3 and log10 Ω = −8 are not), and report the combined posterior's coverage at every N. In the synthetic product-of-likelihoods rule, a per-segment likelihood fitted independently per event count fell 0.3–0.5 dex behind linear stacking beyond about 3 h at ξ ≥ 1e-3; a MAF trained across the prior is smoother, but its log-density must be accurate to roughly 1/√N at the weak-signal end for the product not to lose.
3. Report, beside the product, the linear stack of the per-segment posterior means of log10 Ω for both networks; it is the rule the paper's own Sec. V F predicts to be optimal once events are weak, and it is immune to the compounding above.
4. Keep N ≤ 10⁴ (11 h) with synthetic whitened noise, and real noise to N ≈ 246 (16 min), as planned; longer stacks add nothing the synthetic analysis does not already give.
5. If comment 10 is to be answered on real noise, add a per-detector glitch component to the mixture likelihood (a third component with its own rate), otherwise the analytic statistic's false-alarm rate on glitch-contaminated segments is not comparable to ING-Net's.

**Caveats of the synthetic test** (to carry into the paper's new subsection): white Gaussian noise and no inter-detector delay; the product-of-likelihoods rule uses a three-component Gaussian mixture per event count, which under-performs the linear stack for loud single events (ξ = 1e-4, N ≤ 100) and is therefore a lower bound there; the Drasco–Flanagan statistic uses the sky-averaged signal covariance, a lower bound on the sky-marginalised optimum; all three statistics assume the true (Ω, ξ), so the marginalised versions pay a small trials factor; c\_w = 1.94 here against 1.73 in the manuscript.

**Files delivered with this document**

**Runner for the real models** (`option_b_real.py`, added 2026-10-30 23:50). Implements steps 1–5 above against the trained networks: per-segment log posteriors on a 71 × 31 grid in (log10 Ω, log10 ξ), the product over N segments, the posterior-mean statistic, 0.3 % thresholds from noise-only stacks, bisection to the 50 % limit for both the product and the linear stack, Trad combined the same way, coverage at N = 1, 10, 100, and the gains per run with the pre-stated expectation written into the output. Five adapter functions at the top of the file must be pointed at the SGWB1 loaders (evaluation noise, injector, feature extractor, posterior loader, grid log-prob); `python3 option_b_real.py --selftest` checks the generic part (passes on a mock posterior), then `python3 option_b_real.py` on the server, `--synthetic` for the 1.1–11 h stacks. Send back `option_b_results.json` and the bracketed numbers in Sections 6 and 7 get replaced.

| File | What it is |
| --- | --- |
| `stacking_test.py` | The simulation: signal model, summaries, three combination rules, bootstrap and central-limit stacking; `--xi`, `--grid`, `--quick` options |
| `lin_rerun.py` | Linear-stacking limits with analytic signal directions and noise covariance (the values used in the tables and figure) |
| `make_figure.py` | Merges the result files, prints the tables, draws the figure |
| `stacking_gain_vs_duration.png`, `.pdf` | Manuscript-ready figure: limits (top) and gains (bottom) against stacked duration, three duty cycles, six statistics |
| `stacking_table.csv` | All limits and gains for every N, ξ and statistic, with the per-event SNR at the cross-correlation limit |
| `stacking_results_merged.json` | Raw limits (bootstrap and central-limit), detection fractions on the amplitude grid, pool moments |

Reproduce with `python3 stacking_test.py --xi 0.01` and `--xi 0.001,0.0001,1.0` (about 30 min each on one core), `python3 stacking_test.py --xi 0.0001 --grid=-5.6,-4.4,0.1 --out res_c.json`, `python3 lin_rerun.py --xi 0.01,1.0 --out lin_a.json`, `python3 lin_rerun.py --xi 0.001,0.0001 --out lin_b.json`, then `python3 make_figure.py`.

Sources: [Drasco & Flanagan 2003](https://arxiv.org/abs/gr-qc/0210032) · [Lawrence et al. 2023](https://www.arxiv.org/abs/2301.07675) · [Smith & Thrane 2018](https://arxiv.org/abs/1712.00688) · referee report DT18456, memo of 2026-10-30 and manuscript draft of 2026-10-31 (attached to the conversation).
