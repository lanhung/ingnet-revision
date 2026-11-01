#!/usr/bin/env python3
"""
make_tables.py -- regenerate the manuscript tables on the calibrated amplitude axis (task 4/5 of CLAUDE.md)
from the rev2 result files copied into docs/source_tables/ (read-only copies of /root/SGWB1 outputs).

Writes docs/tables/:
  table2_15stretch.csv / .md     Table II: per-stretch and 15-stretch limits, ING-Net vs Trad, 5 duty cycles
  table3_null_ul.csv / .md       Table III: 95 % null upper limits on 200 non-overlapping eval segments (calibrated axis)
  table4_tradfr.csv / .md        Table IV: Trad-FR against Trad and ING-Net on the three reference stretches
  table5_veto.csv / .md          Table V: identical vs antenna injection with the coincidence veto (median over seeds)
  table6_gps.md                  Table VI: GPS start times of the 15 stretches
  seed_scatter.json              [X], [Y] of Sec. III B
  fig7_sensitivity_curves.png/pdf  limits vs xi for the three reference stretches (3 seeds, shaded +-1 sigma)
  tables_summary.md              everything in one Markdown file with the aggregation rules spelled out
Conventions: limits are log10 Omega on the paper's calibrated axis (Eq. 11 sigma1 per stretch); Delta = Trad - ING in dex,
positive = ING deeper; diverged Trad seeds (limit pinned at the prior top -1.0) are excluded and the n is given.
"""
import csv, json, glob, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, 'docs', 'source_tables', 'outputs_rev1')
OUT = os.path.join(ROOT, 'docs', 'tables')
os.makedirs(OUT, exist_ok=True)
XIS = ['0.001', '0.01', '0.1', '0.5', '1.0']
ORDER = ['03A', '03A2', '03A3', '03A4', '03A5', '03B', '03B2', '03B3', '03B4', '03B5', '04A', '04A2', '04A3', '04A4', '04A5']
RUN_OF = {s: {'03': 'O3a' if s.startswith('03A') else 'O3b', '04': 'O4a'}[s[:2]] for s in ORDER}
DIVERGED_TRAD_GLITCHAUG = {('03A', 1401), ('03A', 1402), ('03B', 1402), ('04A2', 1401)}

def fl(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan

def fmt(x, nd=2, sign=False):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return '--'
    return (f'{x:+.{nd}f}' if sign else f'{x:.{nd}f}')

def md_table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '|'.join(['---'] * len(header)) + '|']
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)

def write_csv(path, header, rows):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

