# Solar Radiation Model Explorer

This existing Streamlit application presents the validated results for the MSc project *Comparative evaluation of temperature-based solar radiation models using global performance indicator*. The project evaluates Ahmedabad, Amreli and Okha using station-specific daily records from 1985–2025, five periods and 16 models.

The app is a consumer of the validated project results. Its bundled `data/demo/` files are summaries generated from `../results/final/`; they do not contain source daily observations. Scientific definitions and analysis are maintained in the root `solar_radiation_analysis.ipynb` notebook.

## Method

The reference is the supplied Karale et al. (2026) paper's Eq. 5 (p. 5):

\[
R_{s,AP}=\left(0.25+0.50\frac{n}{N}\right)R_a,
\]

where (n) is actual bright sunshine duration, (N=24\omega_s/\pi) is maximum sunshine duration and (R_a) is extraterrestrial radiation. Only rows with valid Tmax, Tmin, sunshine, (Tmax>Tmin), (0\le n\le N), and finite estimates from all models are included. All dates are used; no shared station period or year blacklist is applied. Each station-period needs at least 30 valid days.

For the primary results, the study's cited solar-geometry equation calculates (N) in hours from the sunset hour angle and calculates (R_a) in MJ m⁻² day⁻¹ from latitude and day of year. The study prints (d_r=1+0.003\cos(2\pi J/365)); the notebook and dashboard upload engine use that printed coefficient. Measured sunshine hours are used directly as (n), without conversion.

Metrics are RMSE, MAE, signed MBE and (R^2=1-SSE/SST). The GPI min–max scales the four metrics across 16 models within each station-period and applies the paper's directions, α=-1 for R² and +1 for RMSE, MAE and signed MBE. GPI is an unweighted sum; ties share the best rank. A constant metric contributes zero. The paper's statement that MBE should be close to zero conflicts with its printed GPI direction for signed MBE. M2's output units and M8's Θ are not defined in the supplied study; the implementation assumptions and sensitivity results are documented in the project README and model registry.

See the project README and `../results/validation/sensitivity_analysis.csv` for data coverage, equations, exclusions, limitations and ranking sensitivity.

## Run locally

Python 3.11 or newer. Install `requirements.txt`, then run:

```bash
streamlit run app.py
```

Run the scientific pipeline from the project root notebook `solar_radiation_analysis.ipynb` using **Kernel → Restart Kernel and Run All**. Tests are in `tests/` and can be run from this dashboard directory with `pytest`.
