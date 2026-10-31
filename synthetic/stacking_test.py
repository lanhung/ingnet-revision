#!/usr/bin/env python3
"""
stacking_test.py -- Does the per-segment kurtosis gain of ING-Net survive combining many segments,
and does the answer depend on HOW segments are combined?

One synthetic data set, signal model of the ING-Net manuscript (rev2):
  * two detectors (H1, L1), white unit-variance Gaussian noise, 4 s segments (n = 8192 at 2048 Hz)
  * events: Poisson start times (rate xi/tau per sample), Hann-windowed white Gaussian bursts of tau = 8 samples,
    plus/cross polarisations projected with the real H1/L1 antenna patterns (isotropic sky, uniform psi),
    per-event per-sample variance a^2 = sigma_s^2/xi, normalised so that <A> = 1  (time-averaged variance = sigma_s^2)
Per-segment summaries:  C_HL, P = log power, kappa_H, kappa_L  (Eqs. 7-8 of the manuscript)

Three combination rules over N segments, each applied to a known (sigma_s^2, xi):
  LIN : stack the summaries linearly (average over N), optimal linear (Fisher) combination, known signal shape
        -- what the Oct-26 scaling test did; what LVK does with the cross-correlation
  NL  : product over segments of a per-segment likelihood of the summary vector,
        p(x | sigma, xi) = sum_k Poisson(k; lambda) GMM_k(x) fitted on segments with exactly k events
        -- the Lawrence et al. construction; with a uniform prior this is what multiplying ING-Net posteriors does
  DF  : Drasco-Flanagan-type two-component mixture likelihood on the FULL two-detector time series,
        sliding Hann-window implementation with the sky-averaged 2x2 signal covariance (gamma_HL(0) = -0.89)
        -- the analytic non-Gaussian benchmark asked for in referee comment 10 (Gaussian-noise version)

Summary sets:  cc = (C) ; trad = (C, P) ; ing = (C, P, kappa_H, kappa_L)
Methods:       cc_lin, trad_lin, ing_lin, trad_nl, ing_nl, df

Detection: 0.3 % false-alarm probability per stack (99.7 % quantile of the stacked statistic on noise-only stacks),
50 % detection probability defines the limit sigma_50(N).  For N <= 1000 the stacked statistic is bootstrapped
from per-segment pools; for all N a central-limit estimate N_50(sigma) = (z s0 / dm)^2 is also computed with
paired (same-noise) pools.  Durations: T = 4 N s.
"""
import numpy as np, json, time, sys, os, argparse
from numpy.random import default_rng
from scipy.special import logsumexp, gammaln
from scipy.stats import norm, poisson
try:
    from sklearn.mixture import GaussianMixture
    HAVE_SK = True
except Exception:
    HAVE_SK = False

N_SAMP, TAU, FS = 8192, 8, 2048
Z997 = norm.ppf(0.997)             # 2.748, one-sided 0.3 % false-alarm
METHODS = ['cc_lin', 'trad_lin', 'ing_lin', 'trad_nl', 'ing_nl', 'df']
COLS = {'cc': [0], 'trad': [0, 1], 'ing': [0, 1, 2, 3]}

# ---------------------------------------------------------------- burst envelope
jj = np.arange(TAU)
W = 0.5 * (1 - np.cos(2 * np.pi * (jj + 0.5) / TAU))
W = W / np.sqrt(np.mean(W ** 2))                       # <w^2> = 1 over the burst
C_W = float(np.mean(W ** 4) / np.mean(W ** 2) ** 2)

# ---------------------------------------------------------------- antenna patterns (LAL geometry, azimuth clockwise from North)
def detector_tensor(lat_deg, lon_deg, az_x_deg, az_y_deg):
    lat, lon = np.radians(lat_deg), np.radians(lon_deg)
    E = np.array([-np.sin(lon), np.cos(lon), 0.0])
    Nn = np.array([-np.sin(lat) * np.cos(lon), -np.sin(lat) * np.sin(lon), np.cos(lat)])
    def arm(az_deg):
        az = np.radians(az_deg)
        return np.cos(az) * Nn + np.sin(az) * E
    x, y = arm(az_x_deg), arm(az_y_deg)
    return 0.5 * (np.outer(x, x) - np.outer(y, y))

D_H = detector_tensor(46.4551, -119.4077, 324.0, 234.0)
D_L = detector_tensor(30.5629, -90.7742, 252.28, 162.28)

