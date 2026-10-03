# Scientific project audit

## Final study design and coverage

- Objective: compare 16 temperature-based daily solar-radiation models against the project's sunshine-duration reference at Ahmedabad, Amreli and Okha.
- Periods: Annual, Winter, Pre-Monsoon, Monsoon and Post-Monsoon; the exported metric table has exactly 240 unique station-period-model rows.
- Each raw file spans 1985–2025. Usable records: Ahmedabad 14,802 (1985-01-01–2025-12-23), Amreli 14,718 (1985-01-01–2025-12-31), Okha 14,474 (1985-01-01–2025-12-31). No common date window is imposed.
- `results/qc/data_provenance.csv`, `results/qc/year_coverage.csv`, and `results/qc/qc_report.csv` record coverage and exclusions.

## Reference radiation and solar geometry

The primary source, Karale et al. (2026), supplied preprint, Eq. 5, p. 5, gives `Rs_AP = (0.25 + 0.50 n/N) Ra`, where `n` is measured bright-sunshine duration in hours, `N = 24 ws/pi` is maximum astronomical day length in hours, `ws` is sunset hour angle in radians, and `Ra` is extraterrestrial radiation in MJ m-2 day-1. The reference uses sunshine duration; Tmin/Tmax are not inputs.

The same paper's Eq. 2, p. 5, prints `dr = 1 + 0.003 cos(2 pi J/365)`. Primary outputs now use 0.003. The former implementation used 0.033; the notebook retains that as an alternative sensitivity only. `Gsc=0.0820` is used with the conventional MJ m-2 min-1 unit and 24×60 conversion; the supplied paper appears to label its unit inconsistently.

## Model equations and unresolved interpretations

The authoritative equations and model registry are embedded in `solar_radiation_analysis.ipynb` and exported from that notebook to `results/model_registry.csv`. Published equations are recorded separately from implemented equations. M2's primary-table entry omits output units; the supplied secondary companion writes an H/H0 form, so the sources conflict. The ×3.6 implementation is an explicit assumption and no-conversion sensitivity is reported. M8's Theta is undefined in the primary table, and the supplied papers do not include the original Falayi equation; the implementation assumes `Theta=Tmin/Tmax`, by analogy with M12. M16 follows the printed form without a square root.

## Metrics, GPI and ranking

RMSE, MAE, signed MBE and the paper's printed `R2=1-SSE/SST` are calculated within each station-period. GPI min-max scales each indicator among the 16 models, subtracts each scaled value from its metric median, and sums using the printed signs: -1 for R2, +1 for RMSE, MAE and signed MBE. The four contributions are equal; there are no additional weights. A constant metric contributes zero. GPI is rounded to 10 decimals for ranking; descending GPI determines rank and ties share minimum rank.

The paper calls zero-closer MBE ideal, but its printed positive sign for signed MBE can reward more negative bias. The primary results follow the printed equation; absolute-MBE is a sensitivity. The paper's R2 table values also appear consistent with Pearson-r-squared in places; the primary results use the printed coefficient-of-determination equation and record Pearson-r-squared sensitivity.

## Primary annual leaders and repeat Top-3 appearances

Annual Top 3: Ahmedabad M1/M13/M15; Amreli M1/M15/M13; Okha M5/M6/M3. Across all 15 station-periods, Top-3 counts are M1 (10), M15 (9), M14 (6), M13 and M5 (4 each), M12 (3), M4 and M6 (2 each), and M2/M3/M7/M8/M9 (1 each). M10, M11 and M16 do not enter the primary Top 3.

Changing the distance coefficient from 0.003 to 0.033 preserves 15/15 Top-3 sets in the current output. Other sensitivities and per-cell rankings are in `results/validation/sensitivity_analysis.csv` and `results/final/`.

## Reproduction and validation

Run the sole scientific pipeline by opening `solar_radiation_analysis.ipynb` and choosing **Kernel → Restart Kernel and Run All**. It exports the complete tables, QC/provenance, validation checks, figures, and `results/validation/output_hashes.csv`. Data exclusions are documented row-by-row in `results/final/daily_predictions.csv`; observations are not imputed or shifted.

The original research PDFs are preserved. A supplied secondary study companion is not used as the method authority where it conflicts with the primary paper. The existing presentation has been left unchanged for its later phase.
