#!/usr/bin/env python3
"""
analyze_option_b.py -- merge the option-(b) result files (real/results/option_b_*.json, one per launched process),
aggregate the combined-posterior gains over stretches, compare them with the synthetic three-rule prediction
(synthetic/results/stacking_table.csv) and summarise the coverage of the combined posterior.

Writes real/results/:
  option_b_summary.json           per-stretch and aggregate numbers (machine-readable)
  option_b_gain_table.csv / .md   Delta(N) for both rules and both xi, real noise (15 stretches) and synthetic (3 stretches)
  option_b_coverage.csv / .md     coverage of the combined posterior per N (P-P at 0.5/0.9, KS, bias, width)
  option_b_gain_vs_duration.png/.pdf  figure: Delta against stacked duration, real points on the synthetic curves
  option_b_summary.md             the write-up of the numbers, including the pre-stated criterion
Conventions (CLAUDE.md): limits are log10 Omega on the calibrated axis; Delta = Trad - ING in dex (positive = ING deeper);
per-stretch Delta = mean over available Trad seeds - mean over ING seeds (the Table II rule); aggregate = mean over stretches +- SE.
"""
import json, glob, csv, os, sys, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORDER = ['03A', '03A2', '03A3', '03A4', '03A5', '03B', '03B2', '03B3', '03B4', '03B5', '04A', '04A2', '04A3', '04A4', '04A5']
XIS = ['0.001', '0.01']
RULES = ['combined', 'linear']
SEG_S = 4.0

def dur(N):
    s = N * SEG_S
    if s < 60: return f'{s:.0f} s'
    if s < 3600: return f'{s / 60:.0f} min' if s >= 120 else f'{s / 60:.1f} min'
    if s < 86400: return f'{s / 3600:.1f} h'
    return f'{s / 86400:.1f} d'

def load(paths):
    stretches = {}
    meta = None
    for p in paths:
        r = json.load(open(p))
        meta = meta or {k: v for k, v in r.items() if k != 'stretches'}
        for s, st in r['stretches'].items():
            stretches[s] = st
    return meta, stretches

def per_stretch(st):
    """{xi: {N: {rule: {'ing': [...], 'trad': [...], 'delta_mean', 'delta_pairs_median', 'n_ing', 'n_trad'}}}}"""
    out = {}
    seeds = st['seeds']
    for xi in XIS:
        out[xi] = {}
        Ns = set()
        for sd, e in seeds.items():
            for fs in ('ing', 'trad'):
                if fs in e and e[fs].get('complete'):
                    Ns |= set(e[fs]['limits'].get(xi, {}).keys())
        for N in sorted(Ns, key=int):
            out[xi][N] = {}
            for rule in RULES:
                ing = {sd: e['ing']['limits'][xi][N][f'limit_{rule}'] for sd, e in seeds.items() if 'ing' in e and e['ing'].get('complete') and N in e['ing']['limits'].get(xi, {})}
                tr = {sd: e['trad']['limits'][xi][N][f'limit_{rule}'] for sd, e in seeds.items() if 'trad' in e and e['trad'].get('complete') and N in e['trad']['limits'].get(xi, {})}
                pairs = [tr[s] - ing[s] for s in ing if s in tr]
                out[xi][N][rule] = {'ing': ing, 'trad': tr, 'n_ing': len(ing), 'n_trad': len(tr),
                                    'ing_mean': float(np.mean(list(ing.values()))) if ing else None,
                                    'trad_mean': float(np.mean(list(tr.values()))) if tr else None,
                                    'delta_mean': float(np.mean(list(tr.values())) - np.mean(list(ing.values()))) if ing and tr else None,
                                    'delta_pairs_median': float(np.median(pairs)) if pairs else None,
                                    'synthetic': bool(next(iter(seeds.values()))['ing']['limits'][xi][N].get('synthetic', False)) if 'ing' in next(iter(seeds.values())) else int(N) >= 1000}
    return out

