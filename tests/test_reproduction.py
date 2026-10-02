"""The engine must reproduce the validated project results (results/final of the original project).

Needs the raw IMD files in data/private/raw_imd/ (not published, decision D7); skipped if they are absent.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from engine.config import DISTRICTS, LATITUDE, SUNSHINE_YEARS_USED, FIRST_YEAR, LAST_YEAR, MODELS, PERIODS
from engine.pipeline import prepare_days, evaluate_all_periods, top3

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "private" / "raw_imd"
DEMO = ROOT / "data" / "demo"
TOL = 1e-9

pytestmark = pytest.mark.skipif(not RAW.exists(), reason="raw IMD files not available (private data)")


def load_imd(district):
    """Same parsing as notebook Cell 3: columns YEAR, MN, DT, MAX, MIN, SSH; blank = missing."""
    raw = pd.read_csv(RAW / f"{district.upper()}.csv", dtype=str)
    return pd.DataFrame({
        "Date": pd.to_datetime(dict(year=raw["YEAR"].astype(int), month=raw["MN"].astype(int), day=raw["DT"].astype(int))),
        "Tmax": pd.to_numeric(raw["MAX"].str.strip(), errors="coerce"),
        "Tmin": pd.to_numeric(raw["MIN"].str.strip(), errors="coerce"),
        "SSH": pd.to_numeric(raw["SSH"].str.strip(), errors="coerce"),
    })


@pytest.fixture(scope="module")
def engine_output():
    days, results = {}, []
    for d in DISTRICTS:
        days[d] = prepare_days(load_imd(d), LATITUDE[d], SUNSHINE_YEARS_USED[d], FIRST_YEAR, LAST_YEAR)
        results.append(evaluate_all_periods(days[d], d))
    return days, pd.concat(results, ignore_index=True)


def test_days_used_match_readme(engine_output):
    days, _ = engine_output
    assert {d: int(days[d].used.sum()) for d in DISTRICTS} == \
        {"Surat": 0, "Ahmedabad": 8013, "Amreli": 5437, "Deesa": 0, "Okha": 7040}


def test_metrics_gpi_rank_match_validated_results(engine_output):
    _, ours = engine_output
    validated = pd.concat([pd.read_csv(DEMO / "annual_gpi.csv"), pd.read_csv(DEMO / "seasonal_gpi.csv")])
    assert len(validated) == len(ours) == len(DISTRICTS) * len(PERIODS) * len(MODELS)
    m = validated.merge(ours, on=["district", "period", "model"], suffixes=("_v", "_e"), validate="one_to_one")
    assert (m.status_v == m.status_e).all()
    assert (m.n_v == m.n_e).all()
    for col in ["R2", "RMSE", "MAE", "MBE", "GPI", "y_R2", "y_RMSE", "y_MAE", "y_MBE",
                "median_y_R2", "median_y_RMSE", "median_y_MAE", "median_y_MBE", "rank"]:
        v, e = m[col + "_v"].astype(float), m[col + "_e"].astype(float)
        assert (v.isna() == e.isna()).all(), col
        assert np.nanmax(np.abs(v - e)) < TOL, col


def test_top3_matches_validated_results(engine_output):
    _, ours = engine_output
    validated = pd.read_csv(DEMO / "top_3_models.csv")
    ours = top3(ours)
    key = ["district", "period", "rank", "model"]
    assert sorted(map(tuple, validated[key].astype(str).values)) == \
        sorted(map(tuple, ours[key].astype({"rank": float}).astype(str).values))


def test_ranking_table_matches(engine_output):
    _, ours = engine_output
    validated = pd.read_csv(DEMO / "model_ranking.csv").set_index(["district", "model"])
    pivot = ours.pivot_table(index=["district", "model"], columns="period", values="rank").astype(float)
    for (d, mdl), row in validated.iterrows():
        for p in PERIODS:
            v = row[p]
            e = pivot[p].get((d, mdl), np.nan) if p in pivot else np.nan
            assert (np.isnan(v) and np.isnan(e)) or v == e, (d, mdl, p)


@pytest.mark.skipif(not (ROOT / "data/private/daily_predictions.csv").exists(), reason="daily file is private")
def test_daily_values_match(engine_output):
    days, _ = engine_output
    validated = pd.read_csv(ROOT / "data/private/daily_predictions.csv", parse_dates=["Date"])
    ours = pd.concat([days[d].assign(district=d) for d in DISTRICTS], ignore_index=True)
    m = validated.merge(ours, on=["district", "Date"], suffixes=("_v", "_e"), validate="one_to_one")
    assert len(m) == len(validated) == len(ours)
    assert (m.Season_v == m.Season_e).all()
    assert (m.used_v == m.used_e).all()
    for col in ["Tmax", "Tmin", "dT", "SSH", "N", "Ra", "Rs_AP"] + MODELS:
        v, e = m[col + "_v"].astype(float), m[col + "_e"].astype(float)
        assert (v.isna() == e.isna()).all(), col
        assert np.nanmax(np.abs(v - e)) < TOL, col
