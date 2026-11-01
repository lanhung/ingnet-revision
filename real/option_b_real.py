#!/usr/bin/env python3
"""
option_b_real.py -- Option (b) of the Oct-30 memo on the REAL trained networks:
combine per-segment ING-Net posteriors over N segments and compare with the power-only
network combined the same way, and with a linear stack of per-segment posterior means.

Everything below the ADAPTER block is pipeline-independent. The adapter has five functions that
call the SGWB1 code (`/root/SGWB1/.workspace_rev2/rev1/utils_rev1.py`, read-only). Run first with
--selftest, which exercises the generic part on a mock posterior and must print "selftest OK".

Design (memo Sec. 8, with the changes recommended in the report of 2026-10-30):
  1. models: trained ING-Net (4-D) and Trad (2-D) networks of the reference stretch of each run,
     seeds 1400-1402; evaluation noise only, never seen in training; no retraining.
  2. per-segment output: log posterior density on a grid in (log10 Omega, log10 xi).
  3. combination: sum of per-segment log posteriors over N segments (uniform prior => product of
     likelihoods up to a constant); the prior^(N-1) correction is a constant inside the prior box.
  4. detection statistic: posterior mean of log10 Omega under the combined posterior; threshold at the
     99.7 % quantile over noise-only stacks; 50 %-detection amplitude by bisection, injecting into every
     segment of the stack.  Also reported: the LINEAR stack (mean over segments of the per-segment
     posterior mean of log10 Omega), the rule predicted to be optimal once events are weak.
  5. baselines: the Trad network combined both ways.
  6. stack lengths: N = 1, 3, 10, 30, 100, 246 from non-overlapping real evaluation noise;
     longer stacks only with synthetic whitened Gaussian noise (--synthetic), after the single-segment
     coverage check on it.
  7. duty cycles: xi = 1e-3, 1e-2.
  8. coverage of the combined posterior at each N (P-P statistic) from injections drawn from the prior.
  9. readout: Delta_comb(N) for each xi; pre-stated criterion: Delta_comb >= 0.1 dex at the longest stack.
Expected outcome from the synthetic analysis (state before running): gain < 0.1 dex within 16 min at
xi = 1e-2; about 0.3 dex at 16 min and 0.1 dex at 3 h at xi = 1e-3.

Output: option_b_results.json with limits, gains, coverage and the raw per-N detection curves.

Changes of 2026-10-31 (task 2):
  * the five adapters are filled in (see the ADAPTER block; nothing under /root/SGWB1 is written);
  * `combined_stats` is the same quantity computed as a multiplicity matrix times the per-segment
    log posteriors (one matmul instead of an N-fold loop; needed for N = 1e4);
  * synthetic noise is Gaussian noise with the whitened-data spectrum (band 20-1000 Hz, unit robust
    scale) instead of white noise, so that the networks see the same noise-only features;
  * diverged Trad seeds (limit pinned at the prior top in the rev2 pipeline) are skipped and the
    gain is reported from the remaining seeds; `--include-diverged` keeps them;
  * results are written after every (stretch, seed, network) and `--resume` continues a partial file;
  * `--stretches` selects the stretch index within a run (0 = reference stretch, 1-4 = the rev1x ones).
"""
import numpy as np, json, time, argparse, sys, os, glob
from numpy.random import default_rng
try:
    from scipy.stats import norm
    Z997 = norm.ppf(0.997)
except ImportError:            # scipy is only needed for this constant
    Z997 = 2.747781385444

N_LIST_REAL = [1, 3, 10, 30, 100, 246]
N_LIST_SYN = [1000, 3000, 10000]
XI_LIST = [1e-3, 1e-2]
LOGOMEGA_GRID = np.linspace(-8, -1, 71)       # prior U[-8, -1]
LOGXI_GRID = np.linspace(-3, 0, 31)           # prior U[-3, 0]

