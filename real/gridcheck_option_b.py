"""Grid-resolution check (run on the server: python real/gridcheck_option_b.py; needs the adapters of option_b_real.py) for the product rule of option (b): rerun run_one on 03A seed 1400 (ING and Trad)
with the default 0.1 dex log10 Omega grid and with a 0.02 dex grid, same rng seed (same noise stacks and
injections), N = 30, 100, 246, xi = 1e-3 and 1e-2.  Writes /root/ingnet-revision/scratch/gridcheck.json."""
import sys, os, time, json, numpy as np
sys.path.insert(0, '/root/ingnet-revision/real')
import option_b_real as ob
from numpy.random import default_rng

t0 = time.time()
def log(s): print(f'[{time.time()-t0:7.1f}s] {s}', flush=True)

run, si = 'O3a', 0
noise = ob.load_eval_noise(run, si)
segs = ob.segments_from_noise(noise, 246, default_rng(1))
assert np.allclose(ob.GRID_POINTS, np.array([(o, x) for o in ob.LOGOMEGA_GRID for x in ob.LOGXI_GRID]))

def set_grid(nO):
    ob.LOGOMEGA_GRID = np.linspace(-8, -1, nO)
    ob.GRID_POINTS = np.array([(o, x) for o in ob.LOGOMEGA_GRID for x in ob.LOGXI_GRID])
    ob.LOGO = np.tile(ob.LOGOMEGA_GRID[:, None], (1, ob.LOGXI_GRID.size))
    log(f'grid: {nO} points, step {ob.LOGOMEGA_GRID[1]-ob.LOGOMEGA_GRID[0]:.3f} dex')

out = {}
OUT = '/root/ingnet-revision/scratch/gridcheck.json'
for net, seed in (('ing', 1400), ('trad', 1400)):
    post = ob.load_posterior(run, seed, net, si)
    # weight concentration of the noise-only product posterior at N = 246 on the coarse grid
    for nO in (71, 351):
        set_grid(nO)
        f0 = ob.features(segs); lp0 = ob.log_prob_grid(post, f0)
        rng = default_rng(3)
        idx = ob.stacks(246, 246, 500, rng, True)
        L = lp0.reshape(246, -1); C = ob.multiplicity(idx, 246); S = C @ L; S -= S.max(1, keepdims=True)
        w = np.exp(S); w /= w.sum(1, keepdims=True)
        wO = w.reshape(500, nO, -1).sum(2)
        out[f'{net}_{nO}_maxcell'] = {'median_max_cell_weight_N246': float(np.median(wO.max(1))),
                                     'median_posterior_std_dex_N246': float(np.median(np.sqrt((wO * ob.LOGOMEGA_GRID**2).sum(1) - (wO * ob.LOGOMEGA_GRID).sum(1)**2)))}
        log(f'{net} nO={nO}: N=246 noise-only product posterior: median max-cell weight {out[f"{net}_{nO}_maxcell"]["median_max_cell_weight_N246"]:.2f}, median std {out[f"{net}_{nO}_maxcell"]["median_posterior_std_dex_N246"]:.3f} dex')
        for xi in (1e-3, 1e-2):
            rng = default_rng(7)
            log(f'{net} nO={nO} xi={xi:g}')
            r = ob.run_one(segs, post, xi, [30, 100, 246], rng, log, R=2000)
            out[f'{net}_{nO}_{xi:g}'] = {N: {'limit_combined': v['limit_combined'], 'limit_linear': v['limit_linear'],
                                           'thr_combined': v['thr_combined'], 'med_combined': v['noise_stat_combined_median'],
                                           'bisection_combined': v['bisection']['combined']} for N, v in r.items()}
            json.dump(out, open(OUT, 'w'), indent=1)
log('done')
