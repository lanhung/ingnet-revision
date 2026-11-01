# ingnet-revision

Revision work for the ING-Net manuscript (referee comments 3 and 10). Open this folder in Claude Code
(`cd ingnet-revision && claude`); `CLAUDE.md` holds the project memory, the current state, and the next
tasks in order. The original codebase and data are expected at `/root/SGWB1/` (read-only source).

- `synthetic/` — three-rule accumulation test on synthetic data (done 2026-10-30; results and figure included)
- `real/` — option (b) on the trained networks: `option_b_real.py` (adapters filled 2026-10-31, runs on the
  server), `analyze_option_b.py` (merges `real/results/option_b_*.json`, gain table, coverage, figure),
  `make_tables.py` (regenerates manuscript Tables II–VI on the calibrated axis into `docs/tables/`),
  `gridcheck_option_b.py` (server-side check that the 0.1 dex grid does not bias the product rule).
  `real/results/` holds the six run outputs (`option_b_{O3a,O3b,O4a}_{ref,x}.json` + logs), the analysis
  (`option_b_summary.md/.json`, `option_b_gain_table.csv`, `option_b_coverage.csv`, `option_b_rules.csv`,
  `option_b_gain_vs_duration.png/.pdf`) and `gridcheck_03A_seed1400.json`.
- `docs/` — report, draft response to the referee, draft manuscript text, the Oct-30 memo,
  `manuscript_fixes_2026-10-31.md` (itemised second-round fixes), `tables/` (regenerated tables and Fig. 7),
  `source_tables/` (small per-run result files copied from `/root/SGWB1`)
- `manuscript/` — manuscript draft of 2026-10-31 (PDF only; its LaTeX source is not on the server)
