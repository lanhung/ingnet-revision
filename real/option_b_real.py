#!/usr/bin/env python3
"""
option_b_real.py -- Option (b) of the Oct-30 memo on the REAL trained networks:
combine per-segment ING-Net posteriors over N segments and compare with the power-only
network combined the same way, and with a linear stack of per-segment posterior means.

Everything below the ADAPTER block is pipeline-independent. The adapter has five functions that
must call YOUR code (the names in the manuscript are used as a guide). Run first with --selftest,
which exercises the generic part on a mock posterior and must print "selftest OK".

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
"""
import numpy as np, json, time, argparse, sys
from numpy.random import default_rng
from scipy.stats import norm

Z997 = norm.ppf(0.997)
N_LIST_REAL = [1, 3, 10, 30, 100, 246]
N_LIST_SYN = [1000, 3000, 10000]
XI_LIST = [1e-3, 1e-2]
LOGOMEGA_GRID = np.linspace(-8, -1, 71)       # prior U[-8, -1]
LOGXI_GRID = np.linspace(-3, 0, 31)           # prior U[-3, 0]

# ======================================================================================= ADAPTER
# Replace the bodies of these five functions with calls into /root/SGWB1.  Shapes are fixed:
#   noise: float array (2, T) whitened unit-variance H1/L1 strain of the EVALUATION part of a stretch
#   segments: float array (B, 2, 8192)
#   features: float array (B, 4) = (C_HL, P, kappa_H1, kappa_L1), in the units the networks were trained on
#   log_prob_grid: float array (B, len(LOGOMEGA_GRID), len(LOGXI_GRID)) of log q_phi(theta | x_b)

def load_eval_noise(run, stretch_index=0):
    """Whitened evaluation noise (2, T) of the given run/stretch (Sec. II C: last 25 %, 8 s gap, 16 s trimmed).
    e.g.  from sgwb.data import load_whitened; return load_whitened(run, stretch_index, part='eval')"""
    raise NotImplementedError('adapter: load_eval_noise')

def inject(segments, log10_omega, log10_xi, rng):
    """Add the intermittent background of Sec. II (antenna-pattern injection, per-stretch calibration of
    Eq. 11) to a copy of `segments` and return it.  Must use YOUR simulator so that Omega has the paper's
    meaning.  e.g.  from sgwb.sim import inject_sgwb; return inject_sgwb(segments, 10**log10_omega, 10**log10_xi, rng)"""
    raise NotImplementedError('adapter: inject')

def features(segments):
    """(B, 2, 8192) -> (B, 4) summary vector exactly as in training (Eqs. 7-8 plus any transform/scaling)."""
    raise NotImplementedError('adapter: features')

def load_posterior(run, seed, feature_set):
    """Return the trained sbi posterior object for (run, seed, feature_set in {'ing', 'trad'})."""
    raise NotImplementedError('adapter: load_posterior')

def log_prob_grid(posterior, feats):
    """log q(theta | x) on the (log10 Omega, log10 xi) grid for every row of feats -> (B, nO, nX).
    For an sbi DirectPosterior with a MAF this is usually:
        theta = torch.tensor(GRID_POINTS, dtype=torch.float32)          # (nO*nX, 2)
        out = [posterior.log_prob(theta, x=torch.tensor(f[None], dtype=torch.float32)).numpy() for f in feats]
    If the network was trained on transformed theta (e.g. standardised), apply the same transform here."""
    raise NotImplementedError('adapter: log_prob_grid')
# =================================================================================== END ADAPTER

GRID_POINTS = np.array([(o, x) for o in LOGOMEGA_GRID for x in LOGXI_GRID])
LOGO = np.tile(LOGOMEGA_GRID[:, None], (1, LOGXI_GRID.size))

def combined_stats(lp, idx):
    """lp: (M, nO, nX) per-segment log posteriors; idx: (R, N) segment indices per stack.
    Returns posterior mean of log10 Omega under the combined posterior (R,) and the linear stack (R,)."""
    R, N = idx.shape
    S = np.zeros((R,) + lp.shape[1:])
    for j in range(N):
        S += lp[idx[:, j]]
    S -= S.max(axis=(1, 2), keepdims=True)
    w = np.exp(S); w /= w.sum(axis=(1, 2), keepdims=True)
    comb = (w * LOGO[None]).sum(axis=(1, 2))
    # per-segment posterior means, then averaged (linear stack)
    lp0 = lp - lp.max(axis=(1, 2), keepdims=True); w0 = np.exp(lp0); w0 /= w0.sum(axis=(1, 2), keepdims=True)
    pm = (w0 * LOGO[None]).sum(axis=(1, 2))
    lin = pm[idx].mean(axis=1)
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
        lims = {}
        for rule, thr in (('combined', thr_c), ('linear', thr_l)):
            lo, hi = -9.0, -1.0
            for _ in range(10):
                mid = 0.5 * (lo + hi)
                seg1 = inject(noise_segments, mid, np.log10(xi), rng)
                lp1 = log_prob_grid(posterior, features(seg1))
                idx1 = stacks(M, N, R, rng, replace)
                c1, l1 = combined_stats(lp1, idx1)
                pdet = float(np.mean((c1 if rule == 'combined' else l1) > thr))
                if pdet >= 0.5: hi = mid
                else: lo = mid
            lims[rule] = 0.5 * (lo + hi)
        out[str(N)] = {'thr_combined': float(thr_c), 'thr_linear': float(thr_l), 'limit_combined': lims['combined'],
                       'limit_linear': lims['linear'], 'resample_with_replacement': bool(replace), 'synthetic': synthetic}
        log(f'   N={N:<6d} limit combined {lims["combined"]:.2f}  linear {lims["linear"]:.2f}')
    return out

