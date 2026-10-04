"""Project-level data and regenerated-result checks for the dashboard engine."""
from pathlib import Path
import hashlib
import sys

import numpy as np
import pandas as pd

from engine.config import DISTRICTS, LATITUDE, MODELS, PERIODS
from engine.pipeline import prepare_days, evaluate_all_periods, top3
from ui.pages import load_official_results

PROJECT = Path(__file__).resolve().parents[2]
RESULTS = PROJECT / "results" / "final"


def load_station(station):
    raw = pd.read_csv(PROJECT / "data" / "raw_imd" / f"{station.upper()}.csv", dtype=str)
    return pd.DataFrame({
        "Date": pd.to_datetime(dict(year=raw.YEAR.astype(int), month=raw.MN.astype(int), day=raw.DT.astype(int))),
        "Tmax": pd.to_numeric(raw.MAX.str.strip(), errors="coerce"),
        "Tmin": pd.to_numeric(raw.MIN.str.strip(), errors="coerce"),
        "SSH": pd.to_numeric(raw.SSH.str.strip(), errors="coerce"),
    })


def test_fixed_study_design():
    assert DISTRICTS == ["Ahmedabad", "Amreli", "Okha"]
    assert len(MODELS) == 16
    assert PERIODS == ["Annual", "Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]


def test_source_coverage_and_valid_rows():
    expected = {"Ahmedabad": (1985, 2025, 14802), "Amreli": (1985, 2025, 14718), "Okha": (1985, 2025, 14474)}
    for station in DISTRICTS:
        raw = load_station(station)
        days = prepare_days(raw, LATITUDE[station])
        start, end, count = expected[station]
        assert raw.Date.min().year == start and raw.Date.max().year == end
        assert int(days.used.sum()) == count
        assert days.loc[days.used, MODELS].apply(np.isfinite).all().all()
        assert np.isfinite(days.loc[days.used, "Rs_AP"]).all()


def test_notebook_exported_metrics_registry_and_hashes():
    """Validate the notebook's exported source of truth, not the deferred app engine."""
    metrics = pd.read_csv(RESULTS / "all_metrics.csv")
    registry = pd.read_csv(PROJECT / "results" / "model_registry.csv")
    keys = ["station", "period", "model"]
    assert len(metrics) == 3 * 5 * 16
    assert not metrics.duplicated(keys).any()
    assert set(metrics.station) == set(DISTRICTS)
    assert set(metrics.period) == set(PERIODS)
    assert set(metrics.model) == set(MODELS)
    assert set(metrics.status) == {"ok"}
    assert np.isfinite(metrics[["R2", "RMSE", "MAE", "MBE", "GPI", "rank"]].to_numpy()).all()
    assert len(registry) == 16 and set(registry.model) == set(MODELS)
    assert {"model_name", "published_equation", "implemented_equation", "source", "assumption"}.issubset(registry.columns)

    manifest_path = PROJECT / "results" / "validation" / "output_hashes.csv"
    manifest = pd.read_csv(manifest_path).set_index("path")
    target = "results/final/all_metrics.csv"
    actual_hash = hashlib.sha256((PROJECT / target).read_bytes()).hexdigest()
    assert manifest.loc[target, "sha256"] == actual_hash


def test_dashboard_reads_official_notebook_exports_directly():
    metrics, comparison, top, provenance, period_coverage = load_official_results()
    expected_metrics = pd.read_csv(RESULTS / "all_metrics.csv").rename(columns={"station": "district"})
    expected_top = pd.read_csv(RESULTS / "top_3_models.csv").rename(columns={"station": "district"})
    expected_comparison = pd.read_csv(RESULTS / "station_comparison.csv").rename(
        columns={"station": "district", "valid_days": "days used"})
    pd.testing.assert_frame_equal(metrics, expected_metrics, check_dtype=False)
    pd.testing.assert_frame_equal(top, expected_top, check_dtype=False)
    pd.testing.assert_frame_equal(comparison, expected_comparison, check_dtype=False)
    assert set(provenance.district) == set(DISTRICTS)
    assert len(period_coverage) == len(DISTRICTS) * len(PERIODS)
    assert len(metrics) == 240 and len(top) == 45
    assert not (PROJECT / "dashboard" / "data" / "demo").exists()


def test_top3_and_wide_rank_table_have_all_stations_and_periods():
    top = pd.read_csv(RESULTS / "top_3_models.csv")
    assert set(top.station) == set(DISTRICTS)
    assert set(top.period) == set(PERIODS)
    assert top.groupby(["station", "period"]).size().min() >= 3
    ranks = pd.read_csv(RESULTS / "model_ranking.csv")
    assert len(ranks) == len(DISTRICTS) * len(MODELS)
    assert set(ranks.station) == set(DISTRICTS)
    assert not ranks[PERIODS].isna().any().any()


def test_repeated_run_is_rank_reproducible():
    station = "Ahmedabad"
    days = prepare_days(load_station(station), LATITUDE[station])
    first = evaluate_all_periods(days, station).sort_values(["period", "model"]).reset_index(drop=True)
    second = evaluate_all_periods(days, station).sort_values(["period", "model"]).reset_index(drop=True)
    assert first["rank"].equals(second["rank"])
    assert np.allclose(first.GPI, second.GPI, rtol=0, atol=0)