# ======================================================================================= ADAPTER
# The five functions below call into /root/SGWB1 (read-only).  Shapes are fixed:
#   noise: float array (2, T) whitened unit-variance H1/L1 strain of the EVALUATION part of a stretch
#   segments: float array (B, 2, 8192)
#   features: float array (B, 4) in the order of utils_rev1.Simulator.compute_features, i.e.
#             (C_HL, log1p|kappa_H1|, log1p|kappa_L1|, log10(var_H1 var_L1)); the networks only ever see
#             `idx` applied to this order (ING-Net [0,1,2,3], Trad [0,3]).  NB: this is not the manuscript's
#             order (C_HL, P, kappa_H1, kappa_L1).
#   log_prob_grid: float array (B, len(LOGOMEGA_GRID), len(LOGXI_GRID)) of log q_phi(theta | x_b)

SGWB1 = os.environ.get('SGWB1', '/root/SGWB1/.workspace_rev2')      # read-only source
TAG_REF, TAG_X = 'rev1_glitchaug', 'rev1x_glitchaug'                   # the 15-stretch networks (Table II)
STRETCHES = {'O3a': ['03A', '03A2', '03A3', '03A4', '03A5'],
             'O3b': ['03B', '03B2', '03B3', '03B4', '03B5'],
             'O4a': ['04A', '04A2', '04A3', '04A4', '04A5']}
# Trad seeds whose rev2 limit sat at the prior top (outputs_rev1/diverged_*.csv); no ING-Net seed diverged
DIVERGED_TRAD = {('03A', 1401), ('03A', 1402), ('03B', 1402), ('04A2', 1401)}
CHUNK = 1024                      # segments per GPU batch in inject/features
LP_CHUNK = 2048                   # segments per log_prob batch (2201 grid points each)
_S = {}                           # adapter state: U module, torch, current stretch, simulator, sigma1

def _U():
    """Import utils_rev1 once (cwd-independent; data_dir is made absolute in load_eval_noise)."""
    if 'U' not in _S:
        import torch
        sys.path.insert(0, os.path.join(SGWB1, 'rev1'))
        import utils_rev1 as U
        _S['U'], _S['torch'] = U, torch
    return _S['U'], _S['torch']

def stretch_name(run, stretch_index=0):
    return STRETCHES[run][stretch_index]

def run_dir(stretch, seed):
    """Run directory of the glitchaug training for (stretch, seed); the latest timestamp if several."""
    tag = TAG_REF if len(stretch) == 3 else TAG_X
    cands = sorted(glob.glob(os.path.join(SGWB1, 'outputs_rev1', tag, f'{stretch}_seed{seed}_*')))
    cands = [c for c in cands if os.path.exists(os.path.join(c, 'models', f'model_ai_{stretch}.pt'))]
    if not cands:
        raise FileNotFoundError(f'no {tag} run with models for {stretch} seed {seed}')
    return cands[-1]

def load_eval_noise(run, stretch_index=0):
    """Whitened evaluation noise (2, T) of the given run/stretch (Sec. II C: last 25 %, 8 s gap, 16 s trimmed),
    exactly as utils_rev1.prepare_dataset builds it (rev2 whitening: median-Welch PSD, 20-1000 Hz, 1.4826 MAD).
    Also prepares the per-stretch Simulator (Eq. 11 sigma1 of the same stretch) used by `inject`."""
    U, torch = _U()
    stretch = stretch_name(run, stretch_index)
    meta = json.load(open(os.path.join(run_dir(stretch, 1400), 'run_meta.json')))
    cfg = dict(meta['config'])
    if not os.path.isabs(cfg['data_dir']):
        cfg['data_dir'] = os.path.normpath(os.path.join(SGWB1, cfg['data_dir']))
    U.CFG.update(cfg)
    ds = [d for d in U.CFG['datasets'] if d['name'] == stretch]
    if not ds:
        raise KeyError(f'{stretch} not in CFG["datasets"] of {run_dir(stretch, 1400)}')
    D = U.prepare_dataset(ds[0])
    h1, l1 = D['eval']
    sigma1 = float(D['sigma1'])
    ref = float(meta['dataset_meta']['sigma1']) if 'sigma1' in meta.get('dataset_meta', {}) else sigma1
    if abs(sigma1 / ref - 1) > 1e-3:
        raise RuntimeError(f'sigma1 {sigma1} differs from run_meta {ref}')
    _S.update(stretch=stretch, run=run, sigma1=sigma1, sim=U.Simulator(h1, l1, D['sigma1']), meta=meta,
              mode=U.CFG.get('mode'))
    return torch.stack([h1, l1]).detach().cpu().numpy().astype(np.float32)