# ------------------------------------------------------------------ Table II
def table2():
    rows = []
    for f in ('summary_rev1_glitchaug.csv', 'summary_rev1x_glitchaug.csv'):
        rows += [r for r in csv.DictReader(open(os.path.join(SRC, f))) if r['exclude_diverged'] == 'True']
    per = {}
    for r in rows:
        per[(r['ds'], r['xi'])] = r
    csv_rows, md_rows, agg = [], [], {}
    for xi in XIS:
        D = []
        for ds in ORDER:
            r = per[(ds, xi)]
            ai, ais, ain = fl(r['ai_mean']), fl(r['ai_std']), int(r['ai_n'])
            tr, trs, trn = fl(r['tr_mean']), fl(r['tr_std']), int(r['tr_n'])
            d = tr - ai
            D.append(d)
            csv_rows.append([RUN_OF[ds], ds, xi, f'{ai:.3f}', f'{ais:.3f}', ain, f'{tr:.3f}', (f'{trs:.3f}' if np.isfinite(trs) else ''), trn, f'{d:+.3f}'])
            md_rows.append([RUN_OF[ds], ds, xi, f'{ai:.2f} ± {ais:.2f}', f'{tr:.2f}' + (f' ± {trs:.2f}' if np.isfinite(trs) else '') + (f' (n={trn})' if trn < 3 else ''), f'{d:+.2f}'])
        D = np.array(D)
        agg[xi] = {'mean': float(D.mean()), 'se': float(D.std(ddof=1) / np.sqrt(len(D))), 'std': float(D.std(ddof=1)),
                   'median': float(np.median(D)), 'min': float(D.min()), 'max': float(D.max()), 'n_stretches': int(len(D)),
                   'n_positive': int((D > 0).sum()),
                   'ing_mean': float(np.mean([fl(per[(ds, xi)]['ai_mean']) for ds in ORDER])),
                   'ing_range': [float(min(fl(per[(ds, xi)]['ai_mean']) for ds in ORDER)), float(max(fl(per[(ds, xi)]['ai_mean']) for ds in ORDER))],
                   'trad_mean': float(np.mean([fl(per[(ds, xi)]['tr_mean']) for ds in ORDER]))}
    write_csv(os.path.join(OUT, 'table2_15stretch.csv'),
              ['run', 'stretch', 'xi', 'ing_mean', 'ing_std', 'ing_n', 'trad_mean', 'trad_std', 'trad_n', 'delta_trad_minus_ing'], csv_rows)
    md = ['### Table II (regenerated): per-segment limits log10 Ω_limit on the calibrated axis, 15 stretches, glitch-augmented networks',
          '',
          'Mean ± std over training seeds 1400–1402 (n = 3 unless stated; Trad seeds whose limit sat at the prior top are excluded: '
          '03A 1401/1402, 03B 1402, 04A2 1401). Δ = Trad − ING-Net in dex, positive = ING-Net deeper. 50 % detection at the 99.7 % '
          'CFAR threshold, 4 s segments.', '',
          md_table(['Run', 'Stretch', 'ξ', 'ING-Net', 'Trad', 'Δ'], md_rows), '',
          '**Aggregate over the 15 stretches** (mean of the per-stretch Δ ± standard error; this is the rule behind the memo\'s '
          '+0.50 ± 0.03 and +0.23 ± 0.02):', '',
          md_table(['ξ', 'Δ mean ± SE', 'Δ median', 'Δ range', 'stretches with Δ > 0', 'ING mean (range)', 'Trad mean'],
                   [[xi, f'{a["mean"]:+.3f} ± {a["se"]:.3f}', f'{a["median"]:+.3f}', f'{a["min"]:+.2f} … {a["max"]:+.2f}', f'{a["n_positive"]}/15',
                     f'{a["ing_mean"]:.2f} ({a["ing_range"][0]:.2f} … {a["ing_range"][1]:.2f})', f'{a["trad_mean"]:.2f}'] for xi, a in agg.items()])]
    open(os.path.join(OUT, 'table2_15stretch.md'), 'w').write('\n'.join(md) + '\n')
    json.dump(agg, open(os.path.join(OUT, 'table2_aggregate.json'), 'w'), indent=1)
    return '\n'.join(md), agg, per

# ------------------------------------------------------------------ Table III
def table3():
    recs = {}
    for tag in ('rev1_glitchaug', 'rev1x_glitchaug'):
        for f in sorted(glob.glob(os.path.join(SRC, tag, '*', 'eval', 'eval_summary.json'))):
            run = os.path.basename(os.path.dirname(os.path.dirname(f)))
            ds, seed = run.split('_seed')[0], int(run.split('_seed')[1].split('_')[0])
            n = json.load(open(f))['null']
            recs.setdefault(ds, []).append((seed, n))
    csv_rows, md_rows, allD = [], [], []
    for ds in ORDER:
        L = recs[ds]
        ai_m = np.mean([n['ai_mean'] for _, n in L]); ai_s = np.mean([n['ai_std'] for _, n in L])
        good = [(s, n) for s, n in L if (ds, s) not in DIVERGED_TRAD_GLITCHAUG]
        tr_m = np.mean([n['tr_mean'] for _, n in good]); tr_s = np.mean([n['tr_std'] for _, n in good])
        dp = np.mean([n['dpaired_tr_minus_ai'] for _, n in good]); allD.append(dp)
        nseg = L[0][1]['n_segments']
        csv_rows.append([RUN_OF[ds], ds, nseg, f'{ai_m:.3f}', f'{ai_s:.3f}', f'{tr_m:.3f}', f'{tr_s:.3f}', len(good), f'{dp:+.3f}'])
        md_rows.append([RUN_OF[ds], ds, f'{ai_m:.2f}', f'{ai_s:.2f}', f'{tr_m:.2f}', f'{tr_s:.2f}', f'{dp:+.3f}' + (f' (n={len(good)})' if len(good) < 3 else '')])
    write_csv(os.path.join(OUT, 'table3_null_ul.csv'), ['run', 'stretch', 'n_segments', 'ing_mean', 'ing_std', 'trad_mean', 'trad_std', 'n_trad_seeds', 'delta_paired_trad_minus_ing'], csv_rows)
    allD = np.array(allD)
    md = ['### Table III (regenerated): 95 % upper limits on log10 Ω from noise-only segments, calibrated axis', '',
          f'{csv_rows[0][2]} non-overlapping 4 s segments of the evaluation part of each stretch; mean over seeds of the per-seed values '
          '(diverged Trad seeds excluded). Δ_paired = mean per-segment (Trad − ING-Net).', '',
          md_table(['Run', 'Stretch', 'ING-Net mean', 'ING-Net std', 'Trad mean', 'Trad std', 'Δ_paired'], md_rows), '',
          f'Over the 15 stretches: Δ_paired mean {allD.mean():+.3f} dex, range {allD.min():+.3f} … {allD.max():+.3f}; |Δ_paired| ≤ {np.abs(allD).max():.2f} dex; '
          f'ING-Net\'s null upper limit is deeper than Trad\'s on {(allD > 0).sum()} of 15 stretches and shallower on {(allD < 0).sum()} (all three in O4a). '
          'Per-stretch offsets of either sign up to about 0.25 dex, with no systematic excess of ING-Net over the power-only baseline, is the statement '
          'to make: the kurtosis channel does not add false signals on noise-only data. (The old text\'s |Δ_paired| ≤ 0.09 dex referred to three stretches on the old axis.)']
    open(os.path.join(OUT, 'table3_null_ul.md'), 'w').write('\n'.join(md) + '\n')
    return '\n'.join(md), allD

