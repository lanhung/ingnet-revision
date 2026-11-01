### Capacity scan (Table IV footnote): MAF hidden units × transforms, three reference stretches, seeds 1400–1401 (mean over the three stretches; the primary row has seeds 1400–1402)

Glitch-augmented training throughout. The power-only baselines do not close the gap to ING-Net with 5× the hidden units or twice the transforms: Trad and Trad-FR move by ≤ 0.1 dex across the scan while Δ stays at +0.56 … +0.73 dex (ξ = 10⁻³) and +0.24 … +0.35 dex (ξ = 10⁻²).

| hidden × transforms | ING ξ=1e-3 | Trad | Trad-FR | Δ | ING ξ=1e-2 | Trad | Trad-FR | Δ | ING ξ=1 | Trad | Trad-FR | Δ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 50 × 5 (primary) | -4.73 | -4.06 | -4.09 | +0.67 | -4.87 | -4.57 | -4.58 | +0.29 | -4.59 | -4.58 | -4.60 | +0.01 |
| 50 × 10 | -4.73 | -4.17 | -4.06 | +0.56 | -4.84 | -4.60 | -4.56 | +0.24 | -4.61 | -4.61 | -4.57 | -0.01 |
| 128 × 5 | -4.80 | -4.07 | -4.09 | +0.73 | -4.91 | -4.57 | -4.58 | +0.34 | -4.60 | -4.57 | -4.60 | +0.02 |
| 128 × 10 | -4.80 | -4.11 | -4.08 | +0.69 | -4.89 | -4.54 | -4.56 | +0.35 | -4.60 | -4.55 | -4.58 | +0.05 |
| 256 × 5 | -4.80 | -4.16 | -4.06 | +0.64 | -4.89 | -4.59 | -4.57 | +0.30 | -4.63 | -4.60 | -4.58 | +0.03 |
| 256 × 10 | -4.81 | -4.14 | -4.13 | +0.67 | -4.91 | -4.58 | -4.60 | +0.33 | -4.61 | -4.59 | -4.61 | +0.03 |
| 256 × 10, lr 2e-4 | -4.76 | -4.13 | -4.07 | +0.63 | -4.89 | -4.57 | -4.57 | +0.32 | -4.60 | -4.58 | -4.58 | +0.02 |
