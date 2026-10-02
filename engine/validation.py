"""Reading and checking an uploaded file before it enters the pipeline.

Rules (decisions D1-D5, D9):
  * .xlsx and .csv only (.xls must be re-saved as .xlsx).
  * Values are never changed. Problem rows are excluded and listed with the reason.
  * Duplicate dates: every row of that date is excluded (no row is picked silently).
  * Temperatures outside -10..55 degC are only flagged (kept), as in the project's qc_report.csv.
  * The project's satellite sunshine check cannot be run offline; years with < 200 valid
    sunshine days are only flagged.
Day-level exclusions of the method itself (missing values, dT <= 0, n > N ...) are reported by
`exclusion_reasons` after the pipeline has run.
"""
import io
import re

import numpy as np
import pandas as pd

from .config import MODELS

VARIABLES = ["Date", "Year", "Month", "Day", "Tmax", "Tmin", "SSH"]
ALIASES = {
    "Date":  ["date", "dates", "obsdate", "observationdate", "datetime", "time"],
    "Year":  ["year", "yr", "yyyy", "years"],
    "Month": ["month", "mn", "mon", "mm", "mo"],
    "Day":   ["day", "dt", "dd", "dy", "dayofmonth"],
    "Tmax":  ["tmax", "max", "maxt", "maxtemp", "maxtemperature", "maximumtemperature", "tempmax", "tx", "maximum"],
    "Tmin":  ["tmin", "min", "mint", "mintemp", "mintemperature", "minimumtemperature", "tempmin", "tn", "minimum"],
    "SSH":   ["ssh", "sunshine", "sunshinehours", "sunshineduration", "bss", "brightsunshine",
              "brightsunshinehours", "sunhours", "sun", "n", "sd", "sshr"],
}
TEMP_FLAG_RANGE = (-10, 55)       # degC, flag only (project qc_report.csv)
MIN_SUNSHINE_DAYS_PER_YEAR = 200  # flag only (D1)

TEMPLATE = pd.DataFrame({"Date": ["2020-01-01", "2020-01-02", "2020-01-03"],
                         "Tmax": [28.4, 29.1, 27.6], "Tmin": [12.2, 13.0, 11.8], "SSH": [9.6, 9.2, 8.7]})


def _norm(name):
    name = re.sub(r"\(.*?\)|\[.*?\]", "", str(name).lower())   # drop units such as "(degC)"
    return re.sub(r"[^a-z0-9]", "", name)


def read_table(filename, data):
    """Return {sheet name: DataFrame}. Raises ValueError with a plain-language message."""
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if not data:
        raise ValueError("The file is empty.")
    if ext == "xls":
        raise ValueError("Old Excel format (.xls) is not supported. Open the file in Excel and use "
                         "File → Save As → Excel Workbook (.xlsx).")
    if ext not in ("csv", "xlsx"):
        raise ValueError(f"Unsupported file type '.{ext}'. Upload an .xlsx or .csv file.")
    try:
        if ext == "csv":
            try:
                sheets = {"CSV": pd.read_csv(io.BytesIO(data), encoding="utf-8-sig")}
            except UnicodeDecodeError:
                sheets = {"CSV": pd.read_csv(io.BytesIO(data), encoding="latin-1")}
        else:
            sheets = pd.read_excel(io.BytesIO(data), sheet_name=None, engine="openpyxl")
    except pd.errors.EmptyDataError:
        raise ValueError("The file is empty.")
    except Exception as exc:  # corrupt file, wrong content, ...
        raise ValueError(f"The file could not be read ({type(exc).__name__}). Check that it is a valid .{ext} file.")
    sheets = {name: df.dropna(how="all").dropna(axis=1, how="all") for name, df in sheets.items()}
    sheets = {name: df for name, df in sheets.items() if len(df) and len(df.columns)}
    if not sheets:
        raise ValueError("The file contains no data rows.")
    return sheets


KEYWORDS = {"Date": lambda n: "date" in n,
            "Tmax": lambda n: "max" in n and "min" not in n,
            "Tmin": lambda n: "min" in n and "max" not in n,
            "SSH":  lambda n: "sunshine" in n or "ssh" in n or "bss" in n}


