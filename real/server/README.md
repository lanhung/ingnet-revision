# Server-side helpers (run on the SGWB1 server, not locally)

The project's server copy lives in `/root/ingnet-revision/` (`real/` = this directory's parent, `real/results/` = run
outputs, `scratch/` = these helpers). `/root/SGWB1/` is read-only source material.

- `launch.sh` — launches the six option-(b) runs of 2026-10-31 (three reference stretches with `--synthetic`, the
  twelve rev1x stretches real-only) on the two GPUs. Use `setsid nohup … < /dev/null &` rather than plain `nohup`:
  two of the six runs were killed silently at the server's local midnight and were finished with `--resume`.
- `smoke_test.py` — N = 1 smoke test of the filled adapters against the rev2 pipeline (limits, log_prob against
  `DirectPosterior.log_prob`, injected variance = Ω σ1², real against synthetic P scatter). Output of the 2026-10-31
  run is quoted in `../../CLAUDE.md` and `../../docs/manuscript_fixes_2026-10-31.md`.
- `../gridcheck_option_b.py` — grid-resolution check; output `../results/gridcheck_03A_seed1400.json`.

Logs of the runs are in `../results/*.log` (`*.part1.log` = the part before the midnight kill).