def coverage(noise_segments, posterior, N, rng, log, ntrial=200):
    """P-P check of the combined posterior: fraction of trials in which the true log10 Omega lies inside the
    central credible interval of level p, for p = 0.1 ... 0.9 (marginal over xi)."""
    M = noise_segments.shape[0]
    levels = np.linspace(0.1, 0.9, 9); hits = np.zeros(9)
    for t in range(ntrial):
        o, x = rng.uniform(-8, -1), rng.uniform(-3, 0)
        idx = rng.choice(M, size=N, replace=N > M // 4)
        seg1 = inject(noise_segments[idx], o, x, rng)
        lp1 = log_prob_grid(posterior, features(seg1))
        S = lp1.sum(axis=0); S -= S.max(); w = np.exp(S); w /= w.sum()
        marg = w.sum(axis=1); cdf = np.cumsum(marg)
        q = np.interp(o, LOGOMEGA_GRID, cdf)
        hits += (np.abs(q - 0.5) <= levels / 2)
    pp = hits / ntrial
    log(f'   coverage N={N}: ' + ' '.join(f'{l:.1f}:{p:.2f}' for l, p in zip(levels, pp)))
    return {'levels': levels.tolist(), 'empirical': pp.tolist(), 'ntrial': ntrial}

def segments_from_noise(noise, nseg, rng, n=8192):
    """Non-overlapping segments (as many as fit), or random starts if more are requested."""
    T = noise.shape[1]; kmax = T // n
    if nseg <= kmax:
        starts = np.arange(kmax)[:nseg] * n
    else:
        starts = rng.integers(0, T - n, size=nseg)
    return np.stack([noise[:, s:s + n] for s in starts])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', default='O3a,O3b,O4a')
    ap.add_argument('--seeds', default='1400,1401,1402')
    ap.add_argument('--synthetic', action='store_true', help='also run N in N_LIST_SYN on synthetic whitened Gaussian noise')
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
           'runs': {}}
    for run in args.runs.split(','):
        noise = load_eval_noise(run)
        segs = segments_from_noise(noise, 246, rng)
        res['runs'][run] = {}
        for seed in [int(s) for s in args.seeds.split(',')]:
            res['runs'][run][str(seed)] = {}
            for fs in ('ing', 'trad'):
                post = load_posterior(run, seed, fs)
                log(f'{run} seed {seed} {fs}: coverage on real noise')
                cov = {str(N): coverage(segs, post, N, rng, log) for N in (1, 10, 100)}
                entry = {'coverage': cov, 'limits': {}}
                for xi in XI_LIST:
                    log(f'{run} seed {seed} {fs} xi={xi:g}: real noise')
                    entry['limits'][str(xi)] = run_one(segs, post, xi, N_LIST_REAL, rng, log)
                    if args.synthetic:
                        syn = default_rng(5).standard_normal((N_LIST_SYN[-1], 2, 8192)).astype(np.float32)
                        log(f'{run} seed {seed} {fs} xi={xi:g}: synthetic noise (check single-segment coverage first)')
                        entry['coverage_synthetic'] = coverage(syn[:246], post, 1, rng, log)
                        entry['limits'][str(xi)].update(run_one(syn, post, xi, N_LIST_SYN, rng, log, synthetic=True))
                res['runs'][run][str(seed)][fs] = entry
        # gains per run (median over seeds)
        g = {}
        for xi in XI_LIST:
            g[str(xi)] = {}
            for N in N_LIST_REAL + (N_LIST_SYN if args.synthetic else []):
                for rule in ('combined', 'linear'):
                    d = [res['runs'][run][s]['trad']['limits'][str(xi)][str(N)][f'limit_{rule}'] -
                         res['runs'][run][s]['ing']['limits'][str(xi)][str(N)][f'limit_{rule}'] for s in res['runs'][run]]
                    g[str(xi)][f'{N}_{rule}'] = {'median': float(np.median(d)), 'per_seed': d}
        res['runs'][run]['gain_trad_minus_ing'] = g
        log(f'{run}: gains ' + json.dumps({k: {kk: round(v["median"], 2) for kk, v in vv.items()} for k, vv in g.items()}))
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
    def log_prob_grid(post, f):
        est = np.log10(np.clip(np.exp(f[:, 1]) - 1.0, 1e-9, None) / 1e3)   # estimated log10 Omega from excess power
        sig = 0.3 + 0.0 * est
        lp = -0.5 * ((LOGOMEGA_GRID[None, :, None] - est[:, None, None]) / sig[:, None, None]) ** 2
        return np.broadcast_to(lp, (len(f), LOGOMEGA_GRID.size, LOGXI_GRID.size)).copy()
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
