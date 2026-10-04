# Solar Radiation Model Explorer

Streamlit dashboard for the MSc study *Comparative evaluation of temperature-based solar radiation models using global performance indicator*.

## Official study results

The dashboard reads the validated exports produced by the root `solar_radiation_analysis.ipynb` notebook. The notebook is the only authoritative source for the official analysis; this application does not recalculate its 240 result rows or rankings.

- Stations: Ahmedabad, Amreli and Okha only.
- Data coverage: station-specific valid observations from 1985–2025.
- Periods: Annual, Winter (January–February), Pre-Monsoon (March–May), Monsoon (June–September) and Post-Monsoon (October–December).
- Models: M1–M16.
- Official table: `../results/final/all_metrics.csv` (3 stations × 5 periods × 16 models).
- Top-3, station comparisons and valid-date coverage are read from their corresponding notebook exports under `../results/`.

The reference is exactly:

```text
Rs = Ra [0.25 + 0.50(n/N)]
```

Here `Rs` is estimated global solar radiation, `Ra` is extraterrestrial radiation, `n` is measured sunshine duration in hours, and `N` is maximum possible sunshine duration in hours. Official dashboard views display the exported results; they do not recalculate `Ra`, `N`, the reference, model metrics or GPI.

## Dashboard views

- Overview: annual comparison, seasonal Top-3 matrix, leading models and station-specific coverage dates/counts.
- Model Explorer: station and period filters; all 16 models; R², RMSE, MAE, MBE, GPI and notebook ranks; station comparisons; and downloads of notebook exports.
- Methodology: equations, model registry, data rules, GPI directions and documented interpretation notes.
- Upload & Analyze: separate exploratory calculations for a user-supplied file. It uses the notebook-exported model registry and the finalized method conventions where applicable. It never changes the official study tables or rankings.

Daily source observations are not included in the repository. If a local notebook run has created `../results/final/daily_predictions.csv`, the Explorer can show its optional daily comparison; otherwise that view explains why daily values are unavailable. The summary views work from the checked-in aggregate exports.

## Run locally

From this directory, install the dashboard dependencies and start Streamlit:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Run the dashboard tests with:

```bash
python -m pytest -q
```

To regenerate official results, run the root notebook with **Kernel → Restart Kernel and Run All**. The optional upload workflow is not a substitute for that notebook pipeline.
