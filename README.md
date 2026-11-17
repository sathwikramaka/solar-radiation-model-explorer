<div align="center">

# ☀️ Solar Radiation Model Explorer — Gujarat

**Which temperature-based model best estimates daily solar radiation where no pyranometer exists?**
16 published models, 3 IMD stations, 41 years of daily data, ranked season by season with a Global Performance Indicator.

[![Notebook](https://img.shields.io/badge/Analysis_notebook-Open-00d4ff?style=for-the-badge&logo=jupyter&logoColor=white)](code/solar_radiation_analysis.ipynb)
[![Results](https://img.shields.io/badge/Result_tables-Browse-00ff88?style=for-the-badge&logo=databricks&logoColor=white)](results/final)
[![Dashboard](https://img.shields.io/badge/Dashboard-Run_locally-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](dashboard)

![Python](https://img.shields.io/badge/Python_3.11+-3776AB?logo=python&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?logo=numpy&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?logo=jupyter&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)

<img src="figures/final/seasonal_ranks.png" width="760" alt="Seasonal GPI ranks of the 16 models at each station">

</div>

---

## 📊 Key results

| | Result |
|---|---|
| 🥇 **Annual leader, Ahmedabad** | **M1** · then M13, M15 |
| 🥇 **Annual leader, Amreli** | **M15** · then M1, M13 |
| 🥇 **Annual leader, Okha** (coastal) | **M9** · then M5, M3 |
| 🔁 **Most consistent across all 15 station-periods** | M15 in the Top 3 ten times, M5 eight times, M14 five |
| ❌ **Never in a Top 3** | M7, M8, M10, M11, M16 |
| 📉 **Annual R²** | 0.02 – 0.50; at coastal Okha every model stays below 0.15 |
| 📅 Data | 14,474 – 14,802 valid days per station, 1985–2025 (IMD) |

> The reference is the sunshine-based Ångström–Prescott estimate, **not a pyranometer measurement**. Rankings describe agreement with that reference method.

## 🔍 What makes it different

- **Every assumption written down** — where the source paper is ambiguous (M2 units, M8's Θ, M16's missing √ΔT, the MBE direction in GPI, the d<sub>r</sub> coefficient, the R² definition) the choice is stated, checked against the supplied references and tested in a sensitivity table.
- **Seasonal, not just annual** — Winter, Pre-Monsoon, Monsoon and Post-Monsoon ranked separately at each station, because the best model changes with the season.
- **Nothing filled or patched** — raw IMD rows are kept as delivered; excluded days stay visible with a reason.
- **Reproducible end to end** — one notebook regenerates every table and figure; SHA-256 hashes and structural checks are exported with the results.
- **Use it on your own station** — the Streamlit dashboard runs the same 16 models on an uploaded file, kept separate from the official results.

## 🛰️ Data

**IMD** daily station records (T<sub>max</sub>, T<sub>min</sub>, bright sunshine hours) for **Ahmedabad · Amreli · Okha**, 1985–2025 · model equations from Karale et al. (2026), Table 2

## 📈 Figures

| Annual ranks | Top-3 frequency | Annual-winner residuals |
|---|---|---|
| <img src="figures/final/annual_ranks.png" width="280"> | <img src="figures/final/top3_frequency.png" width="280"> | <img src="figures/final/residuals.png" width="280"> |

## 🚀 Run it yourself

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

| Want to… | Do this |
|---|---|
| Reproduce the study | Put the three authorised IMD files in `data/raw_imd/`, open `code/solar_radiation_analysis.ipynb`, **Kernel → Restart and Run All** |
| Explore the results | `cd dashboard && pip install -r requirements.txt && streamlit run app.py` |
| Run the dashboard tests | `cd dashboard && pip install -r requirements-dev.txt && pytest` |

The raw station files and `results/final/daily_predictions.csv` are not in Git, because redistribution permission for the IMD data has not been confirmed. All aggregate results and figures are.

<details>
<summary><b>Data coverage by station</b></summary>

The analysis reads only the three retained daily files under `data/raw_imd/`. Each has date (`YEAR`, `MN`, `DT`), maximum and minimum temperature (`MAX`, `MIN`, °C), and bright sunshine duration (`SSH`, hours). The supplied files are retained as delivered; no observations are filled, shifted, clipped or recalibrated.

| Station | File records | Raw date span | Valid daily records used | First–last valid date |
|---|---:|---|---:|---|
| Ahmedabad | 14,973 | 1985-01-01–2025-12-31 | 14,802 | 1985-01-01–2025-12-23 |
| Amreli | 14,959 | 1985-01-01–2025-12-31 | 14,718 | 1985-01-01–2025-12-31 |
| Okha | 14,958 | 1985-01-01–2025-12-31 | 14,474 | 1985-01-01–2025-12-31 |

The date spans above are not claims of complete daily coverage. See [`results/qc/year_coverage.csv`](results/qc/year_coverage.csv) for the valid day count in each station-year, [`results/qc/qc_report.csv`](results/qc/qc_report.csv) for exclusions, and [`results/qc/data_provenance.csv`](results/qc/data_provenance.csv) for source and usable spans. Different stations and years contribute different numbers of days.

</details>

<details>
<summary><b>Reference radiation: Ångström–Prescott</b></summary>

The supplied primary study, Karale, Misra, Ghosh & Latwal (2026), *Seasonal and regional evaluation of sixteen temperature-based solar radiation models for India using a Global Performance Indicator*, states Eq. 5 on p. 5 as:

\[
R_{s,AP}=\left(a+b\frac{n}{N}\right)R_a,
\qquad a=0.25,\quad b=0.50.
\]

Here, (R_{s,AP}) is the reference global solar radiation (MJ m⁻² day⁻¹), (n) is actual bright sunshine duration (hours), (N=24\omega_s/\pi) is maximum possible sunshine duration (hours), and (R_a) is extraterrestrial radiation (MJ m⁻² day⁻¹). The station latitude and day of year determine (N) and (R_a). The paper does not use Tmin/Tmax in this reference equation. Only days with (0\le n\le N) receive a reference value.

Solar geometry follows the supplied primary paper, Eq. 2–4, p. 5. The paper prints the Earth–Sun distance factor as (d_r=1+0.003\cos(2\pi J/365)). That is a typo: the factor varies by about ±3.3 % over the year, and FAO-56 Eq. 23 (Allen et al., 1998), the source of Eq. 1–4, uses 0.033. The supplied references agree: Sarkar (2016) uses 0.033, and Tripathy et al. (2008) and Almorox et al. (2013) use 0.034. The primary results use 0.033; the printed 0.003 is a sensitivity case. The implementation uses (G_{sc}=0.0820) MJ m⁻² min⁻¹ with the standard 24×60 conversion; the supplied paper appears to mislabel this constant's unit.

</details>

<details>
<summary><b>The 16 models (equations and assumptions)</b></summary>

All (R_s) outputs are treated as MJ m⁻² day⁻¹. (\Delta T=T_{max}-T_{min}), (T=(T_{max}+T_{min})/2), and (R_a) is extraterrestrial radiation. The equations below follow Karale et al. (2026), Table 2, pp. 7–8. Input requirements, source, units and interpretation notes are in the registry CSV.

| ID | Equation |
|---|---|
| M1 | (0.16\sqrt{\Delta T}\,R_a) |
| M2 | (3.6(1.29+0.3626\Delta T)) **(unit conversion assumption)** |
| M3 | (0.3124\Delta T^{0.2942}R_a) |
| M4 | ((0.7730-0.0296\Delta T+0.0016\Delta T^2)R_a) |
| M5 | ((0.2063+0.1801\ln\Delta T)R_a) |
| M6 | ((0.3040+0.1008\sqrt{\Delta T})R_a) |
| M7 | ((0.2889+0.1562T_{max}/T_{min})R_a) |
| M8 | ((1.7217-1.691\Theta)R_a, \Theta=T_{min}/T_{max}) **(interpretation assumption)** |
| M9 | ((0.28\ln\Delta T+0.15)R_a) **(as printed; implausible output)** |
| M10 | (-4.46+0.477R_a-0.226T) **(as printed; implausible output)** |
| M11 | ((0.4610+0.0029\Delta T)R_a) |
| M12 | ((0.5290+0.0516T_{min}/T_{max})R_a) |
| M13 | ((0.206590+0.026851T_{max}-0.024184T_{min})R_a) |
| M14 | ((0.85235-0.00997T)R_a) |
| M15 | ((0.236+0.106\sqrt{\Delta T})R_a) |
| M16 | ((0.00185\Delta T^2-0.0433\Delta T+0.4023)\sqrt{\Delta T}\,R_a) **(original Samani form; √ΔT restored)** |

Primary Table 2 prints M2 as (H=1.29+0.3626\Delta T) without units; a supplied secondary companion instead writes it as (H/H_0). The sources do not establish the factor 3.6, which is retained only as an implementation assumption and compared with no conversion in the sensitivity analysis. M8's (\Theta) is undefined in the primary table and the original Falayi equation is not included in the supplied papers; the implementation uses (T_{min}/T_{max}) by analogy with M12, explicitly as an assumption. Table 2 prints M16 as only the KT polynomial; the original Samani (2000) model is (R_s=K_T R_a\sqrt{\Delta T}), as given with the same coefficients in the supplied Almorox et al. (2013), Eq. 9. Without (\sqrt{\Delta T}) the model averages (R_s/R_a\approx0.19) against about 0.59 for the reference (MBE about −14 MJ m⁻² d⁻¹), so the original form is used and the printed form is a sensitivity case. M9 and M10 are kept as printed, but their outputs are physically implausible: M9 exceeds the clear-sky limit (R_s/R_a\approx0.75) whenever (\Delta T>8.6) °C, and M10 averages (R_s/R_a\approx0.15). Their coefficients could not be checked against Chen et al. (2004) and Ertekin & Yaldiz (1999). These points require confirmation from the original cited papers/research group.

</details>

<details>
<summary><b>Inclusion rules and data quality</b></summary>

A daily row contributes to a station-period only when both temperatures and sunshine are present, (T_{max}>T_{min}), (0\le n\le N), and all 16 model outputs are finite. No minimum station-year completeness threshold is imposed. Each station-period requires at least 30 valid daily rows; the minimum is met for every reported cell. Excluded rows remain visible with reasons in `results/final/daily_predictions.csv`.

No station-year completeness filter is imposed. Zero-sunshine days are kept as observed. They fall mainly in the monsoon, but Amreli has 38 dry-season zero-sunshine days with ΔT > 12 °C that may be missing values recorded as 0; they are about 0.3 % of its days. Amreli's one SSH value of 108 h is excluded by the (n\le N) rule. Potential date shifts or systematic sunshine-record errors that are not detectable through these row-level rules remain a limitation and need confirmation from the data provider or research group.

</details>

<details>
<summary><b>Evaluation metrics</b></summary>

For daily model estimate (P_i) and reference (O_i), calculated within each station and period:

- **RMSE** (=\sqrt{\frac1n\sum(P_i-O_i)^2}); lower is better.
- **MAE** (=\frac1n\sum|P_i-O_i|); lower is better.
- **MBE** (=\frac1n\sum(P_i-O_i)); positive values indicate overestimation, negative values underestimation, and zero is ideal.
- **R²** (=r^2=\left(\frac{\sum(P_i-\bar P)(O_i-\bar O)}{\sqrt{\sum(P_i-\bar P)^2\sum(O_i-\bar O)^2}}\right)^2), the coefficient of determination; always 0–1, higher is better. The paper prints (1-SSE/SST), but its Table 4 values are r²: Bhubaneswar annual M-5 has R² = 0.40 with RMSE 5.28 and MBE −3.75, which (1-SSE/SST) cannot give. (1-SSE/SST) turns negative for any strongly biased model and is reported only as a sensitivity. The supplied Almorox et al. (2013) and Sarkar (2016) also print (1-SSE/SST), but for locally calibrated models with near-zero bias, where it is close to r²; the models here are uncalibrated.

</details>

<details>
<summary><b>GPI and ranking method</b></summary>

Karale et al. (2026), §2.3.1 and Table 3 (p. 8), first min–max scales each indicator across the 16 models in each station-period: (y_{ij}=(x_{ij}-\min x_j)/(\max x_j-\min x_j)). It then computes

\[
GPI_i=\sum_j\alpha_j(\tilde y_j-y_{ij}),\qquad
\alpha_{R^2}=-1,\quad\alpha_{RMSE}=\alpha_{MAE}=\alpha_{MBE}=+1,
\]

where (\tilde y_j) is the median scaled value. MBE is scaled as (|MBE|), because Table 3 gives its ideal value as 0. This is the paper's unweighted sum; no additional weights are used. Rank is descending GPI. GPI values are rounded to 10 decimal places for ranking; tied models share the best rank (`min` rank), so a Top 3 can contain more than three models in a tie. A constant indicator has a zero contribution rather than producing a division-by-zero result.

Applying the (+1) direction to signed MBE would reward the most negative bias: M10, with MBE ≈ −14 MJ m⁻² d⁻¹, would score best on bias. The primary results therefore use (|MBE|); the tables still report signed MBE, so its sign shows over- or underestimation. `results/validation/sensitivity_analysis.csv` reports the printed alternatives: signed MBE, (1-SSE/SST), M2 without ×3.6, M16 without (\sqrt{\Delta T}), and d_r=0.003.

Negative values that remain are expected. MBE is negative when a model underestimates. GPI is negative when a model is worse than the median model.

</details>

<details>
<summary><b>Every result file</b></summary>

- `results/final/all_metrics.csv`: all 240 station-period-model combinations, including metrics, GPI, rank, status and sample count.
- `results/final/annual_metrics.csv`, `results/final/seasonal_metrics.csv`, `results/final/annual_gpi.csv`, `results/final/seasonal_gpi.csv`: convenient filtered tables.
- `results/final/top_3_models.csv`, `results/final/model_ranking.csv`, `results/final/top3_frequency.csv`, `results/final/station_comparison.csv`, `results/final/district_comparison.csv`: rankings and summaries.
- `results/final/daily_predictions.csv`: source-day values, reference, all model estimates, inclusion flag and exclusion reason.
- `results/final/station_period_summary.csv`: usable sample sizes and date spans for each period.
- `results/model_registry.csv`: authoritative model definitions.
- `results/qc/data_provenance.csv`, `results/qc/year_coverage.csv`, `results/qc/qc_report.csv`: coverage and exclusions.
- `results/validation/sensitivity_analysis.csv`: effect of M2 units/conversion, the printed M16 form, R² definition, MBE treatment and the solar-geometry coefficient.
- `results/validation/output_hashes.csv`: SHA-256 fingerprints for exported result CSVs and figures.
- `results/validation/validation_checks.csv`: generated structural, finite-value and reproducibility checks.
- `results/final/model_cross_district_summary.csv`: cross-station model summary.
- `figures/final/`: annual ranks and metrics, seasonal ranks, Top-3 frequency, and annual-winner residuals.

</details>

<details>
<summary><b>Folder layout</b></summary>

```
code/solar_radiation_analysis.ipynb   sole source of the official analysis
data/raw_imd/                         three IMD inputs (kept local, not in Git)
results/final/                        metrics, GPI, rankings, summaries
results/qc/                           provenance, coverage, exclusions
results/validation/                   checks, sensitivity, output hashes
results/model_registry.csv            model definitions (generated)
figures/final/                        published figures
dashboard/                            Streamlit explorer + tests
Research_References/                  source papers
presentation/                         slide decks (New/ PowerPoint, html/ web); pre-correction versions in Old/
```

</details>

## ⚠️ Limitations

The reference radiation is itself a model (Ångström–Prescott with fixed a = 0.25, b = 0.50), so a high rank means close agreement with that estimate, not with measured radiation. M2's unit conversion and M8's Θ need confirmation from the original authors, and M9 and M10 give physically implausible values as printed; the sensitivity table shows how much the documented choices move the rankings. Date shifts or systematic sunshine-record errors that pass the row-level checks would not be caught.

## 📚 Research source

Karale, P., Misra, V., Ghosh, K. & Latwal, S. (2026). *Seasonal and regional evaluation of sixteen temperature-based solar radiation models for India using a Global Performance Indicator*. Research Square preprint v1, DOI: 10.21203/rs.3.rs-8639991/v1. The supplied PDF is `Research_References/1. Seasonal_and_regional_evaluation_of_sixteen_temper.pdf`.

Other supplied research papers are preserved in `Research_References/`; they were reviewed as context and are not silently treated as substitutes for definitions absent from the main study.

## 👥 Team

1. Sathwik
2. Yaswanthi
3. Het
4. Shreya
5. Gayatri
6. Gopal