# ------------------------------------------------------------------ Table IV
def table4():
    rows = [r for r in csv.DictReader(open(os.path.join(SRC, 'summary_rev1_glitchaug.csv'))) if r['exclude_diverged'] == 'True']
    per = {(r['ds'], r['xi']): r for r in rows}
    csv_rows, md_rows = [], []
    for ds in ('03A', '03B', '04A'):
        for xi in XIS:
            r = per[(ds, xi)]
            ai, tr, fr = fl(r['ai_mean']), fl(r['tr_mean']), fl(r['fr_mean'])
            dfr = tr - fr
            csv_rows.append([RUN_OF[ds], ds, xi, f'{ai:.3f}', f'{fl(r["ai_std"]):.3f}', r['ai_n'], f'{tr:.3f}', r['tr_std'], r['tr_n'], f'{fr:.3f}', f'{fl(r["fr_std"]):.3f}', r['fr_n'], f'{dfr:+.3f}', f'{tr - ai:+.3f}', f'{fr - ai:+.3f}'])
            md_rows.append([RUN_OF[ds], xi, f'{ai:.2f} ± {fl(r["ai_std"]):.2f}', f'{tr:.2f}' + (f' ± {fl(r["tr_std"]):.2f}' if r['tr_std'] else '') + (f' (n={r["tr_n"]})' if int(r['tr_n']) < 3 else ''),
                            f'{fr:.2f} ± {fl(r["fr_std"]):.2f}', f'{dfr:+.2f}', f'{fr - ai:+.2f}'])
    write_csv(os.path.join(OUT, 'table4_tradfr.csv'), ['run', 'stretch', 'xi', 'ing_mean', 'ing_std', 'ing_n', 'trad_mean', 'trad_std', 'trad_n', 'tradfr_mean', 'tradfr_std', 'tradfr_n', 'delta_fr_trad_minus_tradfr', 'delta_trad_minus_ing', 'delta_tradfr_minus_ing'], csv_rows)
    dfr = np.array([fl(r[12]) for r in csv_rows])
    md = ['### Table IV (regenerated): frequency-resolved baseline on the three reference stretches (glitch-augmented runs, seeds 1400–1402)', '',
          'Δ_FR = Trad − Trad-FR (positive: the 64-D frequency-resolved input improves on the scalar power-only baseline); '
          'Δ_FR→ING = Trad-FR − ING-Net (positive: ING-Net deeper than Trad-FR). All 9 Trad-FR runs converged; the Trad column excludes the diverged seeds.', '',
          md_table(['Run', 'ξ', 'ING-Net', 'Trad', 'Trad-FR', 'Δ_FR', 'Trad-FR − ING-Net'], md_rows), '',
          f'Δ_FR over the 15 cells: mean {dfr.mean():+.3f} dex, range {dfr.min():+.2f} … {dfr.max():+.2f}. At ξ ≥ 0.1 the two second-order baselines agree '
          f'to within {np.abs(dfr[[i for i, r in enumerate(csv_rows) if r[2] in ("0.1", "0.5", "1.0")]]).max():.2f} dex; at ξ = 1e-3 Trad-FR is shallower than ING-Net by '
          f'{np.mean([fl(r[14]) for r in csv_rows if r[2] == "0.001"]):+.2f} dex on average.']
    open(os.path.join(OUT, 'table4_tradfr.md'), 'w').write('\n'.join(md) + '\n')
    return '\n'.join(md)