def inject(segments, log10_omega, log10_xi, rng):
    """Add the intermittent background of Sec. II (Simulator.draw_signal: Poisson bursts, antenna-pattern
    H1/L1 draw, band-limited, per-event variance (Omega/xi) sigma1^2 with the Eq. 11 sigma1 of the stretch)
    to a copy of `segments`.  The simulator uses torch's global RNG, which is seeded from `rng` here."""
    U, torch = _U()
    sim = _S['sim']
    U.set_seed(int(rng.integers(2 ** 31 - 1)))
    out = np.empty_like(segments)
    with torch.no_grad():
        for a in range(0, segments.shape[0], CHUNK):
            b = min(segments.shape[0], a + CHUNK)
            lo = torch.full((b - a,), float(log10_omega), device=U.device)
            lx = torch.full((b - a,), float(log10_xi), device=U.device)
            s_h, s_l, _ = sim.draw_signal(lo, lx)
            seg = torch.as_tensor(segments[a:b], device=U.device)
            seg = torch.stack([seg[:, 0] + s_h, seg[:, 1] + s_l], 1)
            out[a:b] = seg.cpu().numpy()
    return out

def features(segments):
    """(B, 2, 8192) -> (B, 4) in the compute_features order (see the block comment).  Segments are
    mean-subtracted first, as Simulator.draw_noise does for the training segments."""
    U, torch = _U()
    out = np.empty((segments.shape[0], 4))
    with torch.no_grad():
        for a in range(0, segments.shape[0], CHUNK):
            b = min(segments.shape[0], a + CHUNK)
            seg = torch.as_tensor(segments[a:b], device=U.device)
            seg = seg - seg.mean(dim=2, keepdim=True)
            out[a:b] = U.Simulator.compute_features(seg[:, 0], seg[:, 1]).double().cpu().numpy()
    return out

class Posterior:
    """Trained sbi DirectPosterior plus the feature columns it was trained on."""
    def __init__(self, post, idx, stretch, seed, feature_set, diverged, path):
        self.post, self.idx, self.stretch, self.seed = post, [int(i) for i in idx], stretch, seed
        self.feature_set, self.diverged, self.path = feature_set, diverged, path

def load_posterior(run, seed, feature_set, stretch_index=0):
    """Trained posterior for (run, seed, feature_set in {'ing', 'trad'}) of the glitchaug run of the stretch."""
    U, torch = _U()
    stretch = stretch_name(run, stretch_index)
    key = {'ing': 'ai', 'trad': 'tr'}[feature_set]
    p = os.path.join(run_dir(stretch, seed), 'models', f'model_{key}_{stretch}.pt')
    d = torch.load(p, map_location=U.device, weights_only=False)
    if 'sigma1' in _S and abs(float(d['sigma1']) / _S['sigma1'] - 1) > 1e-3:
        raise RuntimeError(f'{p}: sigma1 {d["sigma1"]} differs from the loaded stretch {_S["sigma1"]}')
    return Posterior(d['posterior'], d['idx'], stretch, seed, feature_set,
                     feature_set == 'trad' and (stretch, seed) in DIVERGED_TRAD, p)

