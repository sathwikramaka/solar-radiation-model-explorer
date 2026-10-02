"""Fixed settings of the method. Every value here is copied from the final project notebook
(code/solar_radiation_analysis_FINAL.ipynb). Do not change them without group approval.

Unresolved assumptions of the project (README section 7), kept exactly as in the notebook:
  A. M2 is multiplied by 3.6 (paper result read as kWh -> MJ).
  B. M8 uses Theta = Tmin/Tmax (Theta is not defined in the paper).
  C. M16 uses the paper's printed form (no sqrt(dT)).
  D. R2 = 1 - SSE/SST (paper formula); the paper's printed R2 values look like Pearson r2.
  E. MBE enters the GPI with its sign (as in the paper); |MBE| is only a sensitivity test.
"""

MODELS = [f"M{i}" for i in range(1, 17)]

# IMD seasons used in the paper (Karale et al. 2026)
SEASON_OF_MONTH = {1: "Winter", 2: "Winter",
                   3: "Pre-Monsoon", 4: "Pre-Monsoon", 5: "Pre-Monsoon",
                   6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
                   10: "Post-Monsoon", 11: "Post-Monsoon", 12: "Post-Monsoon"}
PERIODS = ["Annual", "Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]

GSC = 0.0820             # solar constant, MJ m-2 min-1 (FAO-56)
A_AP, B_AP = 0.25, 0.50  # Angstrom-Prescott coefficients (paper Eq. 5)
MIN_DAYS = 30            # a district/period needs at least 30 valid days to be evaluated

# ---- Five demonstration districts (used only to reproduce the validated project results) ----
DISTRICTS = ["Surat", "Ahmedabad", "Amreli", "Deesa", "Okha"]
LATITUDE = {"Surat": 21 + 12/60, "Ahmedabad": 23 + 4/60, "Amreli": 21 + 36/60,
            "Deesa": 24 + 12/60, "Okha": 22 + 29/60}   # degrees N, IMD Climatological Normals 1981-2010
FIRST_YEAR, LAST_YEAR = 2002, 2023
# Years whose sunshine record passed the project's satellite cross-check (results/qc_report.csv).
# This check needs NASA POWER data, so it is NOT applied to uploaded files (decision D1).
SUNSHINE_YEARS_USED = {
    "Surat":     [],
    "Ahmedabad": list(range(2002, 2024)),
    "Amreli":    [2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2013, 2014, 2015, 2016, 2017, 2023],
    "Deesa":     [],
    "Okha":      list(range(2002, 2022)),
}