def antenna_pool(rng, M):
    cos_t = rng.uniform(-1, 1, M); sin_t = np.sqrt(1 - cos_t ** 2)
    phi = rng.uniform(0, 2 * np.pi, M); psi = rng.uniform(0, np.pi, M)
    u = np.stack([np.cos(phi) * cos_t, np.sin(phi) * cos_t, -sin_t], 1)     # theta-hat
    v = np.stack([-np.sin(phi), np.cos(phi), np.zeros(M)], 1)                 # phi-hat
    m = np.cos(psi)[:, None] * u + np.sin(psi)[:, None] * v
    nn = -np.sin(psi)[:, None] * u + np.cos(psi)[:, None] * v
    e_plus = m[:, :, None] * m[:, None, :] - nn[:, :, None] * nn[:, None, :]
    e_cross = m[:, :, None] * nn[:, None, :] + nn[:, :, None] * m[:, None, :]
    F = {}
    for name, D in [('H', D_H), ('L', D_L)]:
        F[name] = [np.einsum('ij,mij->m', D, e_plus), np.einsum('ij,mij->m', D, e_cross)]
    A_H = F['H'][0] ** 2 + F['H'][1] ** 2
    norm_ = np.sqrt(np.mean(A_H))                       # <A> = 2/5 for a single detector
    for name in F:
        F[name] = [F[name][0] / norm_, F[name][1] / norm_]
    A_H = F['H'][0] ** 2 + F['H'][1] ** 2
    gamma0 = float(np.mean(F['H'][0] * F['L'][0] + F['H'][1] * F['L'][1]) / np.mean(A_H))
    c_F = float(np.mean(A_H ** 2) / np.mean(A_H) ** 2)
    return F, gamma0, c_F

# ---------------------------------------------------------------- segments, injection, features
def make_noise(rng, B):
    return rng.standard_normal((B, 2, N_SAMP), dtype=np.float32)

def inject(x, rng, k_per_seg, a2, ant):
    """Add k_per_seg[b] events to segment b (in place). Per-event per-sample variance a2 (<A> = 1)."""
    B = x.shape[0]
    E = int(k_per_seg.sum())
    if E == 0:
        return x
    seg = np.repeat(np.arange(B), k_per_seg)
    t0 = rng.integers(-TAU + 1, N_SAMP, size=E)                  # events may straddle the segment edges
    idx = rng.integers(0, ant['H'][0].size, size=E)
    sa = np.sqrt(a2)
    hp = rng.standard_normal((E, TAU)) * W * sa
    hc = rng.standard_normal((E, TAU)) * W * sa
    tt = t0[:, None] + np.arange(TAU)[None, :]
    ok = (tt >= 0) & (tt < N_SAMP)
    flat = (seg[:, None] * N_SAMP + tt)[ok]
    for d, name in enumerate(['H', 'L']):
        Fp, Fc = ant[name]
        s = Fp[idx][:, None] * hp + Fc[idx][:, None] * hc
        add = np.bincount(flat, weights=s[ok], minlength=B * N_SAMP).reshape(B, N_SAMP)
        x[:, d, :] += add.astype(np.float32)
    return x

def features(x):
    """(B,2,n) -> (B,4): C_HL, P, kappa_H, kappa_L."""
    x = x.astype(np.float64)
    d = x - x.mean(axis=2, keepdims=True)
    v = (d ** 2).mean(axis=2)
    q = (d ** 4).mean(axis=2)
    kap = q / v ** 2 - 3.0
    C = (d[:, 0] * d[:, 1]).mean(axis=1) / np.sqrt(v[:, 0] * v[:, 1])
    P = np.log(v.mean(axis=1))
    return np.stack([C, P, kap[:, 0], kap[:, 1]], 1)

# ---------------------------------------------------------------- Drasco-Flanagan-type sliding-window likelihood
def df_score(x, a2, p, gamma0):
    """log p(x | events: Poisson, rate p per window start, per-event variance a2, sky-averaged covariance) - log p(x | noise).
    Per window of TAU samples at start t, sample j has covariance I + a2 w_j^2 Mbar, Mbar = [[1, g],[g, 1]];
    eigenvectors (1,1)/sqrt2 (eigenvalue 1+g) and (1,-1)/sqrt2 (1-g)."""
    lam = np.array([1 + gamma0, 1 - gamma0])
    c = a2 * W ** 2
    beta = [c * lam[m] / (1 + c * lam[m]) for m in range(2)]
    D = float(np.sum(np.log1p(c * lam[0]) + np.log1p(c * lam[1])))
    xH = x[:, 0].astype(np.float64); xL = x[:, 1].astype(np.float64)
    q1 = 0.5 * (xH + xL) ** 2
    q2 = 0.5 * (xH - xL) ** 2
    nwin = N_SAMP - TAU + 1
    L = np.full((x.shape[0], nwin), -0.5 * D)
    for j in range(TAU):
        L += 0.5 * (beta[0][j] * q1[:, j:j + nwin] + beta[1][j] * q2[:, j:j + nwin])
    return np.logaddexp(np.log1p(-p), np.log(p) + L).sum(axis=1)