def log_prob_grid(posterior, feats, grid=None):
    """log q(theta | x) on the (log10 Omega, log10 xi) grid for every row of feats -> (B, nO, nX).
    `grid` = (points (n, 2), nO, nX) overrides the default grid (the coverage test uses a 0.02 dex grid).
    Direct call of the density estimator with the raw grid and raw features: the networks z-score x and
    theta internally (Standardize embedding, first PointwiseAffineTransform of the flow).  Equivalent to
    DirectPosterior.log_prob(grid, x=f, norm_posterior=False) per segment (checked on the server); the
    leakage constant is per-x and cancels in the grid normalisation, and the grid lies inside the prior box."""
    U, torch = _U()
    est = posterior.post.posterior_estimator
    x = torch.as_tensor(feats[:, posterior.idx], dtype=torch.float32, device=U.device)
    pts, nO, nX = grid if grid is not None else (GRID_POINTS, LOGOMEGA_GRID.size, LOGXI_GRID.size)
    theta = torch.as_tensor(pts, dtype=torch.float32, device=U.device)
    out = np.empty((feats.shape[0], pts.shape[0]))
    with torch.no_grad():
        for a in range(0, x.shape[0], LP_CHUNK):
            xb = x[a:a + LP_CHUNK]
            lp = est.log_prob(theta[:, None, :].expand(-1, xb.shape[0], -1), condition=xb)   # (nO*nX, b)
            out[a:a + xb.shape[0]] = lp.T.double().cpu().numpy()
    if not np.all(np.isfinite(out)):
        bad = ~np.isfinite(out).all(axis=1)
        out[bad] = np.where(np.isfinite(out[bad]), out[bad], -1e30)
    return out.reshape(feats.shape[0], nO, nX)

def synthetic_noise(nseg, seed=5):
    """Gaussian noise with the spectrum of the whitened data: white noise band-limited to 20-1000 Hz with the
    simulator's `bandlimit`, scaled to unit robust scale (1.4826 MAD) like `whiten_block`."""
    U, torch = _U()
    g = torch.Generator(device='cpu').manual_seed(seed)
    out = np.empty((nseg, 2, 8192), np.float32)
    with torch.no_grad():
        for a in range(0, nseg, CHUNK):
            b = min(nseg, a + CHUNK)
            w = torch.randn((b - a) * 2, 8192, generator=g).to(U.device)
            w = _S['sim'].bandlimit(w)                 # Simulator.bandlimit: rfft mask to [band_lo, band_hi]
            out[a:b] = w.reshape(b - a, 2, 8192).cpu().numpy()
    med = np.median(out); mad = np.median(np.abs(out - med))
    return ((out - med) / (1.4826 * mad)).astype(np.float32)

def device_matmul():
    """Return a matmul for combined_stats: torch float64 on the GPU when the adapters are active, else numpy."""
    if 'torch' in _S:
        torch, U = _S['torch'], _S['U']
        def mm(C, L):
            with torch.no_grad():
                Ct = torch.as_tensor(C, dtype=torch.float64, device=U.device)
                Lt = torch.as_tensor(L, dtype=torch.float64, device=U.device)
                return (Ct @ Lt).cpu().numpy()
        return mm
    return lambda C, L: C @ L
# =================================================================================== END ADAPTER

GRID_POINTS = np.array([(o, x) for o in LOGOMEGA_GRID for x in LOGXI_GRID])
LOGO = np.tile(LOGOMEGA_GRID[:, None], (1, LOGXI_GRID.size))
# finer log10 Omega grid (0.02 dex) for the coverage test: a product of 100 posteriors is ~0.02 dex wide
FINE_LOGOMEGA_GRID = np.linspace(-8, -1, 351)
FINE_GRID = (np.array([(o, x) for o in FINE_LOGOMEGA_GRID for x in LOGXI_GRID]), FINE_LOGOMEGA_GRID.size, LOGXI_GRID.size)

def multiplicity(idx, M):
    """(R, N) segment indices -> (R, M) counts of each segment in each stack."""
    R, N = idx.shape
    flat = (idx + np.arange(R)[:, None] * M).ravel()
    return np.bincount(flat, minlength=R * M).reshape(R, M).astype(np.float64)

