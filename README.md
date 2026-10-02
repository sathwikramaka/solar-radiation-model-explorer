# Solar Radiation Model Explorer

An interactive dashboard for the MSc Agriculture Analytics project *Solar Radiation Model Evaluation:
Five Gujarat Districts*.

**Question:** where only daily temperature and sunshine records exist, which temperature-based model
best estimates daily solar radiation — and does the answer change with the season and the place?

Sixteen published models (M1–M16) are compared against a sunshine-based reference and ranked with the
Global Performance Indicator (GPI), for the whole year and for each IMD season, following
Karale, Misra, Ghosh & Latwal (2026). The dashboard implements the final project notebook **without
changing the method**; its engine reproduces every validated project result to within 1e-14.

**Live app:** see the link in the repository description.

## Pages

| Page | What it shows |
|---|---|
| Overview | Purpose, the five demonstration districts, the method in eight steps |
| Model Explorer | Validated results for Ahmedabad, Amreli, Deesa, Okha, Surat: best model, Top 3, ranking, all metrics, seasonal comparison, cross-district heatmap |
| Upload & Analyze | Run the same method on your own Excel/CSV file and download the results |
| Methodology | The full method, the 16 equations, assumptions and limitations |

## How the analysis works

```
Input → QC → Solar geometry → A–P reference → 16 models → Metrics → GPI → Ranking (Top 3)
```

1. **Input** — daily Tmax, Tmin (°C), bright sunshine hours *n*, and station latitude.
2. **QC** — a day is used only if Tmax and Tmin are present with ΔT = Tmax − Tmin > 0, sunshine is
   present with 0 ≤ n ≤ N, and all 16 models give a finite value. Nothing is filled or clipped.
   A period needs at least 30 valid days.
3. **Solar geometry** (FAO-56) — extraterrestrial radiation Ra and maximum day length N from latitude and day of year.
4. **Reference** — Ångström–Prescott radiation Rs = (0.25 + 0.50·n/N)·Ra. It is the sunshine-based
   standard used by the paper, *not* measured radiation.
5. **16 models** — published temperature-based equations, coefficients as printed, nothing calibrated.
6. **Metrics** — each model's daily estimates are compared with the reference.
7. **GPI** — the four metrics combined into one score.
8. **Ranking** — highest GPI = rank 1; ranks 1–3 are the Top 3.

### Five periods (IMD seasons)

| Period | Months |
|---|---|
| Annual | Jan – Dec |
| Winter | Jan – Feb |
| Pre-Monsoon | Mar – May |
| Monsoon | Jun – Sep |
| Post-Monsoon | Oct – Dec |

### The sixteen models (Rs, Ra in MJ m⁻² d⁻¹; ΔT = Tmax − Tmin; T = mean temperature)

| | Source | Equation |
|---|---|---|
| M1 | Hargreaves & Samani (1985) | 0.16 √ΔT · Ra |
| M2 | Rao et al. (2017) | 3.6 × (1.29 + 0.3626 ΔT) |
| M3 | Richardson / Marif et al. | 0.3124 ΔT^0.2942 · Ra |
| M4 | Sarkar & Sifat / Marif et al. | (0.7730 − 0.0296 ΔT + 0.0016 ΔT²) · Ra |
| M5 | Chen et al. / Marif et al. | (0.2063 + 0.1801 ln ΔT) · Ra |
| M6 | Hargreaves & Riley / Marif et al. | (0.3040 + 0.1008 √ΔT) · Ra |
| M7 | Panday & Katiyar (2010) | (0.2889 + 0.1562 Tmax/Tmin) · Ra |
| M8 | Falayi et al. (2008) | (1.7217 − 1.691 Tmin/Tmax) · Ra |
| M9 | Chen et al. (2004) | (0.28 ln ΔT + 0.15) · Ra |
| M10 | Ertekin & Yaldiz (1999) | −4.46 + 0.477 Ra − 0.226 T |
| M11 | Sivamadhavi & Selvaraj (2012) | (0.4610 + 0.0029 ΔT) · Ra |
| M12 | Sivamadhavi & Selvaraj (2012) | (0.5290 + 0.0516 Tmin/Tmax) · Ra |
| M13 | Hassan et al. / Ghazouani et al. | (0.206590 + 0.026851 Tmax − 0.024184 Tmin) · Ra |
| M14 | Kirmani et al. (2015) | (0.85235 − 0.00997 T) · Ra |
| M15 | Hargreaves & Samani / Onyeka et al. | (0.236 + 0.106 √ΔT) · Ra |
| M16 | Samani (2000) | (0.00185 ΔT² − 0.0433 ΔT + 0.4023) · Ra |