# ------------------------------------------------------------------ Table V
def table5():
    CFG = 'veto_K1.0_r0.1_PRIMARY'
    vals = {}
    for tag in ('rev1_identical', 'rev1_antenna'):
        for f in sorted(glob.glob(os.path.join(SRC, tag, '*', 'veto_diag', 'veto_diag.json'))):
            v = json.load(open(f)); ds, seed = v['dataset'], int(v['seed'])
            if ds not in ('03A', '03B', '04A'):
                continue
            for xi in ('0.001', '0.01'):
                c = v['configs'][CFG]['xi'][xi]
                vals.setdefault((tag, ds, xi), {})[seed] = (c['ai']['mean'], c['tr']['mean'])
    csv_rows, md_rows = [], []
    for xi in ('0.001', '0.01'):
        for ds in ('03A', '03B', '04A'):
            row_md = [xi, RUN_OF[ds]]; row_csv = [xi, RUN_OF[ds], ds]
            for tag in ('rev1_identical', 'rev1_antenna'):
                d = vals[(tag, ds, xi)]
                ai = np.array([d[s][0] for s in sorted(d)]); tr = np.array([d[s][1] for s in sorted(d)])
                ok = tr < -1.5                        # a diverged Trad seed has its limit pinned at the prior top (-1.0)
                ai_med, tr_med = np.median(ai), np.median(tr[ok]); D_med = np.median((tr - ai)[ok])
                row_md += [f'{ai_med:.2f}', f'{tr_med:.2f}' + ('' if ok.all() else f' (n={ok.sum()})'), f'{D_med:+.2f}']
                row_csv += [f'{ai_med:.3f}', f'{tr_med:.3f}', int(ok.sum()), f'{D_med:+.3f}']
            md_rows.append(row_md); csv_rows.append(row_csv)
    write_csv(os.path.join(OUT, 'table5_veto.csv'), ['xi', 'run', 'stretch', 'ident_ing_median', 'ident_trad_median', 'ident_trad_n', 'ident_delta_median',
                                                    'ant_ing_median', 'ant_trad_median', 'ant_trad_n', 'ant_delta_median'], csv_rows)
    md = ['### Table V (verified from veto_diag.json): identical vs antenna injection, coincidence veto (max κ > 1 and min κ < 0.1 max κ) on both pipelines', '',
          'Median over seeds 1400–1402 of the per-seed 20-round means; Δ = median of the per-seed (Trad − ING-Net). Tags rev1_identical / rev1_antenna '
          '(no glitch augmentation). One O3b Trad seed (1401) diverged under antenna injection and is excluded.', '',
          md_table(['ξ', 'Run', 'Ident. ING-Net', 'Ident. Trad', 'Ident. Δ', 'Ant. ING-Net', 'Ant. Trad', 'Ant. Δ'], md_rows)]
    open(os.path.join(OUT, 'table5_veto.md'), 'w').write('\n'.join(md) + '\n')
    return '\n'.join(md)

# ------------------------------------------------------------------ Table VI
def table6():
    gps = {}
    for f in sorted(glob.glob(os.path.join(SRC, 'rev1*_glitchaug', '*_seed1400_*', 'run_meta.json'))):
        m = json.load(open(f)); d = m['dataset_meta']
        names = list(eval(d['input_files']).keys()) if isinstance(d['input_files'], str) else list(d['input_files'].keys())
        gps[d['name']] = int(names[0].split('_')[-1].split('.')[0])
    rows = []
    for i, lab in enumerate(['Reference', '2', '3', '4', '5']):
        rows.append([lab] + [gps[f'{p}{"" if i == 0 else i + 1}'] for p in ('03A', '03B', '04A')])
    md = ['### Table VI: GPS start times of the 15 analysed stretches (4096 s each; from run_meta.json input_files)', '',
          md_table(['', 'O3a', 'O3b', 'O4a'], rows)]
    open(os.path.join(OUT, 'table6_gps.md'), 'w').write('\n'.join(md) + '\n')
    return '\n'.join(md), gps

