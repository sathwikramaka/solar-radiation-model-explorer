# Solar Radiation Model Explorer

Interactive dashboard for the MSc Agriculture Analytics project *Solar Radiation Model Evaluation:
Five Gujarat Districts*. Sixteen published temperature-based models (M1–M16) are compared against the
Ångström–Prescott reference and ranked with the Global Performance Indicator (GPI), for the whole year
and for the four IMD seasons, following Karale, Misra, Ghosh & Latwal (2026).

The dashboard **implements the final project notebook without changing the method**. The engine
reproduces every validated project result to within 1e-14 (`tests/test_reproduction.py`).

## Pages

| Page | What it shows |
|---|---|
| Overview | Purpose, the five districts, the method in eight steps |
| Model Explorer | Validated results: best model, Top 3, ranking, all metrics, seasonal comparison, cross-district heatmap |
| Upload & Analyze | Upload → validate → location → calculate → results, with Excel/CSV downloads |
| Methodology | Inputs, QC, solar geometry, reference, the 16 models, metrics, GPI, seasons, assumptions, equations |

## Run locally

Requires Python 3.11 or newer (3.12 recommended).

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows   (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501.

### Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Without the private data, 21 tests run and 6 reproduction tests are skipped (see *Data* below).

## Deploy on Streamlit Community Cloud (free)

1. Push this folder to a GitHub repository (this folder must be the repository root).
2. Go to https://share.streamlit.io → **Create app** → **Deploy a public app from GitHub**.
3. Repository: `<your-username>/solar-radiation-model-explorer`, branch `main`, main file path `app.py`.
4. **Advanced settings → Python version: 3.12.** No secrets are needed.
5. Deploy. The first build takes a few minutes. Free apps sleep after a period without visitors;
   open the link a minute before a demonstration to wake it.

## Uploading your own data

One row per day with Date (or Year/Month/Day), Tmax (°C), Tmin (°C) and sunshine hours; `.xlsx` or
`.csv`. Columns are detected automatically and can be reassigned. Templates are on the upload page.
Differences from the demonstration districts:

- The project's satellite (NASA POWER) sunshine-record check is not applied; years with < 200 sunshine values are flagged.
- All dates in the file are used (the demonstration districts use 2002–2023).
- Rows with an invalid date and all rows of a duplicated date are excluded. Nothing is filled or clipped.
- Temperatures outside −10…55 °C are flagged but kept.
- The station latitude is entered by the user (±66°).

## Data

- `data/demo/` — validated, aggregated project results (metrics, GPI, ranks, Top 3). Public.
- `data/private/` — raw IMD station files and daily predictions. **Git-ignored and never published**
  until redistribution rights are confirmed. Without it the dashboard works fully; only the demo
  "Observed vs predicted" chart and the reproduction tests are unavailable.

## Structure

```
app.py                  entry point (navigation)
engine/                 the scientific method — plain Python, no Streamlit
  config.py             fixed settings and the five flagged assumptions (A–E)
  solar_geometry.py     Ra, day length N (FAO-56), Ångström–Prescott reference
  models.py             M1–M16 (paper Table 2)
  metrics.py            RMSE, MAE, MBE, R² (paper Table 3)
  gpi.py                Global Performance Indicator and rank
  pipeline.py           inclusion rules → … → Top 3, in the notebook's order
  validation.py         reading and checking uploaded files
ui/                     pages, cards, charts and styling
data/demo/              validated aggregated results
tests/                  engine, upload and reproduction tests
.streamlit/config.toml  theme and upload limit
```

## Method assumptions (not yet settled — results are conditional on them)

A · M2 × 3.6 (kWh → MJ) · B · M8 Θ = Tmin/Tmax · C · M16 in the paper's printed form ·
D · R² = 1 − SSE/SST · E · signed MBE in the GPI. Details on the Methodology page.

Reference: Karale, Misra, Ghosh & Latwal (2026), *Seasonal and regional evaluation of sixteen
temperature-based solar radiation models for India using a Global Performance Indicator* (preprint).
