#!/usr/bin/env python3
"""Merge the two result files, print the tables used in the write-up, and draw the figure."""
import json, numpy as np, sys, os
os.makedirs('results', exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

res = {}
for f in ['res_a.json', 'res_b.json']:
    r = json.load(open(f))
    for key in ['limits', 'limits_boot', 'limits_clt', 'moments', 'grid', 'n50_clt', 'pdet_boot']:
        res.setdefault(key, {}).update(r[key])
    for key in ['gamma0', 'c_F', 'c_w', 'N_all', 'N_boot', 'M0', 'MK', 'ncomp']:
        res[key] = r[key]
# analytic-direction LIN results replace the fitted-direction ones; extension grid fills in DF at xi=1e-4
for f in ['lin_a.json', 'lin_b.json']:
    r = json.load(open(f))
    for xi in r['limits']:
        for m in r['limits'][xi]:
            res['limits'][xi][m] = r['limits'][xi][m]
            res['limits_boot'][xi][m] = r['limits_boot'][xi][m]
            res['limits_clt'][xi][m] = r['limits_clt'][xi][m]
r = json.load(open('res_c.json'))
for xi in r['limits']:
    for m in r['limits'][xi]:
        for N, v in r['limits'][xi][m].items():
            if (res['limits'][xi][m].get(N) is None or not np.isfinite(res['limits'][xi][m][N])) and v is not None and np.isfinite(v):
                res['limits'][xi][m][N] = v
json.dump(res, open('results/stacking_results_merged.json', 'w'), indent=1)

METHODS = ['cc_lin', 'trad_lin', 'ing_lin', 'trad_nl', 'ing_nl', 'df']
N_ALL = res['N_all']; NB = res['N_boot']
TAU = 8

def tlabel(N):
    T = 4 * N
    if T < 60: return f'{T:.0f} s'
    if T < 3600: return f'{T/60:.0f} min'
    if T < 86400: return f'{T/3600:.1f} h'
    return f'{T/86400:.1f} d'

def val(xi, m, N):
    return res['limits'][str(xi)][m][str(N)]

rows_out = []
for xi in [1e-2, 1e-3, 1e-4, 1.0]:
    k = str(xi)
    if k not in res['limits']:
        continue
    print(f'\n=== xi = {xi:g} ===')
    print(f"{'N':>7} {'T':>8} | " + ' '.join(f'{m:>9}' for m in METHODS) + ' | ING-Trad(lin) ING-Trad(NL) DF-Trad(lin) DF-CC(lin)  rho_ev@CC rho_ev@DF')
    for N in N_ALL:
        v = {m: val(xi, m, N) for m in METHODS}
        d1 = v['trad_lin'] - v['ing_lin']; d2 = v['trad_nl'] - v['ing_nl']
        d3 = v['trad_lin'] - v['df']; d4 = v['cc_lin'] - v['df']
        rho_cc = np.sqrt(10 ** v['cc_lin'] / xi * TAU) if np.isfinite(v['cc_lin']) else np.nan
        rho_df = np.sqrt(10 ** v['df'] / xi * TAU) if np.isfinite(v['df']) else np.nan
        print(f'{N:>7d} {tlabel(N):>8} | ' + ' '.join(f'{v[m]:9.2f}' for m in METHODS) +
              f' | {d1:12.2f} {d2:12.2f} {d3:12.2f} {d4:10.2f}   {rho_cc:7.1f} {rho_df:7.1f}')
        rows_out.append(dict(xi=xi, N=N, T=tlabel(N), **{m: v[m] for m in METHODS},
                             d_lin=d1, d_nl=d2, d_df_trad=d3, d_df_cc=d4, rho_cc=rho_cc, rho_df=rho_df))

# bootstrap vs CLT check at N = 1000 and slope check
print('\n=== bootstrap vs CLT at N = 1000 (log10 sigma_50) ===')
for xi in [1e-2, 1e-3, 1e-4]:
    k = str(xi)
    if k not in res['limits_boot']: continue
    for m in METHODS:
        b = res['limits_boot'][k][m]['1000']; c = res['limits_clt'][k][m]['1000']
        print(f'xi={xi:g} {m:9s} boot {b:7.2f}  clt {c:7.2f}  diff {b-c:6.2f}')
print('\n=== cc_lin slope per decade of N (expect -0.50) ===')
for xi in [1e-2, 1e-3, 1e-4, 1.0]:
    k = str(xi)
    if k not in res['limits']: continue
    a = val(xi, 'cc_lin', 10); b = val(xi, 'cc_lin', 100000)
    print(f'xi={xi:g}: ({b:.2f} - {a:.2f})/4 = {(b-a)/4:.3f}')

json.dump(rows_out, open('results/stacking_table.json', 'w'), indent=1)
import csv
with open('results/stacking_table.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys())); w.writeheader(); w.writerows(rows_out)

# ---------------- figure
plt.rcParams.update({'font.size': 9, 'axes.titlesize': 10})
fig, axes = plt.subplots(2, 3, figsize=(11, 6.2), sharex=True)
T = np.array([4 * N for N in N_ALL]) / 3600.0
labels = {'cc_lin': 'CC, stacked (LVK)', 'trad_lin': 'Trad (C,P), stacked', 'ing_lin': 'ING (C,P,κ), stacked',
          'trad_nl': 'Trad, product of likelihoods', 'ing_nl': 'ING, product of likelihoods', 'df': 'Drasco–Flanagan, full data'}
styles = {'cc_lin': dict(color='0.55', ls=':', lw=1.8), 'trad_lin': dict(color='#d95f02', ls='--', lw=1.6),
          'ing_lin': dict(color='#1b9e77', ls='--', lw=1.6), 'trad_nl': dict(color='#d95f02', ls='-', lw=1.6),
          'ing_nl': dict(color='#1b9e77', ls='-', lw=2.0), 'df': dict(color='#7570b3', ls='-', lw=2.0)}
for j, xi in enumerate([1e-2, 1e-3, 1e-4]):
    ax = axes[0, j]
    for m in METHODS:
        y = np.array([val(xi, m, N) for N in N_ALL])
        ax.plot(T, y, marker='o', ms=3, label=labels[m], **styles[m])
    ax.set_xscale('log'); ax.set_title(f'ξ = {xi:g}')
    ax.grid(alpha=0.3)
    if j == 0: ax.set_ylabel('log10 σ_s² at 50 % detection (lower is better)')
    ax = axes[1, j]
    d_lin = np.array([val(xi, 'trad_lin', N) - val(xi, 'ing_lin', N) for N in N_ALL])
    d_nl = np.array([val(xi, 'trad_nl', N) - val(xi, 'ing_nl', N) for N in N_ALL])
    d_df = np.array([val(xi, 'trad_lin', N) - val(xi, 'df', N) for N in N_ALL])
    ax.plot(T, d_lin, marker='o', ms=3, color='#1b9e77', ls='--', lw=1.6, label='ING − Trad, stacked (memo Sec. 4)')
    ax.plot(T, d_nl, marker='o', ms=3, color='#1b9e77', ls='-', lw=2.0, label='ING − Trad, product of likelihoods (option b)')
    ax.plot(T, d_df, marker='o', ms=3, color='#7570b3', ls='-', lw=2.0, label='Drasco–Flanagan − Trad stacked (comment 10)')
    ax.axhline(0, color='k', lw=0.8); ax.axhline(0.1, color='k', lw=0.6, ls=':')
    ax.set_xscale('log'); ax.grid(alpha=0.3)
    ax.set_xlabel('stacked duration [h]  (4 s × N)')
    if j == 0: ax.set_ylabel('gain Δ over power-only baseline [dex]')
    ax.set_ylim(-0.25, 1.6)
axes[0, 0].legend(fontsize=7, loc='lower left'); axes[1, 0].legend(fontsize=7, loc='upper right')
for ax in axes[0]:
    for N, lab in [(1, '4 s'), (1000, '1.1 h'), (100000, '4.6 d')]:
        pass
fig.suptitle('Per-segment kurtosis gain under three ways of combining segments (synthetic, Gaussian noise, rev2 signal model)', fontsize=10)
fig.tight_layout()
fig.savefig('results/stacking_gain_vs_duration.png', dpi=170)
fig.savefig('results/stacking_gain_vs_duration.pdf')
print('figure written')