# ------------------------------------------------------------------ capacity scan (Table IV footnote)
def table_capacity():
    f = os.path.join(SRC, 'summary_capacity_scan.csv')
    if not os.path.exists(f):
        return 'capacity-scan summary not available'
    rows = [r for r in csv.DictReader(open(f)) if r['exclude_diverged'] == 'True']
    tags = ['rev1_glitchaug', 'rev1_cap_h50_t10', 'rev1_cap_h128_t5', 'rev1_cap_h128_t10', 'rev1_cap_h256_t5', 'rev1_cap_h256_t10', 'rev1_cap_h256_t10_lr2e-4']
    label = {'rev1_glitchaug': '50 × 5 (primary)', 'rev1_cap_h50_t10': '50 × 10', 'rev1_cap_h128_t5': '128 × 5', 'rev1_cap_h128_t10': '128 × 10',
             'rev1_cap_h256_t5': '256 × 5', 'rev1_cap_h256_t10': '256 × 10', 'rev1_cap_h256_t10_lr2e-4': '256 × 10, lr 2e-4'}
    md_rows, csv_rows = [], []
    for tag in tags:
        row = [label[tag]]; crow = [tag, label[tag]]
        for xi in ('0.001', '0.01', '1.0'):
            R = [r for r in rows if r['tag'] == tag and r['xi'] == xi]
            ai = np.mean([fl(r['ai_mean']) for r in R]); tr = np.mean([fl(r['tr_mean']) for r in R]); fr = np.mean([fl(r['fr_mean']) for r in R])
            row += [f'{ai:.2f}', f'{tr:.2f}', f'{fr:.2f}', f'{tr - ai:+.2f}']; crow += [f'{ai:.3f}', f'{tr:.3f}', f'{fr:.3f}', f'{tr - ai:+.3f}']
        md_rows.append(row); csv_rows.append(crow)
    write_csv(os.path.join(OUT, 'table_capacity_scan.csv'), ['tag', 'hidden x transforms', 'ing_1e-3', 'trad_1e-3', 'tradfr_1e-3', 'delta_1e-3', 'ing_1e-2', 'trad_1e-2', 'tradfr_1e-2', 'delta_1e-2', 'ing_1', 'trad_1', 'tradfr_1', 'delta_1'], csv_rows)
    md = ['### Capacity scan (Table IV footnote): MAF hidden units × transforms, three reference stretches, seeds 1400–1401 (mean over the three stretches; the primary row has seeds 1400–1402)', '',
          'Glitch-augmented training throughout. The power-only baselines do not close the gap to ING-Net with 5× the hidden units or twice the transforms: '
          'Trad and Trad-FR move by ≤ 0.1 dex across the scan while Δ stays at +0.56 … +0.73 dex (ξ = 10⁻³) and +0.24 … +0.35 dex (ξ = 10⁻²).', '',
          md_table(['hidden × transforms', 'ING ξ=1e-3', 'Trad', 'Trad-FR', 'Δ', 'ING ξ=1e-2', 'Trad', 'Trad-FR', 'Δ', 'ING ξ=1', 'Trad', 'Trad-FR', 'Δ'], md_rows)]
    open(os.path.join(OUT, 'table_capacity_scan.md'), 'w').write('\n'.join(md) + '\n')
    return '\n'.join(md)

# ------------------------------------------------------------------ seed scatter and Fig. 7
def seed_scatter():
    rows = []
    for f in ('summary_rev1_glitchaug.csv', 'summary_rev1x_glitchaug.csv'):
        rows += [r for r in csv.DictReader(open(os.path.join(SRC, f))) if r['exclude_diverged'] == 'True']
    out = {}
    for net, lab in (('ai', 'ING-Net'), ('tr', 'Trad'), ('fr', 'Trad-FR')):
        ok = [r for r in rows if r.get(f'{net}_n') and int(r[f'{net}_n']) >= 2 and np.isfinite(fl(r.get(f'{net}_std')))]
        s = np.array([fl(r[f'{net}_std']) for r in ok])
        out[lab] = {'n_cells': int(s.size), 'median': float(np.median(s)), 'p90': float(np.percentile(s, 90)), 'max': float(s.max()),
                    'median_low_xi': float(np.median([fl(r[f'{net}_std']) for r in ok if r['xi'] in ('0.001', '0.01')]))}
    json.dump(out, open(os.path.join(OUT, 'seed_scatter.json'), 'w'), indent=1)
    return out