# ---------------------------------------------------------------- per-segment likelihood of the summary vector
def fit_gmm(X, ncomp):
    """Return list of (log weight, mean, cov)."""
    X = np.asarray(X, float)
    d = X.shape[1]
    if HAVE_SK and ncomp > 1 and X.shape[0] >= 60 * ncomp:
        g = GaussianMixture(n_components=ncomp, covariance_type='full', reg_covar=1e-7,
                            n_init=1, random_state=0, max_iter=300).fit(X)
        return [(float(np.log(g.weights_[i])), g.means_[i].copy(), g.covariances_[i].copy()) for i in range(ncomp)]
    mu = X.mean(0); cov = np.cov(X.T).reshape(d, d) + 1e-9 * np.eye(d)
    return [(0.0, mu, cov)]

def gmm_logpdf(X, comps):
    X = np.asarray(X, float)
    M, d = X.shape
    out = np.empty((M, len(comps)))
    for i, (lw, mu, cov) in enumerate(comps):
        Lc = np.linalg.cholesky(cov)
        y = np.linalg.solve(Lc, (X - mu).T)
        out[:, i] = lw - 0.5 * (y ** 2).sum(0) - np.log(np.diag(Lc)).sum() - 0.5 * d * np.log(2 * np.pi)
    return logsumexp(out, axis=1)

class Hypothesis:
    """Everything that depends on (sigma_s^2, xi): mixture model of the summaries, Fisher directions."""
    def __init__(self, rng, ant, xi, sig2, feats0_fit, comps0, MK, ncomp, gamma0):
        self.xi, self.sig2 = xi, sig2
        self.a2 = sig2 / xi
        self.lam = xi * N_SAMP / TAU                     # expected events per segment
        self.p = xi / TAU                                 # event probability per window start
        self.gamma0 = gamma0
        # event-count stratification
        if xi >= 0.5:
            ks = [None]                                   # Poisson sims, single GMM (Gaussian regime)
        else:
            kmax = int(poisson.ppf(1 - 1e-5, self.lam))
            kmax = max(kmax, 1)
            ks = list(range(0, kmax + 1))
        self.comps = {'trad': [], 'ing': []}
        mu1 = np.zeros(4); wsum = 0.0
        for k in ks:
            if k is None:
                kk = rng.poisson(self.lam, MK); logw = 0.0
                X = features(inject(make_noise(rng, MK), rng, kk, self.a2, ant))
            elif k == 0:
                X = feats0_fit; logw = poisson.logpmf(0, self.lam)
            else:
                X = features(inject(make_noise(rng, MK), rng, np.full(MK, k), self.a2, ant))
                logw = poisson.logpmf(k, self.lam)
            w = np.exp(logw); mu1 += w * X.mean(0); wsum += w
            for name in ('trad', 'ing'):
                Xc = X[:, COLS[name]]
                cs = comps0[name] if k == 0 else fit_gmm(Xc, ncomp)
                self.comps[name] += [(logw + lw, mu, cov) for (lw, mu, cov) in cs]
        self.mu1 = mu1 / wsum
        self.mu0 = feats0_fit.mean(0)
        self.Sig0 = np.cov(feats0_fit.T)
        self.wdir = {}
        for name, cols in COLS.items():
            dm = (self.mu1 - self.mu0)[cols]
            S = self.Sig0[np.ix_(cols, cols)]
            self.wdir[name] = np.linalg.solve(S, dm)
        self.comps0 = comps0

    def score(self, x, f):
        """Per-segment statistics for all methods, given raw segments x and their features f."""
        out = {}
        for name in COLS:
            out[name + '_lin'] = f[:, COLS[name]] @ self.wdir[name]
        for name in ('trad', 'ing'):
            Xc = f[:, COLS[name]]
            out[name + '_nl'] = gmm_logpdf(Xc, self.comps[name]) - gmm_logpdf(Xc, self.comps0[name])
        out['df'] = df_score(x, self.a2, self.p, self.gamma0)
        return out

