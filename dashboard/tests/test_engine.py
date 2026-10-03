"""Unit tests of the calculation steps on small, hand-checkable inputs (no private data needed)."""
import numpy as np
import pandas as pd
import pytest

from engine.config import MODELS, SEASON_OF_MONTH
from engine.solar_geometry import day_length_and_ra, angstrom_prescott
from engine.models import predict_all, MODEL_INFO
from engine.metrics import calculate_metrics
from engine.gpi import calculate_gpi
from engine.pipeline import prepare_days, evaluate_period


def test_primary_study_solar_geometry():
    # Study geometry uses dr = 1 + 0.003 cos(2 pi J/365): 20 deg S, J = 246.
    N, Ra = day_length_and_ra(246, -20)
    assert round(float(Ra), 1) == 32.6
    assert round(float(N), 1) == 11.7


def test_angstrom_prescott_rule():
    N, Ra = np.array([12.0] * 4), np.array([30.0] * 4)
    ap = angstrom_prescott([6.0, 0.0, 13.0, np.nan], N, Ra)
    assert ap[0] == pytest.approx((0.25 + 0.5 * 0.5) * 30)   # 15
    assert ap[1] == pytest.approx(0.25 * 30)                  # 0 h is a real overcast day
    assert np.isnan(ap[2]) and np.isnan(ap[3])                # n > N and missing: excluded, not clipped


def test_models_by_hand():
    p = predict_all([34.0], [18.0], [30.0]).iloc[0]          # dT = 16, Tmean = 26
    assert list(p.index) == MODELS == list(MODEL_INFO)
    assert p.M1 == pytest.approx(0.16 * 4 * 30)
    assert p.M2 == pytest.approx(3.6 * (1.29 + 0.3626 * 16))
    assert p.M10 == pytest.approx(-4.46 + 0.477 * 30 - 0.226 * 26)
    assert p.M15 == pytest.approx((0.236 + 0.106 * 4) * 30)
    assert p.M16 == pytest.approx((0.00185 * 256 - 0.0433 * 16 + 0.4023) * 30)
    assert predict_all([20.0], [20.0], [30.0]).iloc[0][["M1", "M5"]].isna().all()   # dT <= 0 undefined


def test_metrics_by_hand():
    m = calculate_metrics([2, 4, 6], [1, 4, 7])               # errors 1, 0, -1
    assert m["n"] == 3 and m["MBE"] == 0
    assert m["MAE"] == pytest.approx(2 / 3)
    assert m["RMSE"] == pytest.approx(np.sqrt(2 / 3))
    assert m["R2"] == pytest.approx(1 - 2 / 18)               # SST = 9 + 0 + 9
    assert calculate_metrics([10, 10], [1, 3])["R2"] < 0      # not clipped


def test_gpi_by_hand():
    t = pd.DataFrame({"model": ["A", "B", "C"], "R2": [0.9, 0.5, 0.1], "RMSE": [1, 2, 3], "MAE": [1, 2, 3], "MBE": [0, 1, 2]})
    g = calculate_gpi(t).set_index("model")
    # scaled R2 = [1, .5, 0], errors = [0, .5, 1], medians .5 -> A: +.5 + 3*.5 = 2, B: 0, C: -2
    assert g.GPI.to_dict() == pytest.approx({"A": 2.0, "B": 0.0, "C": -2.0})
    assert g["rank"].to_dict() == {"A": 1, "B": 2, "C": 3}


def test_gpi_ties_share_rank():
    t = pd.DataFrame({"model": ["A", "B", "C"], "R2": [0.9, 0.9, 0.1], "RMSE": [1, 1, 3], "MAE": [1, 1, 3], "MBE": [0, 0, 2]})
    assert calculate_gpi(t).set_index("model")["rank"].to_dict() == {"A": 1, "B": 1, "C": 3}


def test_constant_indicator_has_zero_contribution():
    t = pd.DataFrame({"model": ["A", "B", "C"], "R2": [0.5, 0.5, 0.5],
                      "RMSE": [2.0, 2.0, 2.0], "MAE": [1.0, 1.0, 1.0], "MBE": [-1.0, 0.0, 1.0]})
    g = calculate_gpi(t)
    assert np.isfinite(g.GPI).all()
    assert g.GPI.to_list() == pytest.approx([0.5, 0.0, -0.5])


def test_seasons():
    assert [SEASON_OF_MONTH[m] for m in (1, 2, 3, 5, 6, 9, 10, 12)] == \
        ["Winter", "Winter", "Pre-Monsoon", "Pre-Monsoon", "Monsoon", "Monsoon", "Post-Monsoon", "Post-Monsoon"]


def _synthetic(days=61):   # 2020-01-01 .. 2020-03-01 (leap year): 60 winter days + 1 pre-monsoon day
    dates = pd.date_range("2020-01-01", periods=days)
    rng = np.random.default_rng(0)
    return pd.DataFrame({"Date": dates, "Tmax": 30 + rng.normal(0, 2, days), "Tmin": 15 + rng.normal(0, 2, days),
                         "SSH": rng.uniform(2, 10, days)})


def test_inclusion_rules_and_min_days():
    df = _synthetic()
    df.loc[0, "Tmax"] = np.nan          # missing temperature
    df.loc[1, "Tmin"] = df.loc[1, "Tmax"]  # dT = 0
    df.loc[2, "SSH"] = 15.0             # n > N
    d = prepare_days(df, 22.0)
    assert not d.used[:3].any() and d.used[3:].all()
    assert d[["Tmax", "Tmin", "SSH"]].equals(df[["Tmax", "Tmin", "SSH"]])     # inputs untouched
    assert (evaluate_period(d, "Annual", "X").status == "ok").all()          # 58 days
    assert (evaluate_period(d, "Monsoon", "X").status == "no valid reference data").all()
    assert (evaluate_period(d, "Pre-Monsoon", "X").status == "insufficient days (<30)").all()  # 1 day in March