def column_candidates(columns):
    """Columns that could hold each variable: exact name matches first, otherwise keyword matches."""
    normed = {c: _norm(c) for c in columns}
    cands = {}
    for var in VARIABLES:
        exact = [c for c in columns if normed[c] in ALIASES[var]]
        cands[var] = exact or [c for c in columns if var in KEYWORDS and KEYWORDS[var](normed[c])]
    return cands


def detect_columns(columns):
    """Assign a column to a variable only when exactly one column matches it (never a silent guess).

    Returns {variable: column or None}. Use `ambiguous_columns` to tell the user why a variable is unassigned.
    """
    cands = column_candidates(columns)
    found = {var: c[0] if len(c) == 1 else None for var, c in cands.items()}
    used = [c for c in found.values() if c is not None]
    for var, col in found.items():                          # one column cannot serve two variables
        if col is not None and used.count(col) > 1:
            found[var] = None
    if found["Date"] is not None:                           # a full date column wins over Y/M/D
        for var in ("Year", "Month", "Day"):
            found[var] = None
    return found


def ambiguous_columns(columns):
    """{variable: [candidate columns]} for variables with more than one possible column."""
    return {var: c for var, c in column_candidates(columns).items() if len(c) > 1}


def parse_dates(col, dayfirst=True):
    """Text dates -> datetime. Year-first text (2020-03-04, 2020/03/04) is always year-month-day;
    `dayfirst` decides only for day/month text such as 03/04/2020. Unreadable dates become NaT."""
    s = col.astype(str).str.strip()
    year_first = s.str.match(r"^\d{4}[-/.]\d{1,2}[-/.]\d{1,2}")
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    if year_first.any():
        out[year_first] = pd.to_datetime(s[year_first].str.replace(r"[/.]", "-", regex=True),
                                         format="ISO8601", errors="coerce")
    if (~year_first).any():
        out[~year_first] = pd.to_datetime(s[~year_first], dayfirst=dayfirst, format="mixed", errors="coerce")
    return out


def _to_number(series, label, messages):
    """Convert to numbers; text that is not a number becomes missing and is reported."""
    numbers = pd.to_numeric(series, errors="coerce")
    bad = series.notna() & numbers.isna() & (series.astype(str).str.strip() != "")
    if bad.any():
        examples = ", ".join(f"'{v}'" for v in series[bad].astype(str).unique()[:3])
        messages.append(("warning", f"{label}: {int(bad.sum())} value(s) are not numbers (e.g. {examples}); "
                                    "they are treated as missing."))
    return numbers