def combined_stats(lp, idx):
    """lp: (M, nO, nX) per-segment log posteriors; idx: (R, N) segment indices per stack.
    Returns posterior mean of log10 Omega under the combined posterior (R,) and the linear stack (R,).
    The combined log posterior of a stack is sum_j lp[idx_j] = (multiplicity @ lp) -- one matmul."""
    R, N = idx.shape
    M = lp.shape[0]
    L = lp.reshape(M, -1)
    C = multiplicity(idx, M)
    S = device_matmul()(C, L)
    S -= S.max(axis=1, keepdims=True)
    w = np.exp(S); w /= w.sum(axis=1, keepdims=True)
    comb = w @ LOGO.ravel()
    # per-segment posterior means, then averaged (linear stack)
    lp0 = L - L.max(axis=1, keepdims=True); w0 = np.exp(lp0); w0 /= w0.sum(axis=1, keepdims=True)
    pm = w0 @ LOGO.ravel()
    lin = (C @ pm) / N
    return comb, lin

def stacks(M, N, R, rng, replace):
    if replace:
        return rng.integers(0, M, size=(R, N))
    return np.stack([rng.choice(M, size=N, replace=False) for _ in range(R)])

def run_one(noise_segments, posterior, xi, N_list, rng, log, R=2000, nseg_cap=None, synthetic=False):
    """For one network and one xi: thresholds and 50 %-detection limits for the combined and the linear rule."""
    M = noise_segments.shape[0]
    f0 = features(noise_segments)
    lp0 = log_prob_grid(posterior, f0)
    out = {}
    for N in N_list:
        replace = N > M // 4
        idx0 = stacks(M, N, R, rng, replace)
        c0, l0 = combined_stats(lp0, idx0)
        thr_c, thr_l = np.quantile(c0, 0.997), np.quantile(l0, 0.997)
        lims, curves = {}, {}
        for rule, thr in (('combined', thr_c), ('linear', thr_l)):
            lo, hi = -9.0, -1.0
            curve = []
            for _ in range(10):
                mid = 0.5 * (lo + hi)
                seg1 = inject(noise_segments, mid, np.log10(xi), rng)
                lp1 = log_prob_grid(posterior, features(seg1))
                idx1 = stacks(M, N, R, rng, replace)
                c1, l1 = combined_stats(lp1, idx1)
                pdet = float(np.mean((c1 if rule == 'combined' else l1) > thr))
                curve.append((mid, pdet))
                if pdet >= 0.5: hi = mid
                else: lo = mid
            lims[rule] = 0.5 * (lo + hi)
            curves[rule] = sorted(curve)
        out[str(N)] = {'thr_combined': float(thr_c), 'thr_linear': float(thr_l), 'limit_combined': lims['combined'],
                       'limit_linear': lims['linear'], 'resample_with_replacement': bool(replace), 'synthetic': synthetic,
                       'noise_stat_combined_median': float(np.median(c0)), 'noise_stat_linear_median': float(np.median(l0)),
                       'bisection': curves}
        log(f'   N={N:<6d} limit combined {lims["combined"]:.2f}  linear {lims["linear"]:.2f}')
    return out

