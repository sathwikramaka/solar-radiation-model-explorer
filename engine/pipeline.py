"""The full method in the notebook's order:
Input -> inclusion rules (QC) -> solar geometry -> A-P reference -> 16 models -> metrics -> GPI -> rank -> Top 3.
"""
import numpy as np
import pandas as pd

from .config import MODELS, PERIODS, SEASON_OF_MONTH, MIN_DAYS
from .solar_geometry import day_length_and_ra, angstrom_prescott
from .models import predict_all
from .metrics import calculate_metrics
from .gpi import calculate_gpi


def prepare_days(df, latitude, sunshine_years=None, first_year=None, last_year=None):
    """Daily table with geometry, A-P reference, M1..M16 and the `used` flag (notebook Cells 4-8).

    df: columns Date (datetime), Tmax, Tmin (degC), SSH (sunshine hours); one row per date.
    sunshine_years: years whose sunshine passed the project's satellite check (demo districts only);
                    None = no year filter (uploaded data, decision D1).
    first_year/last_year: optional period filter (2002-2023 for the demo districts; uploads use all dates, D2).
    Nothing is filled, clipped or changed: days that fail a rule are only flagged `used = False`.
    """
    d = df[["Date", "Tmax", "Tmin", "SSH"]].copy()
    d["Date"] = pd.to_datetime(d["Date"])
    if first_year is not None:
        d = d[d.Date.dt.year >= first_year]
    if last_year is not None:
        d = d[d.Date.dt.year <= last_year]
    d = d.reset_index(drop=True)

    d["Year"] = d.Date.dt.year
    d["Season"] = d.Date.dt.month.map(SEASON_OF_MONTH)
    d["dT"] = d.Tmax - d.Tmin                    # diurnal temperature range
    d["Tmean"] = (d.Tmax + d.Tmin) / 2
    d["temperature_ok"] = d.Tmax.notna() & d.Tmin.notna() & (d.dT > 0)
    d["sunshine_year_ok"] = True if sunshine_years is None else d.Year.isin(sunshine_years)

    d["N"], d["Ra"] = day_length_and_ra(d.Date.dt.dayofyear, latitude)
    d["Rs_AP"] = angstrom_prescott(d.SSH, d.N, d.Ra)
    d[MODELS] = predict_all(d.Tmax, d.Tmin, d.Ra)

    # Final inclusion: valid temperatures, valid A-P reference, accepted sunshine year, all 16 models finite
    d["used"] = d.temperature_ok & d.Rs_AP.notna() & d.sunshine_year_ok & np.isfinite(d[MODELS]).all(axis=1)
    return d


def evaluate_period(days, period, district):
    """Metrics + GPI + rank of the 16 models for one site and one period (notebook Cell 10)."""
    sel = days[days.used] if period == "Annual" else days[days.used & (days.Season == period)]
    if len(sel) < MIN_DAYS:
        return pd.DataFrame({"district": district, "period": period, "model": MODELS, "n": len(sel),
                             "status": "no valid reference data" if len(sel) == 0 else "insufficient days (<30)"})
    rows = [{"district": district, "period": period, "model": m, **calculate_metrics(sel[m], sel.Rs_AP)} for m in MODELS]
    table = calculate_gpi(pd.DataFrame(rows))
    table["status"] = "ok"
    return table


def evaluate_all_periods(days, district):
    """Annual + four seasons, one row per model and period."""
    return pd.concat([evaluate_period(days, p, district) for p in PERIODS], ignore_index=True)


def top3(results):
    """Rank 1-3 of every evaluated period."""
    return results[results["rank"] <= 3].sort_values(["district", "period", "rank"]).reset_index(drop=True)