### Metrics and GPI

| Metric | Meaning | Best |
|---|---|---|
| RMSE | typical error size; penalises large errors | 0 |
| MAE | average error size | 0 |
| MBE | systematic bias (+ overestimates, − underestimates) | 0 |
| R² | 1 − SSE/SST: share of the reference's variation explained (can be negative) | 1 |

**GPI** — within one site and period, each metric is scaled to 0–1 across the 16 models. A model gains
score for every metric on which it beats the median model:
GPI = Σ α·(median − scaled value), with α = −1 for R² and +1 for RMSE, MAE and MBE. Higher is better.

### Assumptions (not yet settled — rankings are conditional on them)

- **A** M2 multiplied by 3.6 (printed result read as kWh → MJ).
- **B** M8 uses Θ = Tmin/Tmax (Θ is not defined in the paper).
- **C** M16 in the paper's printed form (no √ΔT).
- **D** R² = 1 − SSE/SST, the paper's formula (its printed values behave like a correlation r²).
- **E** MBE enters the GPI with its sign, as in the paper.

## Upload your own data

Use **Upload & Analyze**. One row per day, `.xlsx` or `.csv`:

| Column | Meaning | Unit / example | Also recognised as |
|---|---|---|---|
| Date | calendar date | 2020-01-31 or 31/01/2020 | or three columns Year, Month, Day (e.g. IMD `YEAR`, `MN`, `DT`) |
| Tmax | daily maximum temperature | °C | `MAX`, `Max Temp` |
| Tmin | daily minimum temperature | °C | `MIN`, `Min Temp` |
| SSH | bright sunshine duration | hours | `Sunshine`, `BSS` |

Example:

```
Date,Tmax,Tmin,SSH
2020-01-01,28.4,12.2,9.6
2020-01-02,29.1,13.0,9.2
```

Then enter the station latitude and press **Run the 16 models**. Columns are matched automatically
only when exactly one column fits; otherwise you choose. Leave gaps blank — do not fill them.
Downloadable templates are on the upload page.

Compared with the demonstration districts:

- the project's satellite (NASA POWER) sunshine-record check cannot be run; years with < 200 sunshine values are flagged;
- all dates in the file are used (the demonstration districts use 2002–2023);
- rows with an invalid date and all rows of a duplicated date are excluded; every exclusion is listed with its reason;
- temperatures outside −10…55 °C are flagged but kept.

Results download as one Excel workbook (settings, metrics, GPI, ranking, Top 3, daily predictions,
excluded rows, validation messages) or as separate CSV files. Files are processed in memory by the app
and are not stored.

## Run locally

Python 3.11 or newer (3.12 recommended).

```bash
python -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt` then `pytest`.

## Public deployment

The app runs free on Streamlit Community Cloud from this repository (branch `main`, file `app.py`,
Python 3.12). Every push to `main` redeploys automatically. Free apps sleep when unused; the first
visit after a pause takes about a minute to wake.

## Data and privacy

- `data/demo/` — the project's validated, **aggregated** results (metrics, GPI, ranks, Top 3). No daily observations.
- Raw IMD station data and daily predictions are **not** published until redistribution rights are
  confirmed. They live in a git-ignored `data/private/` folder on the author's machine. Without it the
  app works fully; only the demo "Observed vs predicted" chart and the reproduction tests are unavailable.

## Project structure

```
app.py                  entry point (navigation)
engine/                 the scientific method — plain Python, no Streamlit
  config.py             fixed settings and assumptions A–E
  solar_geometry.py     Ra, N (FAO-56), Ångström–Prescott reference
  models.py             M1–M16
  metrics.py            RMSE, MAE, MBE, R²
  gpi.py                GPI and rank
  pipeline.py           QC → … → Top 3, in the notebook's order
  validation.py         reading and checking uploaded files
ui/                     pages, cards, charts, styling
data/demo/              validated aggregated results
tests/                  engine, upload and reproduction tests
```

## Reference

Karale, Misra, Ghosh & Latwal (2026). *Seasonal and regional evaluation of sixteen temperature-based
solar radiation models for India using a Global Performance Indicator* (preprint).

## Licence

MIT — see `LICENSE`.