def aggregate(per):
    """per: {stretch: per_stretch}; returns {xi: {N: {rule: {...}}}} with mean +- SE over stretches."""
    agg = {}
    for xi in XIS:
        agg[xi] = {}
        Ns = sorted({N for s in per.values() for N in s[xi]}, key=int)
        for N in Ns:
            agg[xi][N] = {}
            for rule in RULES:
                d = {s: per[s][xi][N][rule]['delta_mean'] for s in per if N in per[s][xi] and per[s][xi][N][rule]['delta_mean'] is not None}
                ing = {s: per[s][xi][N][rule]['ing_mean'] for s in per if N in per[s][xi] and per[s][xi][N][rule]['ing_mean'] is not None}
                tr = {s: per[s][xi][N][rule]['trad_mean'] for s in per if N in per[s][xi] and per[s][xi][N][rule]['trad_mean'] is not None}
                v = np.array(list(d.values()))
                agg[xi][N][rule] = {'n_stretches': int(v.size), 'delta_mean': float(v.mean()) if v.size else None,
                                    'delta_se': float(v.std(ddof=1) / np.sqrt(v.size)) if v.size > 1 else None,
                                    'delta_median': float(np.median(v)) if v.size else None,
                                    'delta_min': float(v.min()) if v.size else None, 'delta_max': float(v.max()) if v.size else None,
                                    'n_positive': int((v > 0).sum()), 'per_stretch': d,
                                    'ing_mean': float(np.mean(list(ing.values()))) if ing else None, 'trad_mean': float(np.mean(list(tr.values()))) if tr else None,
                                    'synthetic': any(per[s][xi][N][rule]['synthetic'] for s in per if N in per[s][xi])}
    return agg

def synthetic_prediction():
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'synthetic', 'results', 'stacking_table.csv'))))
    pred = {}
    for r in rows:
        pred.setdefault(r['xi'], {})[int(r['N'])] = {'linear': float(r['d_lin']), 'combined': float(r['d_nl']), 'df_vs_trad': float(r['d_df_trad']),
                                                      'ing_lin': float(r['ing_lin']), 'trad_lin': float(r['trad_lin']), 'ing_nl': float(r['ing_nl']), 'trad_nl': float(r['trad_nl'])}
    return pred

def interp_pred(pred_xi, N, rule):
    Ns = np.array(sorted(pred_xi)); vals = np.array([pred_xi[n][rule] for n in Ns])
    return float(np.interp(np.log10(N), np.log10(Ns), vals))

def coverage_summary(stretches):
    """{net: {N: {...}}} over all (stretch, seed) entries; plus synthetic N=1 coverage."""
    out = {}
    for fs in ('ing', 'trad'):
        out[fs] = {}
        recs = {}
        for s, st in stretches.items():
            for sd, e in st['seeds'].items():
                if fs in e and e[fs].get('complete'):
                    for N, c in e[fs]['coverage'].items():
                        recs.setdefault(N, []).append((s, sd, c))
                    if 'coverage_synthetic' in e[fs]:
                        recs.setdefault('1_synthetic', []).append((s, sd, e[fs]['coverage_synthetic']))
        for N, L in recs.items():
            ks = np.array([c['ks_omega'] for _, _, c in L]); crit = L[0][2].get('ks_95pct_critical', 1.36 / np.sqrt(L[0][2]['ntrial']))
            p50 = np.array([c['empirical'][4] for _, _, c in L]); p90 = np.array([c['empirical'][8] for _, _, c in L])
            bias = np.array([c.get('bias_median', np.nan) for _, _, c in L]); absb = np.array([c.get('abs_bias_median', np.nan) for _, _, c in L])
            width = np.array([c.get('width_median', np.nan) for _, _, c in L])
            out[fs][N] = {'n_runs': len(L), 'ks_median': float(np.median(ks)), 'ks_max': float(ks.max()), 'ks_95pct_critical': float(crit),
                          'n_ks_above_critical': int((ks > crit).sum()),
                          'pp50_median': float(np.median(p50)), 'pp50_min': float(p50.min()), 'pp50_max': float(p50.max()),
                          'pp90_median': float(np.median(p90)), 'pp90_min': float(p90.min()), 'pp90_max': float(p90.max()),
                          'bias_median': float(np.nanmedian(bias)), 'abs_bias_median': float(np.nanmedian(absb)), 'width_median': float(np.nanmedian(width)),
                          'ntrial': int(L[0][2]['ntrial'])}
    return out

