# Scientific project audit

## Final study design and coverage

- Objective: compare 16 temperature-based daily solar-radiation models against the project's sunshine-duration reference at Ahmedabad, Amreli and Okha.
- Periods: Annual, Winter, Pre-Monsoon, Monsoon and Post-Monsoon; the exported metric table has exactly 240 unique station-period-model rows.
- Each raw file spans 1985–2025. Usable records: Ahmedabad 14,802 (1985-01-01–2025-12-23), Amreli 14,718 (1985-01-01–2025-12-31), Okha 14,474 (1985-01-01–2025-12-31). No common date window is imposed.
- `results/qc/data_provenance.csv`, `results/qc/year_coverage.csv`, and `results/qc/qc_report.csv` record coverage and exclusions.

## Reference radiation and solar geometry

The primary source, Karale et al. (2026), supplied preprint, Eq. 5, p. 5, gives `Rs_AP = (0.25 + 0.50 n/N) Ra`, where `n` is measured bright-sunshine duration in hours, `N = 24 ws/pi` is maximum astronomical day length in hours, `ws` is sunset hour angle in radians, and `Ra` is extraterrestrial radiation in MJ m-2 day-1. The reference uses sunshine duration; Tmin/Tmax are not inputs.

The same paper's Eq. 2, p. 5, prints `dr = 1 + 0.003 cos(2 pi J/365)`. That is a typo: FAO-56 Eq. 23 (the source of Eq. 1–4) uses 0.033, and the supplied Sarkar (2016) uses 0.033, Tripathy et al. (2008) and Almorox et al. (2013) 0.034. Primary outputs use 0.033; the printed 0.003 is a sensitivity case. `Gsc=0.0820` is used with the conventional MJ m-2 min-1 unit and 24×60 conversion; the supplied paper appears to label its unit inconsistently.

## Model equations and unresolved interpretations

The authoritative equations and model registry are embedded in `solar_radiation_analysis.ipynb` and exported from that notebook to `results/model_registry.csv`. Published equations are recorded separately from implemented equations.

- M2: the primary table omits output units; the supplied secondary companion writes an H/H0 form, so the sources conflict. The ×3.6 implementation is an explicit assumption and a no-conversion sensitivity is reported.
- M8: Theta is undefined in the primary table, and the supplied papers do not include the original Falayi equation; the implementation assumes `Theta=Tmin/Tmax`, by analogy with M12.
- M9 and M10: kept as printed, but their outputs are physically implausible (M9 exceeds the clear-sky limit whenever dT > 8.6 °C; M10 gives Rs/Ra ≈ 0.15 against ≈ 0.59 for the reference). Their coefficients could not be verified against Chen et al. (2004) or Ertekin & Yaldiz (1999).
- M16: Table 2 prints only the KT polynomial. The original Samani (2000) model is `Rs = KT * sqrt(dT) * Ra`, given with the same coefficients in the supplied Almorox et al. (2013), Eq. 9, so the √dT factor is restored; the printed form is a sensitivity case.

## Metrics, GPI and ranking

RMSE, MAE, signed MBE and R² are calculated within each station-period. R² is the coefficient of determination r² (squared Pearson correlation, always 0–1). The paper prints `1-SSE/SST`, but its Table 4 values are r² (Bhubaneswar annual M-5: R² 0.40 with RMSE 5.28 and MBE −3.75, which `1-SSE/SST` cannot give); `1-SSE/SST` is negative for any strongly biased model and is reported only as a sensitivity.

GPI min-max scales each indicator among the 16 models, subtracts each scaled value from its metric median, and sums using the printed signs: -1 for R², +1 for RMSE, MAE and MBE. MBE is scaled as |MBE| because its ideal value is 0; scaling signed MBE would reward the most negative bias (M10, MBE ≈ −14, would score best on bias), so signed MBE is a sensitivity. The four contributions are equal; there are no additional weights. A constant metric contributes zero. GPI is rounded to 10 decimals for ranking; descending GPI determines rank and ties share minimum rank.

Remaining negative values are expected: MBE is negative when a model underestimates, and GPI is negative when a model is worse than the median model.

## Primary annual leaders and repeat Top-3 appearances

Annual Top 3: Ahmedabad M1/M13/M15; Amreli M15/M1/M13; Okha M9/M5/M3. Across all 15 station-periods, Top-3 counts are M15 (10), M5 (8), M14 (5), M1, M12 and M13 (4 each), M4 and M6 (3 each), M3 (2), and M2 and M9 (1 each). M7, M8, M10, M11 and M16 do not enter the primary Top 3.

Top-3 sets preserved out of 15 under each sensitivity: d_r = 0.003 15, M16 without √dT 15, M2 without ×3.6 13, signed MBE 10, R² = 1-SSE/SST 2. Per-cell rankings are in `results/validation/sensitivity_analysis.csv` and `results/final/`.

## Reproduction and validation

Run the sole scientific pipeline by opening `solar_radiation_analysis.ipynb` and choosing **Kernel → Restart Kernel and Run All**. It exports the complete tables, QC/provenance, 19 validation checks (all PASS, including R² within 0–1, MAE ≤ RMSE and |MBE| ≤ MAE), figures, and `results/validation/output_hashes.csv`. The dashboard tests check that the dashboard engine reproduces the notebook's metrics, GPI and ranks. Data exclusions are documented row-by-row in `results/final/daily_predictions.csv`; observations are not imputed or shifted.

The original research PDFs are preserved. A supplied secondary study companion is not used as the method authority where it conflicts with the primary paper. This file is maintained by hand; the notebook does not regenerate it.