def coverage(noise_segments, posterior, N, rng, log, ntrial=200):
    """P-P check of the combined posterior: fraction of trials in which the true log10 Omega lies inside the
    central credible interval of level p, for p = 0.1 ... 0.9 (marginal over xi), on the 0.02 dex grid.
    Also returns the Kolmogorov distance of the PIT values from uniform, the same check for the xi marginal,
    and the bias and width of the combined log10 Omega marginal (posterior mean - truth, posterior std)."""
    M = noise_segments.shape[0]
    levels = np.linspace(0.1, 0.9, 9); hits = np.zeros(9); hits_x = np.zeros(9)
    qs, qxs, bias, width, truths = [], [], [], [], []
    og = FINE_LOGOMEGA_GRID
    for t in range(ntrial):
        o, x = rng.uniform(-8, -1), rng.uniform(-3, 0)
        idx = rng.choice(M, size=N, replace=N > M // 4)
        seg1 = inject(noise_segments[idx], o, x, rng)
        lp1 = log_prob_grid(posterior, features(seg1), grid=FINE_GRID)
        S = lp1.sum(axis=0); S -= S.max(); w = np.exp(S); w /= w.sum()
        marg = w.sum(axis=1); cdf = np.cumsum(marg)
        q = np.interp(o, og, cdf - 0.5 * marg)           # CDF at the grid points taken mid-cell
        hits += (np.abs(q - 0.5) <= levels / 2)
        margx = w.sum(axis=0); cdfx = np.cumsum(margx)
        qx = np.interp(x, LOGXI_GRID, cdfx - 0.5 * margx)
        hits_x += (np.abs(qx - 0.5) <= levels / 2)
        m1 = float((marg * og).sum()); sd = float(np.sqrt(max((marg * og ** 2).sum() - m1 ** 2, 0.0)))
        qs.append(q); qxs.append(qx); bias.append(m1 - o); width.append(sd); truths.append(o)
    pp = hits / ntrial; ppx = hits_x / ntrial
    qs_sorted = np.sort(qs); ks = float(np.max(np.abs(qs_sorted - (np.arange(1, ntrial + 1) - 0.5) / ntrial)))
    bias, width, truths = np.array(bias), np.array(width), np.array(truths)
    inside = truths > -7.5                                    # exclude injections at the prior floor (noise-like)
    log(f'   coverage N={N}: ' + ' '.join(f'{l:.1f}:{p:.2f}' for l, p in zip(levels, pp)) +
        f'  KS={ks:.3f}  bias={np.median(bias[inside]):+.3f} (|bias| med {np.median(np.abs(bias[inside])):.3f})  width={np.median(width[inside]):.3f}')
    return {'levels': levels.tolist(), 'empirical': pp.tolist(), 'empirical_xi': ppx.tolist(), 'ntrial': ntrial,
            'ks_omega': ks, 'ks_95pct_critical': float(1.36 / np.sqrt(ntrial)), 'max_abs_dev': float(np.max(np.abs(pp - levels))),
            'bias_median': float(np.median(bias[inside])), 'abs_bias_median': float(np.median(np.abs(bias[inside]))),
            'bias_p16_p84': [float(v) for v in np.percentile(bias[inside], [16, 84])],
            'width_median': float(np.median(width[inside])), 'n_inside': int(inside.sum()),
            'grid_step_dex': float(og[1] - og[0])}

def segments_from_noise(noise, nseg, rng, n=8192):
    """Non-overlapping segments (as many as fit), or random starts if more are requested."""
    T = noise.shape[1]; kmax = T // n
    if nseg <= kmax:
        starts = np.arange(kmax)[:nseg] * n
    else:
        starts = rng.integers(0, T - n, size=nseg)
    return np.stack([noise[:, s:s + n] for s in starts])

def gains_for(entry_by_seed, N_list, log):
    """Gains Trad - ING per N and rule from a {seed: {'ing': entry, 'trad': entry}} dict (seeds may lack trad)."""
    g = {}
    for xi in XI_LIST:
        g[str(xi)] = {}
        for N in N_list:
            for rule in ('combined', 'linear'):
                ing = {s: e['ing']['limits'][str(xi)][str(N)][f'limit_{rule}'] for s, e in entry_by_seed.items()
                       if 'ing' in e and str(N) in e['ing']['limits'].get(str(xi), {})}
                tr = {s: e['trad']['limits'][str(xi)][str(N)][f'limit_{rule}'] for s, e in entry_by_seed.items()
                      if 'trad' in e and str(N) in e['trad']['limits'].get(str(xi), {})}
                if not ing or not tr:
                    continue
                pairs = {s: tr[s] - ing[s] for s in ing if s in tr}
                g[str(xi)][f'{N}_{rule}'] = {
                    'median': float(np.median(list(pairs.values()))) if pairs else None,
                    'per_seed': pairs,
                    'median_trad_minus_median_ing': float(np.median(list(tr.values())) - np.median(list(ing.values()))),
                    'ing_limits': ing, 'trad_limits': tr}
    return g

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='O3a,O3b,O4a')
    ap.add_argument('--stretches', default='0', help='stretch indices within each run: 0 = reference, 1-4 = rev1x')
    ap.add_argument('--seeds', default='1400,1401,1402')
    ap.add_argument('--synthetic', action='store_true', help='also run N in N_LIST_SYN on synthetic whitened Gaussian noise')
    ap.add_argument('--include-diverged', action='store_true', help='keep the Trad seeds that diverged in the rev2 pipeline')
    ap.add_argument('--resume', action='store_true', help='continue from an existing --out file')
    ap.add_argument('--R', type=int, default=2000, help='stacks per threshold / detection estimate')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--out', default='option_b_results.json')
    args = ap.parse_args()
    t0 = time.time()
    def log(s):
        print(f'[{time.time()-t0:7.1f}s] {s}', flush=True)

    if args.selftest:
        _selftest(log); return

    rng = default_rng(20261031)
    res = {'expectation_stated_in_advance': 'gain < 0.1 dex within 16 min at xi=1e-2; ~0.3 dex at 16 min and ~0.1 dex at 3 h at xi=1e-3',
           'criterion': 'Delta_comb >= 0.1 dex at the longest stack', 'grid': {'log10_omega': LOGOMEGA_GRID.tolist(), 'log10_xi': LOGXI_GRID.tolist()},
           'feature_order': 'C_HL, log1p|kappa_H1|, log1p|kappa_L1|, log10(var_H1 var_L1) (utils_rev1.Simulator.compute_features)',
           'networks': f'{TAG_REF} / {TAG_X}', 'R': args.R, 'N_real': N_LIST_REAL, 'N_synthetic': N_LIST_SYN if args.synthetic else [],
           'stretches': {}}
    if args.resume and os.path.exists(args.out):
        res = json.load(open(args.out)); log(f'resuming from {args.out}')
    syn = None
    for run in args.runs.split(','):
        for si in [int(s) for s in args.stretches.split(',')]:
            stretch = stretch_name(run, si)
            noise = load_eval_noise(run, si)
            segs = segments_from_noise(noise, 246, rng)
            log(f'{stretch}: eval noise {noise.shape}, {segs.shape[0]} segments, sigma1 = {_S["sigma1"]:.4f}, mode = {_S["mode"]}')
            st = res['stretches'].setdefault(stretch, {'run': run, 'sigma1': _S['sigma1'], 'seeds': {}})
            for seed in [int(s) for s in args.seeds.split(',')]:
                ent = st['seeds'].setdefault(str(seed), {})
                for fs in ('ing', 'trad'):
                    if fs in ent and ent[fs].get('complete'):
                        log(f'{stretch} seed {seed} {fs}: already done'); continue
                    post = load_posterior(run, seed, fs, si)
                    if post.diverged and not args.include_diverged:
                        log(f'{stretch} seed {seed} {fs}: skipped (diverged in the rev2 pipeline)')
                        ent[fs + '_skipped'] = 'diverged Trad seed'; continue
                    log(f'{stretch} seed {seed} {fs}: coverage on real noise')
                    cov = {str(N): coverage(segs, post, N, rng, log) for N in (1, 10, 100)}
                    entry = {'coverage': cov, 'limits': {}, 'model': os.path.relpath(post.path, SGWB1), 'idx': post.idx,
                             'diverged_in_rev2': post.diverged}
                    for xi in XI_LIST:
                        log(f'{stretch} seed {seed} {fs} xi={xi:g}: real noise')
                        entry['limits'][str(xi)] = run_one(segs, post, xi, N_LIST_REAL, rng, log, R=args.R)
                        if args.synthetic:
                            if syn is None:
                                syn = synthetic_noise(N_LIST_SYN[-1]); log(f'synthetic noise {syn.shape} ready')
                            log(f'{stretch} seed {seed} {fs} xi={xi:g}: synthetic noise (check single-segment coverage first)')
                            entry.setdefault('coverage_synthetic', coverage(syn[:246], post, 1, rng, log))
                            entry['limits'][str(xi)].update(run_one(syn, post, xi, N_LIST_SYN, rng, log, R=args.R, synthetic=True))
                    entry['complete'] = True
                    ent[fs] = entry
                    json.dump(res, open(args.out, 'w'), indent=1)
            st['gain_trad_minus_ing'] = gains_for(st['seeds'], N_LIST_REAL + (N_LIST_SYN if args.synthetic else []), log)
            log(f'{stretch}: gains (median over seed pairs) ' + json.dumps(
                {k: {kk: (round(v['median'], 2) if v['median'] is not None else None) for kk, v in vv.items()} for k, vv in st['gain_trad_minus_ing'].items()}))
            json.dump(res, open(args.out, 'w'), indent=1)
    log(f'written {args.out}')

