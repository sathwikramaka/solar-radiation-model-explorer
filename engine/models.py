"""The sixteen temperature-based models (paper Table 2), copied from notebook Cell 8.

Published coefficients, nothing calibrated. Output in MJ m-2 d-1.
dT = Tmax - Tmin, Tmean = (Tmax + Tmin) / 2, Ra from solar_geometry.
"""
import numpy as np
import pandas as pd

MODEL_INFO = {
    "M1":  ("Hargreaves & Samani (1985)",                         "Rs = 0.16 √ΔT · Ra"),
    "M2":  ("Rao et al. (2017)",                                  "Rs = 3.6 × (1.29 + 0.3626 ΔT)   [assumption A: kWh → MJ]"),
    "M3":  ("Richardson (2018) / Marif et al. (2022)",            "Rs = 0.3124 ΔT^0.2942 · Ra"),
    "M4":  ("Sarkar & Sifat (2016) / Marif et al. (2022)",        "Rs = (0.7730 − 0.0296 ΔT + 0.0016 ΔT²) · Ra"),
    "M5":  ("Chen et al. (2004) / Marif et al. (2022)",           "Rs = (0.2063 + 0.1801 ln ΔT) · Ra"),
    "M6":  ("Hargreaves & Riley (1985) / Marif et al. (2022)",    "Rs = (0.3040 + 0.1008 √ΔT) · Ra"),
    "M7":  ("Panday & Katiyar (2010)",                            "Rs = (0.2889 + 0.1562 Tmax/Tmin) · Ra"),
    "M8":  ("Falayi et al. (2008)",                               "Rs = (1.7217 − 1.691 Tmin/Tmax) · Ra   [assumption B: Θ = Tmin/Tmax]"),
    "M9":  ("Chen et al. (2004)",                                 "Rs = (0.28 ln ΔT + 0.15) · Ra"),
    "M10": ("Ertekin & Yaldiz (1999)",                            "Rs = −4.46 + 0.477 Ra − 0.226 Tmean"),
    "M11": ("Sivamadhavi & Selvaraj (2012)",                      "Rs = (0.4610 + 0.0029 ΔT) · Ra"),
    "M12": ("Sivamadhavi & Selvaraj (2012)",                      "Rs = (0.5290 + 0.0516 Tmin/Tmax) · Ra"),
    "M13": ("Hassan et al. (2016) / Ghazouani et al. (2022)",     "Rs = (0.206590 + 0.026851 Tmax − 0.024184 Tmin) · Ra"),
    "M14": ("Kirmani et al. (2015)",                              "Rs = (0.85235 − 0.00997 Tmean) · Ra"),
    "M15": ("Hargreaves & Samani (1982) / Onyeka et al. (2021)",  "Rs = (0.236 + 0.106 ΔT^0.5) · Ra"),
    "M16": ("Samani (2000)",                                      "Rs = (0.00185 ΔT² − 0.0433 ΔT + 0.4023) · Ra   [assumption C: paper form]"),
}


def predict_all(Tmax, Tmin, Ra):
    """Return a DataFrame with columns M1..M16. Models are undefined where dT <= 0 (NaN)."""
    Tmax, Tmin, Ra = (pd.Series(x, dtype=float).reset_index(drop=True) for x in (Tmax, Tmin, Ra))
    dT = (Tmax - Tmin).where(Tmax - Tmin > 0)
    Tmean = (Tmax + Tmin) / 2
    p = pd.DataFrame()
    p["M1"]  = 0.16 * np.sqrt(dT) * Ra
    p["M2"]  = 3.6 * (1.29 + 0.3626 * dT)                           # ASSUMPTION A: kWh -> MJ
    p["M3"]  = 0.3124 * dT**0.2942 * Ra
    p["M4"]  = (0.7730 - 0.0296 * dT + 0.0016 * dT**2) * Ra
    p["M5"]  = (0.2063 + 0.1801 * np.log(dT)) * Ra
    p["M6"]  = (0.3040 + 0.1008 * np.sqrt(dT)) * Ra
    p["M7"]  = (0.2889 + 0.1562 * Tmax / Tmin) * Ra
    p["M8"]  = (1.7217 - 1.691 * Tmin / Tmax) * Ra                  # ASSUMPTION B: Theta = Tmin/Tmax
    p["M9"]  = (0.28 * np.log(dT) + 0.15) * Ra
    p["M10"] = -4.46 + 0.477 * Ra - 0.226 * Tmean
    p["M11"] = (0.4610 + 0.0029 * dT) * Ra
    p["M12"] = (0.5290 + 0.0516 * Tmin / Tmax) * Ra
    p["M13"] = (0.206590 + 0.026851 * Tmax - 0.024184 * Tmin) * Ra
    p["M14"] = (0.85235 - 0.00997 * Tmean) * Ra
    p["M15"] = (0.236 + 0.106 * np.sqrt(dT)) * Ra
    p["M16"] = (0.00185 * dT**2 - 0.0433 * dT + 0.4023) * Ra        # ASSUMPTION C: paper form, no sqrt(dT)
    return p
