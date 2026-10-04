"""Upload reading and checking: file types, column detection, invalid values, duplicates, and
that the upload path does not change the data (it reproduces the validated results)."""
import io
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from engine.config import LATITUDE
from engine.pipeline import prepare_days, evaluate_all_periods
from engine.validation import (read_table, detect_columns, ambiguous_columns, build_input, exclusion_reasons,
                               parse_dates)


def _xlsx(df):
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


def _days(n=40, start="2021-01-01"):
    rng = np.random.default_rng(3)
    return pd.DataFrame({"Date": pd.date_range(start, periods=n), "Tmax": 30 + rng.normal(0, 2, n),
                         "Tmin": 15 + rng.normal(0, 2, n), "SSH": rng.uniform(2, 10, n)})


# ---------------------------------------------------------------- reading
def test_read_csv_and_xlsx():
    df = _days()
    assert len(read_table("a.csv", df.to_csv(index=False).encode())["CSV"]) == 40
    assert len(next(iter(read_table("a.xlsx", _xlsx(df)).values()))) == 40


@pytest.mark.parametrize("name,data,text", [
    ("e.csv", b"", "empty"),
    ("h.csv", b"Date,Tmax,Tmin,SSH\n", "no data rows"),
    ("o.xls", b"\xd0\xcf fake", ".xls"),
    ("o.txt", b"abc", "Unsupported"),
    ("bad.xlsx", b"not a zip file", "could not be read"),
])
def test_read_errors(name, data, text):
    with pytest.raises(ValueError, match=text):
        read_table(name, data)


# ---------------------------------------------------------------- detection
def test_detect_imd_and_named_columns():
    assert detect_columns(["YEAR", "MN", "DT", "MAX", "MIN", "SSH"]) == \
        {"Date": None, "Year": "YEAR", "Month": "MN", "Day": "DT", "Tmax": "MAX", "Tmin": "MIN", "SSH": "SSH"}
    found = detect_columns(["Obs Date", "Max Temp (°C)", "Min Temp (°C)", "Bright Sunshine (h)", "Rain"])
    assert (found["Date"], found["Tmax"], found["Tmin"], found["SSH"]) == \
        ("Obs Date", "Max Temp (°C)", "Min Temp (°C)", "Bright Sunshine (h)")


def test_ambiguous_columns_are_not_guessed():
    cols = ["Date", "Tmax", "MAX", "Tmin", "SSH"]               # two exact Tmax candidates
    found = detect_columns(cols)
    assert found["Tmax"] is None and found["Tmin"] == "Tmin" and found["SSH"] == "SSH"
    assert ambiguous_columns(cols) == {"Tmax": ["Tmax", "MAX"]}
    found = detect_columns(["Date", "Max Temp", "Max Temp (station 2)", "Min Temp", "Sunshine"])
    assert found["Tmax"] is None and found["Tmin"] == "Min Temp"  # two keyword candidates


def test_dates_year_first_never_swapped():
    s = parse_dates(pd.Series(["2020-03-04", "04/03/2020", "03/04/2020"]), dayfirst=True)
    assert list(s.dt.strftime("%Y-%m-%d")) == ["2020-03-04", "2020-03-04", "2020-04-03"]


# ---------------------------------------------------------------- checks
MAP = {"Date": "Date", "Tmax": "Tmax", "Tmin": "Tmin", "SSH": "SSH"}


def test_missing_column_is_an_error():
    clean, msgs, _ = build_input(_days().drop(columns="SSH"), {**MAP, "SSH": None})
    assert clean is None and msgs[0][0] == "error" and "SSH" in msgs[0][1]


def test_same_column_twice_is_an_error():
    clean, msgs, _ = build_input(_days(), {**MAP, "Tmin": "Tmax"})
    assert clean is None and "same column" in msgs[0][1]


def test_invalid_values_reported_not_changed():
    df = _days().astype(object)
    df.loc[1, "Tmax"] = "NA"
    df.loc[2, "Date"] = "not a date"
    df.loc[3, "Tmax"] = 70.0
    df = pd.concat([df, df.iloc[[5]]], ignore_index=True)      # duplicate date
    clean, msgs, excluded = build_input(df, MAP)
    text = " ".join(m for _, m in msgs)
    assert "not numbers" in text and "'NA'" in text
    assert "invalid or missing date" in text
    assert "share a date" in text and "outside -10…55" in text
    assert len(excluded) == 3                                   # bad date + both duplicate rows
    assert len(clean) == 38 and clean.Tmax.isna().sum() == 1    # 'NA' -> missing, row kept
    assert (clean.Tmax == 70).sum() == 1                        # implausible temperature kept (flag only)
    original = pd.to_numeric(df.set_index(df.index + 2).Tmax, errors="coerce")
    assert np.allclose(clean.Tmax, original.loc[clean.source_row], equal_nan=True)


def test_method_exclusion_reasons():
    df = _days(40)
    df.loc[0, "Tmin"] = np.nan
    df.loc[1, "Tmin"] = df.loc[1, "Tmax"] + 1
    df.loc[2, "SSH"] = np.nan
    df.loc[3, "SSH"] = 20.0
    df.loc[4, "Tmin"] = 0.0                                     # M7 = Tmax/Tmin -> infinite
    clean, _, _ = build_input(df, MAP)
    days = prepare_days(clean, 23.0)
    assert list(exclusion_reasons(days)[:6]) == ["Tmax or Tmin missing", "Tmax ≤ Tmin (ΔT ≤ 0)", "sunshine missing",
                                                 "sunshine < 0 or > day length N", "a model gives a non-finite value", ""]


def test_year_month_day_columns():
    df = _days()
    ymd = pd.DataFrame({"YEAR": df.Date.dt.year, "MN": df.Date.dt.month, "DT": df.Date.dt.day,
                        "MAX": df.Tmax, "MIN": df.Tmin, "SSH": df.SSH})
    clean, _, _ = build_input(ymd, detect_columns(list(ymd.columns)))
    assert clean.Date.equals(df.Date) and clean.Tmax.equals(df.Tmax)


# ---------------------------------------------------------------- the upload path reproduces validated results
RAW = Path(__file__).resolve().parents[2] / "data" / "raw_imd"


@pytest.mark.skipif(not (RAW / "AHMEDABAD.csv").exists(), reason="retained IMD input is unavailable")
def test_upload_path_reproduces_validated_ahmedabad():
    """Raw IMD file -> Excel bytes -> read/detect/validate -> engine == validated results."""
    raw = pd.read_csv(RAW / "AHMEDABAD.csv")
    sheet = next(iter(read_table("ahmedabad.xlsx", _xlsx(raw)).values()))
    clean, _, excluded = build_input(sheet, detect_columns(list(sheet.columns)))
    assert len(excluded) == 0
    days = prepare_days(clean, LATITUDE["Ahmedabad"])
    ours = evaluate_all_periods(days, "Ahmedabad")
    project = Path(__file__).resolve().parents[2]
    val = pd.read_csv(project / "results" / "final" / "all_metrics.csv").rename(columns={"station": "district"})
    m = val[val.district == "Ahmedabad"].merge(ours, on=["period", "model"])
    assert len(m) == 80
    for col in ["R2", "RMSE", "MAE", "MBE", "GPI", "rank"]:
        assert np.max(np.abs(m[col + "_x"] - m[col + "_y"].astype(float))) < 1e-9, col