def fig7(per):
    try:
        import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    except ImportError:
        return 'matplotlib missing: Fig. 7 not drawn'
    xs = np.array([float(x) for x in XIS])
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4), sharey=True)
    for ax, ds in zip(axes, ('03A', '03B', '04A')):
        for net, lab, col in (('ai', 'ING-Net', 'C0'), ('tr', 'power-only (Trad)', 'C1'), ('fr', 'Trad-FR', 'C2')):
            m = np.array([fl(per[(ds, xi)][f'{net}_mean']) for xi in XIS]); s = np.array([fl(per[(ds, xi)][f'{net}_std']) for xi in XIS])
            s = np.where(np.isfinite(s), s, 0)
            ax.plot(xs, m, 'o-', color=col, label=lab, ms=4); ax.fill_between(xs, m - s, m + s, color=col, alpha=0.2)
        ax.set_xscale('log'); ax.set_title(f'{RUN_OF[ds]} reference stretch'); ax.set_xlabel('duty cycle ξ'); ax.grid(alpha=0.3)
    axes[0].set_ylabel('log10 Ω_limit (per 4 s segment)'); axes[0].legend(fontsize=8)
    fig.suptitle('Per-segment 50 %-detection limits at 0.3 % false alarm; mean ± 1σ over seeds 1400–1402 (glitch-augmented runs)', fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, 'fig7_sensitivity_curves.png'), dpi=150); fig.savefig(os.path.join(OUT, 'fig7_sensitivity_curves.pdf'))
    return 'Fig. 7 written'

def main():
    t2, agg, per = table2()
    t3, allD = table3()
    t4 = table4()
    t5 = table5()
    t6, gps = table6()
    tc = table_capacity()
    ss = seed_scatter()
    f7 = fig7(per)
    head = ['# Regenerated manuscript tables (calibrated amplitude axis) — 2026-10-31', '',
            'Source: `docs/source_tables/outputs_rev1/` (copies of `/root/SGWB1/.workspace_rev2/outputs_rev1/`). Script: `real/make_tables.py`.',
            'All limits are log10 Ω_limit per 4 s segment on the Eq. (11) calibrated axis (σ1 per stretch). Δ = Trad − ING-Net in dex.', '',
            '**Amplitude axis.** The old Table II/III values (log10 Ω ≈ −7.3 to −7.6) were produced by the paper-v1 code, whose calibration constant '
            'S_code = √(2∫S_gw/P_n df) carries an extra factor √(2·980 Hz) ≈ 44 relative to the Eq. (11) σ1 = √(∫S_gw/P_n df / 980 Hz) '
            '(rev1 change R2); for the same injected variance, log10 Ω_new = log10 Ω_old + 2 log10(44.3) = log10 Ω_old + 3.29. '
            'The regenerated tables below are all on the new axis, as is Table V, so one axis is used everywhere.', '',
            f'**Seed scatter** (per-cell std over seeds, 75 cells): ING-Net median {ss["ING-Net"]["median"]:.3f}, 90th percentile {ss["ING-Net"]["p90"]:.2f}, '
            f'max {ss["ING-Net"]["max"]:.2f} dex; Trad median {ss["Trad"]["median"]:.3f}, 90th percentile {ss["Trad"]["p90"]:.2f}, max {ss["Trad"]["max"]:.2f} dex '
            f'(diverged seeds excluded). Suggested [X] = 0.1, [Y] = 0.05 (90th percentiles), with the medians quoted alongside.', '']
    open(os.path.join(OUT, 'tables_summary.md'), 'w').write('\n'.join(head + [t2, '', t3, '', t4, '', tc, '', t5, '', t6, '', f'_{f7}_']) + '\n')
    print('\n'.join(head)); print(t2); print(t3); print(t4); print(tc); print(t5); print(t6); print(ss); print(f7)

if __name__ == '__main__':
    main()
