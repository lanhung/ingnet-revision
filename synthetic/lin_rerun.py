#!/usr/bin/env python3
"""Recompute the LIN (stacked-summary, Fisher) limits with ANALYTIC signal directions and noise covariance,
so that the stacked-summary results carry no Monte-Carlo noise from a fitted direction.
  dC = gamma s2/(1+s2),  dP = log(1+s2),  dkappa = 3 c_w c_F s2^2 / (xi (1+s2)^2)   [shot-noise 4th cumulant]
  Sigma0 = diag(1/n, 1/n, 24/n, 24/n)
Same noise seeds and injection stream as stacking_test.py, so the pools are paired with the main run."""
import numpy as np, json, sys, argparse
from numpy.random import default_rng
import stacking_test as st

ap = argparse.ArgumentParser(); ap.add_argument('--xi', required=True); ap.add_argument('--out', required=True)
ap.add_argument('--grid', default='-4.3,-1.0,0.1'); ap.add_argument('--M0', type=int, default=6000); ap.add_argument('--B', type=int, default=500)
args = ap.parse_args()
XI = [float(v) for v in args.xi.split(',')]
lo, hi, step = [float(v) for v in args.grid.split(',')]
GRID = np.arange(lo, hi + 1e-9, step)
N_ALL = [1, 3, 10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000]
NB = [1, 3, 10, 30, 100, 300, 1000]
rng = default_rng(20261030)
ant, gamma0, c_F = st.antenna_pool(rng, 200000)
n = st.N_SAMP
Sig0 = np.diag([1 / n, 1 / n, 24 / n, 24 / n])

def direction(xi, s2):
    dmu = np.array([gamma0 * s2 / (1 + s2), np.log1p(s2), 3 * st.C_W * c_F * s2 ** 2 / (xi * (1 + s2) ** 2),
                    3 * st.C_W * c_F * s2 ** 2 / (xi * (1 + s2) ** 2)])
    w = {}
    for name, cols in st.COLS.items():
        w[name] = np.linalg.solve(Sig0[np.ix_(cols, cols)], dmu[cols])
    return w

keys = [(xi, round(float(ls), 3)) for xi in XI for ls in GRID]
W = {k: direction(k[0], 10 ** k[1]) for k in keys}
pools = {k: {name: [[], []] for name in st.COLS} for k in keys}
for b in range(args.M0 // args.B):
    brng = default_rng(1000 + b)
    x0 = st.make_noise(brng, args.B); f0 = st.features(x0)
    for k in keys:
        xi, ls = k; a2 = 10 ** ls / xi; lam = xi * n / st.TAU
        kk = brng.poisson(lam, args.B)
        f1 = st.features(st.inject(x0.copy(), brng, kk, a2, ant))
        for name, cols in st.COLS.items():
            pools[k][name][0].append(f0[:, cols] @ W[k][name]); pools[k][name][1].append(f1[:, cols] @ W[k][name])
    print(f'batch {b+1} done', flush=True)
res = {'limits_boot': {}, 'limits_clt': {}, 'limits': {}, 'grid': {}}
srng = default_rng(7)
for xi in XI:
    grid = [round(float(v), 3) for v in GRID]
    res['grid'][str(xi)] = grid
    for d in ('limits_boot', 'limits_clt', 'limits'):
        res[d][str(xi)] = {}
    for name in st.COLS:
        m = name + '_lin'
        pdet = {N: [] for N in NB}; n50 = []
        for ls in grid:
            h0 = np.concatenate(pools[(xi, ls)][name][0]); h1 = np.concatenate(pools[(xi, ls)][name][1])
            for N in NB:
                pdet[N].append(st.stack_pdet_boot(h0, h1, N, srng))
            n50.append(st.n50_clt(h0, h1))
        lb = {str(N): st.crossing(grid, pdet[N], 0.5, True) for N in NB}
        logn = np.log10(np.where(np.isfinite(n50), n50, np.nan))
        lc = {str(N): st.crossing(grid, logn, np.log10(N), False) for N in N_ALL}
        res['limits_boot'][str(xi)][m] = lb; res['limits_clt'][str(xi)][m] = lc
        res['limits'][str(xi)][m] = {str(N): (lb[str(N)] if N in NB else lc[str(N)]) for N in N_ALL}
json.dump(res, open(args.out, 'w'), indent=1)
for xi in XI:
    print(f'xi={xi:g}')
    for N in N_ALL:
        L = res['limits'][str(xi)]
        print(f"  N={N:<7d} cc {L['cc_lin'][str(N)]:6.2f} trad {L['trad_lin'][str(N)]:6.2f} ing {L['ing_lin'][str(N)]:6.2f}  gain {L['trad_lin'][str(N)]-L['ing_lin'][str(N)]:6.2f}")