def rule_comparison(stretches):
    """Per (xi, N, network): mean over runs of (limit_combined - limit_linear) and the noise-only gap
    (0.3 % threshold - median) of each statistic, in dex.  A product rule that works is at least as deep as
    the linear stack of the same posteriors; a gap that stops shrinking with N means the product statistic
    has saturated (the noise-only product posterior no longer moves with the data)."""
    acc = {}
    for st in stretches.values():
        for sd, e in st['seeds'].items():
            for fs in ('ing', 'trad'):
                if fs not in e or not e[fs].get('complete'):
                    continue
                for xi in XIS:
                    for N, r in e[fs]['limits'].get(xi, {}).items():
                        a = acc.setdefault((xi, int(N), fs), {'cl': [], 'gc': [], 'gl': [], 'syn': bool(r.get('synthetic', False))})
                        a['cl'].append(r['limit_combined'] - r['limit_linear'])
                        a['gc'].append(r['thr_combined'] - r['noise_stat_combined_median'])
                        a['gl'].append(r['thr_linear'] - r['noise_stat_linear_median'])
    out = {}
    for (xi, N, fs), a in sorted(acc.items()):
        n = len(a['cl'])
        out.setdefault(xi, {}).setdefault(str(N), {})[fs] = {
            'n_runs': n, 'synthetic': a['syn'],
            'comb_minus_lin_mean': float(np.mean(a['cl'])),
            'comb_minus_lin_se': float(np.std(a['cl'], ddof=1) / np.sqrt(n)) if n > 1 else None,
            'gap_combined': float(np.mean(a['gc'])), 'gap_linear': float(np.mean(a['gl']))}
    return out

def md_table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)