def build_input(raw, mapping, dayfirst=True):
    """Apply the column mapping and check the file.

    Returns (clean, messages, excluded):
      clean    - DataFrame Date, Tmax, Tmin, SSH, source_row (one row per date, values unchanged) or None on error
      messages - list of (level, text), level in ok / info / warning / error
      excluded - rows removed before the method runs, with the reason
    """
    messages = []
    use_date = mapping.get("Date") is not None
    need = (["Date"] if use_date else ["Year", "Month", "Day"]) + ["Tmax", "Tmin", "SSH"]
    missing = [v for v in need if mapping.get(v) is None]
    if missing:
        hint = "" if use_date else " Provide either one Date column or Year, Month and Day columns."
        return None, [("error", f"Required column(s) not assigned: {', '.join(missing)}.{hint}")], None
    chosen = [mapping[v] for v in need]
    if len(set(chosen)) < len(chosen):
        return None, [("error", "The same column is assigned to two variables. Each variable needs its own column.")], None
    for v in need:
        messages.append(("ok", f"{v} detected → column “{mapping[v]}”"))

    src = raw.reset_index(drop=True)
    if use_date:
        col = src[mapping["Date"]]
        dates = col if pd.api.types.is_datetime64_any_dtype(col) else parse_dates(col, dayfirst)
    else:
        ymd = {k: _to_number(src[mapping[v]], v, messages) for k, v in
               (("year", "Year"), ("month", "Month"), ("day", "Day"))}
        dates = pd.to_datetime(pd.DataFrame(ymd), errors="coerce")

    clean = pd.DataFrame({"Date": dates,
                          "Tmax": _to_number(src[mapping["Tmax"]], "Tmax", messages),
                          "Tmin": _to_number(src[mapping["Tmin"]], "Tmin", messages),
                          "SSH": _to_number(src[mapping["SSH"]], "SSH", messages)})
    clean["source_row"] = src.index + 2        # row number as seen in Excel (row 1 = header)

    reason = pd.Series("", index=clean.index)
    reason[clean.Date.isna()] = "invalid or missing date"
    dup = clean.Date.notna() & clean.Date.duplicated(keep=False)
    reason[dup] = "duplicate date (all rows of this date excluded)"
    excluded = clean[reason != ""].assign(reason=reason[reason != ""])
    n_bad_date = int((reason == "invalid or missing date").sum())
    n_dup_dates = int(clean.Date[dup].nunique())
    clean = clean[reason == ""].sort_values("Date").reset_index(drop=True)

    if n_bad_date:
        messages.append(("warning", f"{n_bad_date} row(s) have an invalid or missing date and are excluded."))
    if n_dup_dates:
        messages.append(("warning", f"{int(dup.sum())} row(s) share a date with another row ({n_dup_dates} date(s)). "
                                    "All rows of those dates are excluded."))
    if len(clean) == 0:
        messages.append(("error", "No rows with a valid, unique date remain. Check the date column and the date format."))
        return None, messages, excluded

    span = pd.date_range(clean.Date.min(), clean.Date.max())
    messages.append(("info", f"Period in file: {clean.Date.min():%d %b %Y} – {clean.Date.max():%d %b %Y} "
                             f"({len(clean):,} days with a valid date)."))
    if len(span) > len(clean):
        messages.append(("info", f"{len(span) - len(clean):,} calendar day(s) inside this period have no row."))
    for v in ("Tmax", "Tmin", "SSH"):
        n = int(clean[v].isna().sum())
        if n:
            messages.append(("info", f"{v} is missing on {n:,} day(s); those days cannot be evaluated."))
    lo, hi = TEMP_FLAG_RANGE
    odd = int(((clean.Tmax < lo) | (clean.Tmax > hi) | (clean.Tmin < lo) | (clean.Tmin > hi)).sum())
    if odd:
        messages.append(("warning", f"{odd} day(s) have a temperature outside {lo}…{hi} °C. "
                                    "They are kept (flag only) — please check them."))
    if (clean.SSH > 24).any():
        messages.append(("warning", "Some sunshine values exceed 24 h. Is the column in hours? "
                                    "Values above the day length N are excluded by the method."))
    per_year = clean.groupby(clean.Date.dt.year).SSH.count()
    weak = per_year[per_year < MIN_SUNSHINE_DAYS_PER_YEAR]
    if len(weak):
        messages.append(("warning", "Years with fewer than 200 sunshine values: "
                                    + ", ".join(f"{y} ({n})" for y, n in weak.items())
                                    + ". The project's satellite sunshine check is not applied to uploads; "
                                      "treat results from these years with care (partial years at the start/end are normal)."))
    return clean[["Date", "Tmax", "Tmin", "SSH", "source_row"]], messages, excluded


def exclusion_reasons(days):
    """Why each day is not used by the method (first failing rule); '' for used days."""
    r = pd.Series("", index=days.index, dtype=object)
    rules = [
        (days.Tmax.isna() | days.Tmin.isna(), "Tmax or Tmin missing"),
        (days.dT <= 0, "Tmax ≤ Tmin (ΔT ≤ 0)"),
        (days.SSH.isna(), "sunshine missing"),
        ((days.SSH < 0) | (days.SSH > days.N), "sunshine < 0 or > day length N"),
        (~days.sunshine_year_ok, "sunshine year rejected"),
        (~np.isfinite(days[MODELS]).all(axis=1), "a model gives a non-finite value"),
    ]
    for mask, text in rules:
        r[(r == "") & mask & ~days.used] = text
    return r