def _selftest(log):
    """Exercise the generic machinery on a mock posterior: Gaussian around a 'measured' log10 Omega with
    width 0.3 dex, uninformative in xi, and a mock injector/feature extractor.  Checks that the combined
    posterior narrows as 1/sqrt(N), that the limit falls with N, and that coverage is near nominal."""
    global features, log_prob_grid, inject
    def features(seg):
        v = seg.astype(np.float64).var(axis=2).mean(axis=1)          # per-segment power
        return np.stack([np.zeros(len(v)), np.log(v), np.zeros(len(v)), np.zeros(len(v))], 1)
    def inject(seg, lo, lx, rng):
        s2 = 10 ** lo * 1e3                                           # mock calibration: Omega=1e-3 <-> s2=1
        return seg + rng.standard_normal(seg.shape).astype(np.float32) * np.sqrt(s2)
    def log_prob_grid(post, f, grid=None):
        og = FINE_LOGOMEGA_GRID if grid is not None else LOGOMEGA_GRID
        est = np.log10(np.clip(np.exp(f[:, 1]) - 1.0, 1e-9, None) / 1e3)   # estimated log10 Omega from excess power
        sig = 0.3 + 0.0 * est
        lp = -0.5 * ((og[None, :, None] - est[:, None, None]) / sig[:, None, None]) ** 2
        return np.broadcast_to(lp, (len(f), og.size, LOGXI_GRID.size)).copy()
    # the matmul form of combined_stats must agree with the explicit N-fold sum
    rng = default_rng(2)
    lp = rng.standard_normal((50, LOGOMEGA_GRID.size, LOGXI_GRID.size))
    idx = rng.integers(0, 50, size=(7, 12))
    S = sum(lp[idx[:, j]] for j in range(12)); S -= S.max(axis=(1, 2), keepdims=True)
    w = np.exp(S); w /= w.sum(axis=(1, 2), keepdims=True); comb_ref = (w * LOGO[None]).sum(axis=(1, 2))
    comb, lin = combined_stats(lp, idx)
    assert np.allclose(comb, comb_ref, atol=1e-9), (comb, comb_ref)
    rng = default_rng(1)
    segs = rng.standard_normal((246, 2, 8192)).astype(np.float32)
    out = run_one(segs, None, 1e-3, [1, 10, 100], rng, log, R=500)
    l1, l100 = out['1']['limit_combined'], out['100']['limit_combined']
    assert l100 < l1 - 0.5, (l1, l100)
    cov = coverage(segs, None, 10, rng, log, ntrial=100)
    assert abs(cov['empirical'][4] - 0.5) < 0.2
    log('selftest OK')

if __name__ == '__main__':
    main()