# ---------------------------------------------------------------- stacking
def stack_pdet_boot(h0, h1, N, rng, R=3000):
    if N == 1:
        thr = np.quantile(h0, 0.997)
        return float(np.mean(h1 > thr))
    s0 = rng.choice(h0, size=(R, N)).sum(1)
    s1 = rng.choice(h1, size=(R, N)).sum(1)
    thr = np.quantile(s0, 0.997)
    return float(np.mean(s1 > thr))

def n50_clt(h0, h1):
    """Stack length at which this sigma is the 50 %-detection limit (paired pools)."""
    dm = float(np.mean(h1 - h0)); s0 = float(np.std(h0))
    if dm <= 0:
        return np.inf
    return (Z997 * s0 / dm) ** 2

def crossing(logs, y, level, increasing=True):
    """First crossing of y(logs) through level, linear interpolation; NaN if none."""
    y = np.asarray(y, float); logs = np.asarray(logs, float)
    for i in range(1, len(y)):
        a, b = y[i - 1], y[i]
        if np.isnan(a) or np.isnan(b):
            continue
        if (a < level <= b) if increasing else (a > level >= b):
            return float(logs[i - 1] + (level - a) / (b - a) * (logs[i] - logs[i - 1]))
    return float('nan')

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--out', default='stacking_results.json')
    ap.add_argument('--ncomp', type=int, default=3)
    ap.add_argument('--xi', default='')
    ap.add_argument('--tag', default='')
    ap.add_argument('--grid', default='')
    args = ap.parse_args()
    t_start = time.time()
    rng = default_rng(20261030)

    if args.quick:
        XI = [1e-2, 1e-3]
        GRID = {1e-2: np.arange(-3.0, -1.2, 0.3), 1e-3: np.arange(-3.0, -1.2, 0.3)}
        M0, B, MK, MFIT = 1200, 300, 300, 1500
        NB = [1, 10, 100]
    else:
        XI = [1e-2, 1e-3, 1e-4, 1.0]
        GRID = {1e-2: np.arange(-4.3, -0.95, 0.1), 1e-3: np.arange(-4.3, -0.95, 0.1),
                1e-4: np.arange(-4.3, -0.95, 0.1), 1.0: np.arange(-4.3, -0.95, 0.2)}
        M0, B, MK, MFIT = 6000, 500, 800, 4000
        NB = [1, 3, 10, 30, 100, 300, 1000]
    N_ALL = [1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000]
    if args.xi:
        XI = [float(v) for v in args.xi.split(',')]
    if args.grid:
        lo, hi, st = [float(v) for v in args.grid.split(',')]
        GRID = {xi: np.arange(lo, hi + 1e-9, st) for xi in XI}

    ant, gamma0, c_F = antenna_pool(rng, 200000)
    log = open(f'stacking_progress{args.tag}.log', 'a')
    def say(s):
        msg = f'[{time.time()-t_start:7.1f}s] {s}'
        print(msg, flush=True); log.write(msg + '\n'); log.flush()
    say(f'gamma_HL(0) = {gamma0:.3f}  c_F = {c_F:.3f}  c_w = {C_W:.3f}  sklearn={HAVE_SK}')

    # independent noise sims for the k = 0 component and the Fisher baseline
    feats0_fit = features(make_noise(rng, MFIT))
    comps0 = {name: fit_gmm(feats0_fit[:, COLS[name]], args.ncomp) for name in ('trad', 'ing')}
    say(f'noise features: mean {feats0_fit.mean(0).round(4)}  std {feats0_fit.std(0).round(4)}')

    # phase 1: hypotheses
    hyps = {}
    for xi in XI:
        for ls in GRID[xi]:
            hyps[(xi, round(float(ls), 3))] = Hypothesis(rng, ant, xi, 10 ** ls, feats0_fit, comps0, MK, args.ncomp, gamma0)
        say(f'hypotheses fitted for xi={xi:g} ({len(GRID[xi])} amplitudes)')

    # phase 2: paired pools (same noise for H0 and H1)
    pools = {key: {m: [[], []] for m in METHODS} for key in hyps}
    nbatch = M0 // B
    for b in range(nbatch):
        brng = default_rng(1000 + b)
        x0 = make_noise(brng, B)
        f0 = features(x0)
        for key, H in hyps.items():
            kk = brng.poisson(H.lam, B)
            x1 = inject(x0.copy(), brng, kk, H.a2, ant)
            f1 = features(x1)
            s0 = H.score(x0, f0); s1 = H.score(x1, f1)
            for m in METHODS:
                pools[key][m][0].append(s0[m]); pools[key][m][1].append(s1[m])
        say(f'batch {b+1}/{nbatch} scored')
    for key in pools:
        for m in METHODS:
            pools[key][m] = [np.concatenate(pools[key][m][0]), np.concatenate(pools[key][m][1])]

    # phase 3: stacking
    res = {'gamma0': gamma0, 'c_F': c_F, 'c_w': C_W, 'M0': M0, 'MK': MK, 'ncomp': args.ncomp,
           'N_all': N_ALL, 'N_boot': NB, 'xi': XI, 'grid': {str(xi): [round(float(v), 3) for v in GRID[xi]] for xi in XI},
           'pdet_boot': {}, 'n50_clt': {}, 'limits_boot': {}, 'limits_clt': {}, 'limits': {}}
    srng = default_rng(7)
    for xi in XI:
        grid = [round(float(v), 3) for v in GRID[xi]]
        res['pdet_boot'][str(xi)] = {m: {str(N): [] for N in NB} for m in METHODS}
        res['n50_clt'][str(xi)] = {m: [] for m in METHODS}
        res.setdefault('moments', {})[str(xi)] = {m: [] for m in METHODS}
        for ls in grid:
            for m in METHODS:
                h0, h1 = pools[(xi, ls)][m]
                for N in NB:
                    res['pdet_boot'][str(xi)][m][str(N)].append(stack_pdet_boot(h0, h1, N, srng))
                res['n50_clt'][str(xi)][m].append(n50_clt(h0, h1))
                res['moments'][str(xi)][m].append([float(np.mean(h0)), float(np.std(h0)), float(np.mean(h1 - h0)), float(np.std(h1 - h0))])
        # limits
        res['limits_boot'][str(xi)] = {}
        res['limits_clt'][str(xi)] = {}
        res['limits'][str(xi)] = {}
        for m in METHODS:
            lb = {}
            for N in NB:
                lb[str(N)] = crossing(grid, res['pdet_boot'][str(xi)][m][str(N)], 0.5, increasing=True)
            lc = {}
            n50 = np.array(res['n50_clt'][str(xi)][m])
            logn = np.log10(np.where(np.isfinite(n50), n50, np.nan))
            for N in N_ALL:
                lc[str(N)] = crossing(grid, logn, np.log10(N), increasing=False)
            res['limits_boot'][str(xi)][m] = lb
            res['limits_clt'][str(xi)][m] = lc
            # headline: bootstrap up to 1000, CLT beyond
            res['limits'][str(xi)][m] = {str(N): (lb[str(N)] if N in NB else lc[str(N)]) for N in N_ALL}
        say(f'stacking done for xi={xi:g}')

    with open(args.out, 'w') as fh:
        json.dump(res, fh, indent=1)
    say(f'written {args.out}')

    # print summary table
    def show(xi):
        print(f'\n=== xi = {xi:g} : log10 sigma_50  (bootstrap N<=1000, CLT beyond) ===')
        print('N      T        ' + ' '.join(f'{m:>9s}' for m in METHODS) + '   d(ing_lin-trad_lin) d(ing_nl-trad_nl) d(df-trad_lin) d(df-cc_lin)')
        for N in N_ALL:
            L = res['limits'][str(xi)]
            vals = [L[m][str(N)] for m in METHODS]
            T = 4 * N
            Ts = f'{T:6.0f}s' if T < 3600 else (f'{T/3600:5.1f}h' if T < 86400 else f'{T/86400:5.1f}d')
            d1 = L['trad_lin'][str(N)] - L['ing_lin'][str(N)]
            d2 = L['trad_nl'][str(N)] - L['ing_nl'][str(N)]
            d3 = L['trad_lin'][str(N)] - L['df'][str(N)]
            d4 = L['cc_lin'][str(N)] - L['df'][str(N)]
            print(f'{N:<6d} {Ts:>8s} ' + ' '.join(f'{v:9.2f}' for v in vals) + f'   {d1:9.2f}         {d2:9.2f}        {d3:9.2f}      {d4:9.2f}')
    for xi in XI:
        show(xi)
    say('done')

if __name__ == '__main__':
    main()