def f2(x, sign=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)): return '--'
    return f'{x:+.2f}' if sign else f'{x:.2f}'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inputs', default=os.path.join(HERE, 'results', 'option_b_*.json'))
    ap.add_argument('--out', default=os.path.join(HERE, 'results'))
    args = ap.parse_args()
    paths = sorted(p for p in glob.glob(args.inputs) if 'summary' not in os.path.basename(p))
    if not paths:
        sys.exit(f'no inputs match {args.inputs}')
    os.makedirs(args.out, exist_ok=True)
    meta, stretches = load(paths)
    per = {s: per_stretch(stretches[s]) for s in ORDER if s in stretches}
    agg = aggregate(per)
    pred = synthetic_prediction()
    cov = coverage_summary(stretches)
    rc = rule_comparison(stretches)
    def saturated(xi, N):
        """product statistic not usable at this N: for both networks the noise-only 0.3 % threshold sits within
        0.05 dex of the noise-only median (the statistic no longer moves with the data), or the product-rule limit
        is more than 0.2 dex shallower than the linear stack of the same posteriors"""
        r = rc.get(xi, {}).get(str(N), {})
        return bool(r) and (all(v['gap_combined'] < 0.05 for v in r.values()) or all(v['comb_minus_lin_mean'] > 0.2 for v in r.values()))

    # ---- product rule against linear rule
    rc_rows = []
    for xi in XIS:
        for N in sorted(rc.get(xi, {}), key=int):
            for fs in ('ing', 'trad'):
                if fs not in rc[xi][N]: continue
                v = rc[xi][N][fs]
                rc_rows.append([xi, int(N), dur(int(N)), 'synthetic' if v['synthetic'] else 'real', fs, v['n_runs'],
                                f2(v['comb_minus_lin_mean']), f2(v['comb_minus_lin_se'], False) if v['comb_minus_lin_se'] is not None else '',
                                f2(v['gap_combined'], False), f2(v['gap_linear'], False), 'yes' if saturated(xi, N) else ''])
    with open(os.path.join(args.out, 'option_b_rules.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['xi', 'N', 'duration', 'noise', 'network', 'n_runs', 'limit_combined_minus_linear_mean', 'se', 'noise_gap_combined', 'noise_gap_linear', 'product_saturated'])
        w.writerows(rc_rows)
    rules_md = md_table(['ξ', 'N', 'T', 'noise', 'net', 'runs', 'limit(product) − limit(linear)', 'SE', 'noise gap, product', 'noise gap, linear', 'saturated'], rc_rows)

    # ---- gain table
    rows_csv, rows_md = [], []
    for xi in XIS:
        for N in sorted(agg[xi], key=int):
            a = agg[xi][N]; Ni = int(N)
            p_lin = interp_pred(pred[xi], Ni, 'linear') if xi in pred else np.nan
            p_nl = interp_pred(pred[xi], Ni, 'combined') if xi in pred else np.nan
            c, l = a['combined'], a['linear']
            rows_csv.append([xi, Ni, dur(Ni), 'synthetic' if c['synthetic'] else 'real', c['n_stretches'],
                             f2(c['delta_mean']), f2(c['delta_se'], False), f2(c['delta_median']), c['n_positive'],
                             f2(l['delta_mean']), f2(l['delta_se'], False), f2(l['delta_median']), l['n_positive'],
                             f2(p_nl), f2(p_lin), f2(c['ing_mean'], False), f2(c['trad_mean'], False), f2(l['ing_mean'], False), f2(l['trad_mean'], False)])
            rows_md.append([xi, Ni, dur(Ni), 'syn' if c['synthetic'] else 'real', c['n_stretches'],
                            f"{f2(c['delta_mean'])} ± {f2(c['delta_se'], False)}", f"{c['n_positive']}/{c['n_stretches']}", f2(p_nl),
                            f"{f2(l['delta_mean'])} ± {f2(l['delta_se'], False)}", f"{l['n_positive']}/{l['n_stretches']}", f2(p_lin),
                            f"{f2(c['ing_mean'], False)} / {f2(c['trad_mean'], False)}"])
    with open(os.path.join(args.out, 'option_b_gain_table.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['xi', 'N', 'duration', 'noise', 'n_stretches', 'delta_combined_mean', 'delta_combined_se', 'delta_combined_median', 'n_pos_combined',
                    'delta_linear_mean', 'delta_linear_se', 'delta_linear_median', 'n_pos_linear', 'synthetic_pred_product', 'synthetic_pred_linear',
                    'ing_limit_combined', 'trad_limit_combined', 'ing_limit_linear', 'trad_limit_linear'])
        w.writerows(rows_csv)
    gain_md = md_table(['ξ', 'N', 'T', 'noise', 'n', 'Δ_comb (mean ± SE)', 'Δ_comb > 0', 'synth. product', 'Δ_lin (mean ± SE)', 'Δ_lin > 0', 'synth. linear', 'ING / Trad limit (comb.)'], rows_md)

    # ---- coverage table
    cov_rows = []
    for fs in ('ing', 'trad'):
        for N in sorted(cov[fs], key=lambda k: (k.endswith('synthetic'), int(k.split('_')[0]))):
            c = cov[fs][N]
            cov_rows.append([fs, N.replace('_synthetic', ' (synthetic noise)'), c['n_runs'], f"{c['pp50_median']:.2f} [{c['pp50_min']:.2f}, {c['pp50_max']:.2f}]",
                             f"{c['pp90_median']:.2f} [{c['pp90_min']:.2f}, {c['pp90_max']:.2f}]", f"{c['ks_median']:.3f} (max {c['ks_max']:.3f})",
                             f"{c['n_ks_above_critical']}/{c['n_runs']}", f"{c['bias_median']:+.3f}", f"{c['abs_bias_median']:.3f}", f"{c['width_median']:.3f}"])
    with open(os.path.join(args.out, 'option_b_coverage.csv'), 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['network', 'N', 'n_runs', 'pp50_median_range', 'pp90_median_range', 'ks_median_max', 'n_ks_above_95pct_critical', 'bias_median', 'abs_bias_median', 'width_median']); w.writerows(cov_rows)
    cov_md = md_table(['network', 'N', 'runs', 'coverage of 50 % CI', 'coverage of 90 % CI', 'KS (median, max)', 'KS > crit.', 'bias', '|bias|', 'width'], cov_rows)

    # ---- criterion and headline numbers
    headline = {}
    for xi in XIS:
        real_N = [N for N in agg[xi] if not agg[xi][N]['combined']['synthetic']]
        syn_N = [N for N in agg[xi] if agg[xi][N]['combined']['synthetic']]
        longest_real = max(real_N, key=int) if real_N else None
        longest_syn = max(syn_N, key=int) if syn_N else None
        h = {'longest_real_N': longest_real, 'longest_synthetic_N': longest_syn}
        for tag, N in (('real', longest_real), ('synthetic', longest_syn)):
            if N is None: continue
            for rule in RULES:
                a = agg[xi][N][rule]
                h[f'{tag}_{rule}'] = {'N': int(N), 'duration': dur(int(N)), 'delta_mean': a['delta_mean'], 'delta_se': a['delta_se'], 'n_stretches': a['n_stretches'],
                                     'criterion_0.1dex_met': (a['delta_mean'] is not None and a['delta_mean'] >= 0.1)}
        # first N at which the mean gain drops below 0.1 dex (real noise), per rule
        for rule in RULES:
            below = [int(N) for N in sorted(agg[xi], key=int) if agg[xi][N][rule]['delta_mean'] is not None and agg[xi][N][rule]['delta_mean'] < 0.1]
            h[f'first_N_below_0.1dex_{rule}'] = min(below) if below else None
            h[f'first_T_below_0.1dex_{rule}'] = dur(min(below)) if below else None
        headline[xi] = h

    summary = {'inputs': paths, 'meta': meta, 'n_stretches': len(per), 'stretches': list(per), 'per_stretch': per, 'aggregate': agg,
               'synthetic_prediction': {xi: {str(N): v for N, v in pred[xi].items()} for xi in pred if xi in XIS}, 'coverage': cov, 'headline': headline,
               'rule_comparison': rc, 'product_saturated': {xi: [N for N in rc.get(xi, {}) if saturated(xi, N)] for xi in XIS}}
    json.dump(summary, open(os.path.join(args.out, 'option_b_summary.json'), 'w'), indent=1)

    # ---- figure
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
        fig, axes = plt.subplots(1, 3, figsize=(14, 5))
        for ax, xi in zip(axes[:2], XIS):
            Ns = np.array(sorted(pred[xi]))
            T = Ns * SEG_S
            ax.plot(T, [pred[xi][n]['linear'] for n in Ns], '-', color='C1', lw=1.5, label='synthetic: linear stack')
            ax.plot(T, [pred[xi][n]['combined'] for n in Ns], '-', color='C0', lw=1.5, label='synthetic: product of likelihoods')
            ax.plot(T, [pred[xi][n]['df_vs_trad'] for n in Ns], ':', color='C2', lw=1.2, label='synthetic: Drasco–Flanagan vs Trad')
            for rule, col, mk in (('combined', 'C0', 'o'), ('linear', 'C1', 's')):
                for syn, mfc in ((False, col), (True, 'white')):
                    Nn = [int(N) for N in agg[xi] if agg[xi][N][rule]['synthetic'] == syn and agg[xi][N][rule]['delta_mean'] is not None]
                    if not Nn: continue
                    m = np.array([agg[xi][str(n)][rule]['delta_mean'] for n in Nn]); se = np.array([agg[xi][str(n)][rule]['delta_se'] or 0 for n in Nn])
                    nst = agg[xi][str(Nn[0])][rule]['n_stretches']
                    sat = syn and rule == 'combined' and all(saturated(xi, n) for n in Nn)
                    lab = f'trained nets, {"product of posteriors" if rule == "combined" else "linear stack"}, ' + (
                        f'synthetic noise ({nst} stretches' + ('; statistic saturated)' if sat else ')') if syn else f'real noise ({nst} stretches)')
                    ax.errorbar(np.array(Nn) * SEG_S, m, yerr=se, fmt=mk, color='grey' if sat else col, mfc=mfc, ms=6, capsize=2, alpha=0.6 if sat else 1, label=lab)
            ax.axhline(0, color='k', lw=0.5); ax.axhline(0.1, color='grey', lw=0.5, ls='--')
            ax.set_xscale('log'); ax.set_xlabel('stacked duration [s]'); ax.set_title(f'ξ = {float(xi):g}'); ax.grid(alpha=0.3)
            for s, lab in ((60, '1 min'), (3600, '1 h'), (86400, '1 d')):
                ax.axvline(s, color='grey', lw=0.4, alpha=0.5)
                ax.text(s, 0.98, lab, fontsize=7, rotation=90, va='top', ha='right', color='grey', transform=ax.get_xaxis_transform())
        axes[0].set_ylabel('Δ = Trad − ING-Net [dex] (positive: ING-Net deeper)')
        hs, ls = axes[0].get_legend_handles_labels()
        fig.legend(hs, ls, loc='lower center', ncol=3, fontsize=7.5, frameon=False)
        ax = axes[2]
        for fs, col in (('ing', 'C0'), ('trad', 'C1')):
            Ns = [N for N in cov[fs] if not N.endswith('synthetic')]
            x = [int(N) for N in Ns]
            ax.plot(x, [cov[fs][N]['pp50_median'] for N in Ns], 'o-', color=col, label=f'{fs.upper() if fs == "ing" else "Trad"}: coverage of 50 % CI')
            ax.plot(x, [cov[fs][N]['pp90_median'] for N in Ns], 's--', color=col, label=f'{fs.upper() if fs == "ing" else "Trad"}: coverage of 90 % CI')
        ax.axhline(0.5, color='grey', lw=0.5); ax.axhline(0.9, color='grey', lw=0.5)
        ax.set_xscale('log'); ax.set_xlabel('N segments combined'); ax.set_ylabel('empirical coverage (median over runs)'); ax.set_ylim(0, 1)
        ax.set_title('product posterior: calibration (real noise)'); ax.legend(fontsize=7); ax.grid(alpha=0.3)
        fig.suptitle('Option (b): trained ING-Net and power-only posteriors combined over N segments of real evaluation noise', fontsize=10)
        fig.tight_layout(rect=(0.01, 0.14, 1, 1))
        fig.savefig(os.path.join(args.out, 'option_b_gain_vs_duration.png'), dpi=150); fig.savefig(os.path.join(args.out, 'option_b_gain_vs_duration.pdf'))
        figtxt = 'figure written'
    except ImportError:
        figtxt = 'matplotlib missing: no figure'

    # ---- markdown summary
    lines = ['# Option (b) on the trained networks — results', '',
             f'Inputs: {", ".join(os.path.basename(p) for p in paths)}; {len(per)} stretches: {", ".join(per)}.',
             f'Expectation stated in advance: {meta.get("expectation_stated_in_advance")}. Criterion: {meta.get("criterion")}.',
             f'Networks: {meta.get("networks")}; feature order {meta.get("feature_order")}; R = {meta.get("R")} stacks per threshold and per detection estimate.', '',
             '## Gain against stacked duration', '',
             'Per-stretch Δ = mean over available Trad seeds − mean over ING-Net seeds (Table II rule; diverged Trad seeds skipped: 03A 1401/1402, 03B 1402, 04A2 1401); '
             'aggregate = mean ± standard error over stretches; "> 0" counts stretches with positive Δ. "synth." columns are the synthetic three-rule prediction of '
             '`synthetic/results/stacking_table.csv` interpolated in log N (product of per-segment likelihoods ↔ combined; linear stack ↔ linear). '
             'Rows marked "syn" use the real networks on synthetic whitened Gaussian noise (3 reference stretches).', '', gain_md, '',
             '## Headline', '']
    for xi in XIS:
        h = headline[xi]
        for tag in ('real', 'synthetic'):
            for rule in RULES:
                k = f'{tag}_{rule}'
                if k in h:
                    v = h[k]
                    note = ' [product statistic saturated at this N, see "Product rule against linear rule": not a usable limit]' if rule == 'combined' and saturated(xi, str(v['N'])) else ''
                    lines.append(f'- ξ = {float(xi):g}, {tag} noise, {rule} rule, longest stack N = {v["N"]} ({v["duration"]}): Δ = {f2(v["delta_mean"])} ± {f2(v["delta_se"], False)} dex over {v["n_stretches"]} stretches → criterion Δ ≥ 0.1 dex {"met" if v["criterion_0.1dex_met"] else "not met"}.{note}')
        for rule in RULES:
            lines.append(f'- ξ = {float(xi):g}, {rule} rule: mean Δ first falls below 0.1 dex at N = {h[f"first_N_below_0.1dex_{rule}"]} ({h[f"first_T_below_0.1dex_{rule}"]}).')
    lines += ['', '## Coverage of the combined posterior', '',
              'Injections drawn from the prior into N real-noise segments; the combined posterior is the normalised product of the N per-segment posteriors on a 0.02 dex grid. '
              '"coverage of 50 % CI" = fraction of injections inside the central 50 % interval of the log10 Ω marginal (nominal 0.50), likewise 90 %; KS = Kolmogorov distance of the '
              'PIT values from uniform (critical value 1.36/√200 = 0.096 at 95 %); bias = median (posterior mean − truth), |bias| = median absolute, width = median posterior std, all in dex '
              'and for injections above log10 Ω = −7.5.', '', cov_md, '',
              '## Product rule against linear rule', '',
              'Same posteriors, same noise stacks and injections, two detection statistics: the posterior mean of log10 Ω under the normalised product of the N '
              'per-segment posteriors ("product", the option-(b) construction, 0.1 dex grid) and the mean of the N per-segment posterior means ("linear"). '
              'Columns: mean over runs (stretch × seed) of limit(product) − limit(linear) in dex (positive: the product rule is shallower), and the noise-only gap '
              '0.3 % threshold − median of each statistic. "saturated" marks N at which, for both networks, the noise-only product statistic has a gap below 0.05 dex '
              'or the product-rule limit is more than 0.2 dex shallower than the linear stack of the same posteriors: the product posterior of that many segments is '
              'dominated by the shared systematic shape of the learned posteriors raised to the power N rather than by the data, so its limits are not usable. '
              'The grid resolution is not the cause: on 03A seed 1400 the limits on a 0.02 dex grid equal those on the 0.1 dex grid to 0.00 dex at N = 30, 100, 246 '
              '(one case 0.05 dex; `real/results/gridcheck_03A_seed1400.json`).', '', rules_md, '',
              f'_{figtxt}: option_b_gain_vs_duration.png_']
    open(os.path.join(args.out, 'option_b_summary.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))

if __name__ == '__main__':
    main()
