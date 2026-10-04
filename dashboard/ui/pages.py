"""The four pages: official notebook results, exploratory upload analysis, and methodology."""
import hashlib
import io
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from engine.config import (DISTRICTS, LATITUDE, MODELS, PERIODS, MIN_DAYS, A_AP, B_AP)
from engine.models import MODEL_INFO
from engine.pipeline import prepare_days, evaluate_all_periods, top3
from engine.validation import (read_table, detect_columns, ambiguous_columns, build_input,
                               exclusion_reasons, TEMPLATE, ALIASES)
from ui import components as C

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = ROOT.parent
FINAL = PROJECT_ROOT / "results" / "final"
QC = PROJECT_ROOT / "results" / "qc"
PRIVATE_DAILY = FINAL / "daily_predictions.csv"
NAV = {}   # page objects, filled by app.py (used for in-page links)

DISTRICT_NOTE = {station: "station-specific valid daily records, 1985–2025" for station in DISTRICTS}
VAR_LABEL = {"Date": "Date", "Year": "Year", "Month": "Month", "Day": "Day", "Tmax": "maximum temperature (Tmax)",
             "Tmin": "minimum temperature (Tmin)", "SSH": "sunshine duration (SSH)"}
METHOD_STEPS = [("dataset", "Input", "Tmax, Tmin, sunshine, latitude"), ("fact_check", "QC", "inclusion rules"),
                ("public", "Solar geometry", "Ra and day length N"), ("wb_sunny", "A–P reference", "Rs from sunshine"),
                ("model_training", "16 models", "Rs from temperature"), ("analytics", "Metrics", "RMSE · MAE · MBE · R²"),
                ("emoji_events", "GPI", "one combined score"), ("leaderboard", "Ranking", "Top 3 per period")]


# ================================================================= data
@st.cache_data(show_spinner=False)
def load_official_results():
    """Load the notebook's exported results; this page does not recalculate official rankings."""
    required = [FINAL / name for name in ("all_metrics.csv", "top_3_models.csv", "station_comparison.csv",
                                          "station_period_summary.csv")]
    required += [QC / "data_provenance.csv"]
    missing = [path for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError("Notebook result export(s) missing: " + ", ".join(str(path) for path in missing))

    results = pd.read_csv(FINAL / "all_metrics.csv")
    top3_results = pd.read_csv(FINAL / "top_3_models.csv")
    comparison = pd.read_csv(FINAL / "station_comparison.csv")
    period_coverage = pd.read_csv(FINAL / "station_period_summary.csv")
    coverage = pd.read_csv(QC / "data_provenance.csv")

    expected_stations = set(DISTRICTS)
    expected_periods = set(PERIODS)
    expected_models = set(MODELS)
    if (len(results) != 240 or results[["station", "period", "model"]].duplicated().any()
            or set(results.station) != expected_stations or set(results.period) != expected_periods
            or set(results.model) != expected_models or not (results.status == "ok").all()):
        raise ValueError("Notebook all_metrics.csv does not match the validated 3 × 5 × 16 study design.")
    if set(top3_results.station) != expected_stations or set(top3_results.period) != expected_periods:
        raise ValueError("Notebook top_3_models.csv does not match the validated study stations and periods.")
    if len(comparison) != 3 or set(comparison.station) != expected_stations:
        raise ValueError("Notebook station_comparison.csv does not contain exactly the three study stations.")
    if len(period_coverage) != 15 or set(period_coverage.station) != expected_stations:
        raise ValueError("Notebook station_period_summary.csv does not contain all 15 station-periods.")
    if set(coverage.station) != expected_stations:
        raise ValueError("Notebook data_provenance.csv does not match the three study stations.")

    return (results.rename(columns={"station": "district"}),
            comparison.rename(columns={"station": "district", "valid_days": "days used"}),
            top3_results.rename(columns={"station": "district"}),
            coverage.rename(columns={"station": "district"}), period_coverage)


@st.cache_data(show_spinner=False)
def load_official_daily():
    """Load the optional local daily export; it is excluded from public Git because it contains raw observations."""
    if not PRIVATE_DAILY.exists():
        return {}
    d = pd.read_csv(PRIVATE_DAILY, parse_dates=["Date"])
    d = d.rename(columns={"station": "district"})
    return {k: g.reset_index(drop=True) for k, g in d.groupby("district")}


@st.cache_data(show_spinner=False, max_entries=8)
def _prepare(clean, latitude):
    """Stage 1 — solar geometry, A-P reference, 16 model estimates, inclusion rules (engine.pipeline.prepare_days)."""
    days = prepare_days(clean, latitude)
    days["source_row"] = clean.source_row.to_numpy()
    days["exclusion_reason"] = exclusion_reasons(days)
    return days


@st.cache_data(show_spinner=False, max_entries=8)
def _evaluate(days, site):
    """Stage 2 — metrics, GPI and ranking for all five periods."""
    return evaluate_all_periods(days, site)


def run_analysis(clean, latitude, site):
    """Uploaded data through the same row-level method, using all supplied dates."""
    days = _prepare(clean, latitude)
    return days, _evaluate(days, site)


def ranked_districts(results):
    ok = results[(results.period == "Annual") & (results.status == "ok")].district.unique()
    return [d for d in DISTRICTS if d in ok]


def winner_matrix(top3_results):
    """Station × period Top 3 table, read directly from the notebook export."""
    head = "".join(f'<th>{C.icon(C.PERIOD_ICON[p])}{p}</th>' for p in PERIODS)
    rows = ""
    for d in DISTRICTS:
        cells = ""
        for p in PERIODS:
            t = top3_results[(top3_results.district == d) & (top3_results.period == p)].sort_values("rank")
            cells += ("<td>" + " · ".join(f'<span class="m1">{m}</span>' if i == 0 else m for i, m in enumerate(t.model))
                      + "</td>") if len(t) else '<td class="na">reference unavailable</td>'
        rows += f'<tr><td class="d">{d}</td>{cells}</tr>'
    C.html(f'<div class="matrix-wrap"><table class="matrix"><thead><tr><th>Station</th>{head}</tr></thead>'
           f'<tbody>{rows}</tbody></table></div>')


# ================================================================= Overview
def overview():
    results, comparison, top3_results, coverage, _ = load_official_results()
    ranked = ranked_districts(results)
    C.hero("MSc Agriculture Analytics · Gujarat, India", "Solar Radiation<br><span>Model Explorer</span>",
           "Comparative analysis of 16 solar-radiation estimation models across seasons and locations — "
           "each scored against the Ångström–Prescott reference and ranked with the Global Performance Indicator.",
            [("location_on", "Gujarat, India"), ("sensors", "3 IMD stations"), ("calendar_month", "1985–2025"),
            ("model_training", "16 models"), ("date_range", "5 periods")])
    c1, c2, c3, _ = st.columns([1, 1, 1, 0.9])
    with c1.container(key="cta_primary"):
        st.page_link(NAV["explorer"], label="Explore the models", icon=":material/insights:")
    c2.page_link(NAV["upload"], label="Analyze your own data", icon=":material/upload_file:")
    c3.page_link(NAV["method"], label="How it works", icon=":material/menu_book:")

    t3 = top3_results[top3_results.status == "ok"]
    counts = t3.model.value_counts()
    leaders = list(counts[counts == counts.max()].index)
    cells = t3.groupby(["district", "period"]).ngroups
    C.kpis([("Stations analysed", f"{len(DISTRICTS)}",
             f"{len(ranked)} ranked · {len(DISTRICTS) - len(ranked)} without valid reference", "location_on", False),
            ("Models evaluated", f"{len(MODELS)}", "published coefficients, none calibrated", "model_training", False),
            ("Periods", f"{len(PERIODS)}", "Annual + 4 IMD seasons", "date_range", False),
            ("Source coverage", "1985–2025", "station-specific valid daily coverage", "calendar_month", False),
            ("Days evaluated", f"{int(comparison['days used'].sum()):,}", "station-days in the ranking",
             "event_available", False),
            ("Most often in Top 3", ", ".join(leaders), f"in {counts.max()} of {cells} ranked station-periods",
             "emoji_events", True)], cols=3)

    C.section("bar_chart", "Annual model comparison",
              f"Annual GPI of all 16 models in the {len(ranked)} ranked stations · hover a dot for its rank and errors")
    C.chart(C.annual_gpi_dots(results, ranked), "ov_annual")

    C.section("date_range", "Seasonal comparison", "Top 3 models in every station and period · highlighted = rank 1")
    winner_matrix(top3_results)

    C.section("military_tech", "Top 3 models", "Pick a station and a period", tone="sun")
    a, b = st.columns([1, 1.6])
    with a:
        d = st.segmented_control("Station", ranked, default=ranked[0], key="ov_d",
                                 format_func=lambda x: f":material/location_on: {x}") or ranked[0]
    with b:
        p = C.period_picker("ov_p")
    t = top3_results[(top3_results.district == d) & (top3_results.period == p)]
    if len(t):
        C.podium(t.sort_values("rank"), f"{d} · {p}")
    else:
        C.unavailable(C.STATUS_TEXT["no valid reference data"])

    C.section("map", "Study stations", "IMD daily records, 1985–2025")
    cards = ""
    coverage_by_station = coverage.set_index("district")
    for dist in DISTRICTS:
        row = comparison[comparison.district == dist].iloc[0]
        span = coverage_by_station.loc[dist]
        ok = row["days used"] > 0
        chip = (f'<span class="chip ok">{C.icon("check_circle")}Ranked</span>' if ok else
                f'<span class="chip na">{C.icon("cloud_off")}Reference unavailable</span>')
        cards += (f'<div class="district"><div class="name">{C.icon("location_on")}{dist}</div>{chip}'
                  f'<div class="meta">{LATITUDE[dist]:.2f}° N · {int(row["days used"]):,} valid days<br>'
                  f'{span.usable_first_date} – {span.usable_last_date}<br>{DISTRICT_NOTE[dist]}'
                  f'<br>Annual Top 3: <b>{row["Top 3 Annual"] if ok else "—"}</b></div></div>')
    C.html(f'<div class="district-grid">{cards}</div>')

    C.section("menu_book", "Method at a glance")
    C.flow(METHOD_STEPS)
    C.note("<b>Read the rankings with their assumptions.</b> The reference is radiation estimated from sunshine "
           "hours, not measured radiation. M2 units and M8 Θ are undefined in the supplied paper, and its R² and signed-MBE "
           "directions need interpretation. See Methodology.")
    C.footer()


# ================================================================= Model Explorer
def explorer():
    results, _, top3_results, _, _ = load_official_results()
    daily = load_official_daily()
    C.page_header("insights", "Validated project results", "Model Explorer",
                  "The 240 validated station–period–model rows exported by the analysis notebook. "
                  "Choose a station, a period and a metric.")
    with st.container(key="ex_filters"):
        c1, c2 = st.columns([1.1, 1])
        with c1:
            district = st.segmented_control("Station", DISTRICTS, default="Ahmedabad", key="ex_d",
                                            format_func=lambda x: f":material/location_on: {x}") or "Ahmedabad"
        with c2:
            metric = C.metric_picker("ex_m")
        period = C.period_picker("ex_p")

    C.section(C.PERIOD_ICON[period], f"{district} · {period}", f"{C.PERIOD_MONTHS[period]} · {LATITUDE[district]:.2f}° N")
    C.results_view(results[results.district == district], period, metric, key="ex", context=f"{district} · {period}",
                   days=daily.get(district), top3_rows=top3_results)

    C.section("compare_arrows", "Station comparison",
              f"{C.label(metric)} of every model at each station · {period} · {C.METRIC_INFO[metric][1]} · "
              "n/a = reference unavailable")
    sel = results[results.period == period]
    pivot = sel.pivot_table(index="model", columns="district", values=metric, dropna=False) \
        .reindex(index=MODELS, columns=DISTRICTS)
    C.chart(C.metric_heatmap(pivot, metric), "ex_cross")
    C.section("table_chart", "Top 3 in every station and period", "highlighted = rank 1")
    winner_matrix(top3_results)

    with st.expander(":material/download: Download the validated results (CSV)"):
        exports = [("All 240 results", FINAL / "all_metrics.csv"),
                   ("Annual results", FINAL / "annual_gpi.csv"),
                   ("Seasonal results", FINAL / "seasonal_gpi.csv"),
                   ("Top 3 models", FINAL / "top_3_models.csv"),
                   ("Model ranks", FINAL / "model_ranking.csv"),
                   ("Station coverage", FINAL / "station_period_summary.csv"),
                   ("Station comparison", FINAL / "station_comparison.csv")]
        for start in range(0, len(exports), 4):
            cols = st.columns(min(4, len(exports) - start))
            for col, (label, path) in zip(cols, exports[start:start + 4]):
                col.download_button(label, path.read_bytes(), path.name, "text/csv",
                                    key=f"dl_{path.stem}", width="stretch")
    C.footer()


# ================================================================= Upload & Analyze
STEPS = ["Upload", "Validate", "Location", "Calculate", "Results"]


def _template_bytes(kind):
    if kind == "csv":
        return TEMPLATE.to_csv(index=False).encode()
    buf = io.BytesIO()
    TEMPLATE.to_excel(buf, index=False)
    return buf.getvalue()


def ranking(results):
    return results.pivot_table(index="model", columns="period", values="rank", dropna=False) \
        .reindex(index=MODELS, columns=PERIODS)


@st.cache_data(show_spinner="Preparing downloads …", max_entries=4)
def _downloads(signature, _days, _results, _excluded, messages, site, latitude):
    """All download files, built once per analysis run (`signature`); arguments with _ are not hashed."""
    daily = _days.drop(columns=["Year", "Tmean", "temperature_ok"], errors="ignore")
    return {"xlsx": _workbook(_days, _results, _excluded, messages, site, latitude),
            "metrics": _results.to_csv(index=False).encode(),
            "ranking": ranking(_results).to_csv().encode(),
            "top3": top3(_results).to_csv(index=False).encode(),
            "daily": daily.to_csv(index=False).encode()}


def _workbook(days, results, excluded, messages, site, latitude):
    gpi_cols = ["district", "period", "rank", "model", "GPI", "y_R2", "y_RMSE", "y_MAE", "y_MBE",
                "median_y_R2", "median_y_RMSE", "median_y_MAE", "median_y_MBE", "R2", "RMSE", "MAE", "MBE", "n", "status"]
    daily_cols = ["source_row", "Date", "Season", "Tmax", "Tmin", "dT", "SSH", "N", "Ra", "Rs_AP", "used",
                  "exclusion_reason"] + MODELS
    about = pd.DataFrame({"item": ["Station", "Latitude (deg)", "Method", "Reference",
                                    "Period", "Minimum days per period"],
                          "value": [site, latitude, "Karale et al. (2026); 16 models, RMSE/MAE/MBE/R2, GPI",
                                     f"Angstrom-Prescott, a = {A_AP}, b = {B_AP}",
                                    f"{days.Date.min():%Y-%m-%d} to {days.Date.max():%Y-%m-%d}", MIN_DAYS]})
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        about.to_excel(w, sheet_name="About", index=False)
        results.reindex(columns=["district", "period", "model", "status", "n", "R2", "RMSE", "MAE", "MBE"]) \
            .to_excel(w, sheet_name="Metrics", index=False)
        results.reindex(columns=gpi_cols).to_excel(w, sheet_name="GPI", index=False)
        ranking(results).to_excel(w, sheet_name="Ranking")
        top3(results)[["period", "rank", "model", "GPI", "R2", "RMSE", "MAE", "MBE", "n"]] \
            .to_excel(w, sheet_name="Top 3", index=False)
        days[daily_cols].to_excel(w, sheet_name="Daily predictions", index=False)
        excluded.to_excel(w, sheet_name="Rows excluded", index=False)
        pd.DataFrame(messages, columns=["level", "message"]).to_excel(w, sheet_name="Validation", index=False)
    return buf.getvalue()


def _stepper(slot, current):
    with slot.container():
        C.stepper(STEPS, current)


READ_ERROR_TITLE = [("empty", "This file is empty"), ("no data rows", "No data rows found"),
                    (".xls", "Old Excel format"), ("Unsupported", "Unsupported file type"),
                    ("could not be read", "The file could not be read")]


def _names(var):
    return ", ".join(f"<code>{a}</code>" for a in ALIASES[var][:4])


def _upload_intro():
    specs = [("event", "Date", "calendar date, e.g. 2020-01-31 or 31/01/2020 — or Year, Month, Day columns"),
             ("thermostat", "Tmax", "daily maximum air temperature, °C"),
             ("device_thermostat", "Tmin", "daily minimum air temperature, °C"),
             ("wb_sunny", "SSH", "bright sunshine duration, hours")]
    cols = "".join(f'<div class="colspec"><div class="k">{C.icon(i)}{k}</div><div class="u">{escape(u)}</div></div>'
                   for i, k, u in specs)
    C.html(f'<div class="card" style="margin-bottom:.9rem"><div class="dropinfo"><div class="ibadge">{C.icon("cloud_upload")}</div><div>'
           f'<div class="h">Upload a daily station dataset</div>'
           f'<div class="b">One row per day. Column names are detected automatically when they are unambiguous — '
           f'otherwise you choose. Blank cells count as missing; leave gaps blank, do not fill them.</div>'
           f'<div class="chips" style="margin-top:.7rem">'
           f'<span class="chip">{C.icon("table_view")}.xlsx</span><span class="chip">{C.icon("csv")}.csv</span>'
           f'<span class="chip">{C.icon("database")}up to 25 MB</span>'
           f'<span class="chip">{C.icon("lock")}processed in memory, not stored</span></div>'
           f'<div class="cols">{cols}</div></div></div></div>')


def upload():
    C.page_header("upload_file", "Run the method on your data", "Upload & Analyze",
                  "Exploratory analysis for a file you provide. It applies the finalized model definitions and method "
                  "where applicable, but these calculations do not change or replace the official notebook exports.")
    C.note("<b>Separate from the official study.</b> The official Ahmedabad, Amreli and Okha results below the "
           "Model Explorer are read from the validated notebook exports. This page analyzes only your uploaded file.", "info")
    step_slot = st.empty()
    _upload_intro()
    t1, t2, _ = st.columns([1, 1, 2.2])
    t1.download_button("Template (.xlsx)", _template_bytes("xlsx"), "solar_template.xlsx", width="stretch",
                       icon=":material/table_view:")
    t2.download_button("Template (.csv)", _template_bytes("csv"), "solar_template.csv", "text/csv", width="stretch",
                       icon=":material/description:")

    file = st.file_uploader("Upload an Excel (.xlsx) or CSV file", type=["xlsx", "csv", "xls"])
    if file is None:
        _stepper(step_slot, 0)
        C.state("empty", "upload_file", "No dataset uploaded yet",
                "Drop an <b>.xlsx</b> or <b>.csv</b> file above. Not sure about the layout? Download a template — "
                "its rows are illustrative only.")
        C.footer()
        return
    data = file.getvalue()
    try:
        sheets = read_table(file.name, data)
    except ValueError as exc:
        title = next((t for k, t in READ_ERROR_TITLE if k in str(exc)), "This file can't be read")
        C.state("error", "error", title, f"{escape(str(exc))}<ul><li>Accepted formats: <b>.xlsx</b> and <b>.csv</b>.</li>"
                "<li>The first row must hold column names; each further row is one day.</li></ul>")
        _stepper(step_slot, 0)
        return
    sheet = st.selectbox("Sheet", list(sheets), key="up_sheet") if len(sheets) > 1 else next(iter(sheets))
    raw = sheets[sheet]

    # ---------------------------------------------------------------- Validate & map
    C.section("fact_check", "1 · Check the columns",
              f"{len(raw):,} rows × {len(raw.columns)} columns read from “{escape(file.name)}”")
    st.dataframe(raw.head(6), hide_index=True, width="stretch")
    cols = [None] + list(raw.columns)
    found = detect_columns(list(raw.columns))
    ambiguous = {v: c for v, c in ambiguous_columns(list(raw.columns)).items()
                 if not (found["Date"] is not None and v in ("Year", "Month", "Day"))}
    for v, c in ambiguous.items():
        C.state("warn", "help", f"Your file was uploaded, but we couldn't identify a unique {VAR_LABEL[v]} column",
                f"{len(c)} columns could be {v}: " + ", ".join(f"<code>{escape(str(x))}</code>" for x in c)
                + ". Nothing was guessed — please choose the right one below.")
    mode = st.radio("Date given as", ["One date column", "Year, Month and Day columns"], horizontal=True,
                    index=0 if found["Date"] is not None or found["Year"] is None else 1, key="up_mode")

    def pick(var, slot):
        return slot.selectbox(var, cols, index=cols.index(found[var]) if found[var] in cols else 0,
                              format_func=lambda c: "— not assigned —" if c is None else str(c), key=f"up_{var}")

    mapping = {}
    if mode == "One date column":
        a, b, c, d = st.columns(4)
        mapping["Date"] = pick("Date", a)
    else:
        a, b, c, d, e, f = st.columns(6)
        mapping.update(Year=pick("Year", a), Month=pick("Month", b), Day=pick("Day", c))
        b, c, d = d, e, f
    mapping.update(Tmax=pick("Tmax", b), Tmin=pick("Tmin", c), SSH=pick("SSH", d))

    dayfirst = True
    if mode == "One date column" and mapping["Date"] is not None and \
            not pd.api.types.is_datetime64_any_dtype(raw[mapping["Date"]]):
        order = st.radio("Date order for dates like 03/04/2020", ["Day first (dd/mm/yyyy)", "Month first (mm/dd/yyyy)"],
                         horizontal=True, key="up_order",
                         help="Dates written year-first (2020-04-03) are always read as year-month-day.")
        dayfirst = order.startswith("Day")

    clean, messages, excluded = build_input(raw, mapping, dayfirst)
    if clean is None:
        need = (["Date"] if mode == "One date column" else ["Year", "Month", "Day"]) + ["Tmax", "Tmin", "SSH"]
        missing = [v for v in need if mapping.get(v) is None]
        if missing:
            title = (f"We couldn't identify a unique {VAR_LABEL[missing[0]]} column" if missing[0] in ambiguous
                     else f"No column assigned for {', '.join(missing)}")
            hint = "".join(f"<li><b>{v}</b> — recognised names include {_names(v)}</li>" for v in missing)
            C.state("error", "rule", title, f"{escape(messages[0][1])}<ul>{hint}</ul>"
                    "Choose the matching column in the selectors above, or rename it in your file.")
        else:
            C.state("error", "error", "The data can't be analysed yet",
                    "<br>".join(escape(t) for lvl, t in messages if lvl == "error"))
            C.checks([m for m in messages if m[0] != "error"])
        _stepper(step_slot, 1)
        return
    period_msg = next((t for lvl, t in messages if t.startswith("Period in file")), "")
    C.state("ok", "task_alt", "Dataset ready",
            escape(period_msg) + "<br>" + " · ".join(escape(t.replace(" detected", "")) for lvl, t in messages if lvl == "ok"))
    issues = [m for m in messages if m[0] in ("warning", "info") and not m[1].startswith("Period in file")]
    if issues:
        C.checks(issues)
    if len(excluded):
        with st.expander(f":material/block: {len(excluded)} row(s) excluded before the analysis — show"):
            st.dataframe(excluded, hide_index=True, width="stretch")
    with st.expander(":material/visibility: Preview of the data as it will be analysed"):
        st.dataframe(clean.head(10), hide_index=True, width="stretch")

    # ---------------------------------------------------------------- Location
    C.section("location_on", "2 · Station location", "Latitude sets the Sun's geometry (Ra and day length N)")
    a, b = st.columns([1.3, 1])
    site = a.text_input("Station name", value=Path(file.name).stem, key="up_site").strip() or "Uploaded station"
    latitude = b.number_input("Latitude (decimal degrees, north positive)", min_value=-66.0, max_value=66.0,
                              value=None, step=0.01, format="%.4f", placeholder="e.g. 23.0667", key="up_lat",
                              help="Needed for extraterrestrial radiation Ra and day length N. "
                                   "Limited to ±66° (the sunset-hour-angle formula is undefined in polar day/night).")
    if latitude is None:
        C.note("Enter the station latitude to continue.", "info")
        _stepper(step_slot, 2)
        return

    # ---------------------------------------------------------------- Calculate
    C.section("calculate", "3 · Run the analysis", "16 models · 4 metrics · GPI · 5 periods")
    signature = hashlib.sha1(repr((file.name, hashlib.sha1(data).hexdigest(), sheet, sorted(mapping.items()),
                                   dayfirst, latitude, site)).encode()).hexdigest()
    if st.button("Run the 16 models", type="primary", icon=":material/play_arrow:", key="run_btn"):
        with st.status("Running the analysis …", expanded=True) as status:
            C.progress()
            st.write(":material/public: Preparing solar geometry, the Ångström–Prescott reference and 16 model estimates …")
            days = _prepare(clean, latitude)
            st.write(":material/functions: Calculating RMSE, MAE, MBE and R², and building the GPI ranking …")
            results = _evaluate(days, site)
            status.update(label=f"Analysis complete — {int(days.used.sum()):,} days evaluated",
                          state="complete", expanded=False)
        st.session_state["up_result"] = (signature, days, results)
    stored = st.session_state.get("up_result")
    if not stored or stored[0] != signature:
        st.caption("Press the button to run the analysis. Changing any setting above requires a new run.")
        _stepper(step_slot, 3)
        return
    _, days, results = stored
    _stepper(step_slot, 4)

    # ---------------------------------------------------------------- Results
    C.section("insights", f"4 · Results — {escape(site)}", f"{days.Date.min():%d %b %Y} – {days.Date.max():%d %b %Y}")
    used = int(days.used.sum())
    C.kpis([("Rows in file", f"{len(raw):,}", "as uploaded", "table_rows", False),
            ("Excluded before analysis", f"{len(excluded):,}", "invalid / duplicate dates", "block", False),
            ("Excluded by method rules", f"{len(days) - used:,}", "see breakdown below", "rule", False),
            ("Days evaluated", f"{used:,}", f"{days.Date.min():%Y} – {days.Date.max():%Y}", "event_available", True)])
    reasons = days.exclusion_reason[days.exclusion_reason != ""].value_counts()
    if len(reasons):
        with st.expander(":material/help: Why were days excluded?"):
            st.dataframe(reasons.rename_axis("reason").reset_index(name="days"), hide_index=True, width="stretch")
            st.caption("Each day is counted once, under the first rule it fails. Values are never filled or clipped.")
    C.note("The analysis applies row-level completeness and physical checks. It does not diagnose systematic "
           "sunshine-record date shifts; results assume the supplied dates and sunshine observations are correct.")

    with st.container(key="up_filters"):
        period = C.period_picker("up_p")
        metric = C.metric_picker("up_m")
    C.results_view(results, period, metric, key="up", context=f"{site} · {period}", days=days)

    C.section("download", "Download", "Every table plus validation messages, excluded rows and settings")
    files = _downloads(signature, days, results, excluded, messages, site, latitude)
    st.download_button("All results (Excel workbook)", files["xlsx"], f"{site}_solar_model_results.xlsx",
                       type="primary", icon=":material/download:")
    a, b, c, d = st.columns(4)
    a.download_button("Metrics & GPI (CSV)", files["metrics"], f"{site}_metrics_gpi.csv", width="stretch")
    b.download_button("Ranking (CSV)", files["ranking"], f"{site}_ranking.csv", width="stretch")
    c.download_button("Top 3 (CSV)", files["top3"], f"{site}_top3.csv", width="stretch")
    d.download_button("Daily predictions (CSV)", files["daily"], f"{site}_daily_predictions.csv", width="stretch")
    C.footer()


# ================================================================= Methodology
def _card(ic, title, body, tone=""):
    return f'<div class="card hover"><div class="ibadge {tone}">{C.icon(ic)}</div><h4>{title}</h4>{body}</div>'


def methodology():
    C.page_header("menu_book", "How the results are produced", "Methodology",
                  "Official study values come from the validated notebook exports. Upload & Analyze is a separate "
                  "exploratory workflow and does not regenerate the published station rankings.")
    C.flow(METHOD_STEPS)

    C.section("account_tree", "The pipeline", first=True)
    C.html('<div class="card-grid c3">'
           + _card("dataset", "1 · Inputs", "<ul><li><b>Tmax, Tmin</b> (°C) — ΔT = Tmax − Tmin drives most models</li>"
                   "<li><b>n</b> (h) — bright sunshine, used only for the reference</li><li><b>Latitude</b> — the Sun's geometry</li></ul>")
           + _card("fact_check", "2 · Quality control", "<ul><li>Tmax, Tmin present and ΔT &gt; 0</li><li>sunshine present and 0 ≤ n ≤ N</li>"
                    "<li>all 16 models finite</li></ul>"
                   f"<p style='margin-top:.4rem'>A period needs ≥ {MIN_DAYS} days. Nothing is filled, clipped or recalibrated.</p>")
           + _card("public", "3 · Solar geometry", "<p>Extraterrestrial radiation <b>Ra</b> and maximum day length <b>N</b> "
                   "from latitude and day of year, following the solar-geometry equation cited by the study.</p>")
           + _card("wb_sunny", "4 · A–P reference", "<p><b>Rs = Ra [0.25 + 0.50(n/N)]</b> — the sunshine-based standard of the "
                   "paper. It is <i>estimated</i>, not measured, radiation.</p>", "sun")
           + _card("analytics", "6 · Metrics", "<ul><li><b>RMSE</b> — typical error size, penalises large errors (best 0)</li>"
                   "<li><b>MAE</b> — average error size (best 0)</li><li><b>MBE</b> — bias; + over, − under (best 0)</li>"
                   "<li><b>R²</b> = 1 − SSE/SST — variation explained (best 1, can be negative)</li></ul>")
           + _card("emoji_events", "7 · GPI and 8 · ranking", "<p>Each metric is scaled to 0–1 across the 16 models. A model "
                   "scores for every metric on which it beats the <b>median</b> model:</p>"
                   "<p style='margin:.35rem 0'><b>GPI = Σ α·(median − scaled)</b>, α = −1 for R², +1 otherwise.</p>"
                   "<p>Highest GPI → rank 1; ranks 1–3 are the Top 3.</p>", "sun")
           + '</div>')

    C.section("date_range", "Seasons (IMD)")
    C.html('<div class="matrix-wrap"><table class="matrix"><thead><tr><th>Period</th><th>Months</th></tr></thead><tbody>'
           + "".join(f'<tr><td class="d">{C.icon(C.PERIOD_ICON[p])} {p}</td><td>{C.PERIOD_MONTHS[p]}</td></tr>' for p in PERIODS)
           + '</tbody></table></div>')

    C.section("model_training", "5 · The sixteen models",
              "Published coefficients from Karale et al. (2026), Table 2 — nothing is calibrated")
    rows = "".join(f'<tr><td class="d">{m}</td><td>{escape(a)}</td><td class="eqcell">{escape(C.equation(m))}</td>'
                   f'<td>{C.MODEL_PROFILE[m][0]}</td></tr>' for m, (a, _) in MODEL_INFO.items())
    C.html('<div class="matrix-wrap"><table class="matrix"><thead><tr><th>Model</th><th>Source</th>'
           '<th>Equation (Rs, Ra in MJ m⁻² d⁻¹)</th><th>Inputs</th></tr></thead><tbody>' + rows + '</tbody></table></div>')

    C.section("report", "Open interpretation questions",
              "Rankings are conditional on these source definitions", tone="warn")
    C.note("<b>M2</b> · the supplied table omits units; 3.6 is used to convert an interpreted kWh output to MJ.<br>"
           "<b>M8</b> · the supplied table does not define Θ; implementation uses Tmin/Tmax.<br>"
           "<b>R² and MBE</b> · results use the printed formulas; the paper's table/prose is internally inconsistent. "
           "See the sensitivity table before interpreting rankings.")

    with st.expander(":material/upload_file: Uploaded data — separate exploratory results"):
        st.markdown("- Official station results on the Overview and Model Explorer pages come directly from the notebook exports.\n"
                    "- This upload workflow calculates results for the uploaded file only; it never updates official results.\n"
                    "- All supplied dates are evaluated; the official station files span 1985–2025 with unequal valid-day coverage.\n"
                    "- Rows with a duplicated date are all excluded; rows with an invalid date are excluded.\n"
                    "- Temperatures outside −10 … 55 °C are flagged but kept.\n"
                    "- Columns are assigned automatically only when exactly one column matches.\n"
                    "- Latitude is entered by the user.")

    with st.expander(":material/functions: Technical details — equations"):
        st.markdown("**Solar geometry** (J = day of year, φ = latitude in radians, Gsc = 0.0820 MJ m⁻² min⁻¹)")
        st.latex(r"d_r = 1 + 0.003\cos\!\left(\tfrac{2\pi J}{365}\right),\quad "
                 r"\delta = 0.409\sin\!\left(\tfrac{2\pi J}{365} - 1.39\right),\quad "
                 r"\omega_s = \arccos(-\tan\varphi\,\tan\delta)")
        st.latex(r"N = \tfrac{24}{\pi}\,\omega_s,\qquad R_a = \tfrac{24\cdot 60}{\pi} G_{sc}\, d_r "
                 r"\left[\omega_s \sin\varphi \sin\delta + \cos\varphi \cos\delta \sin\omega_s\right]")
        st.caption("The primary analysis follows the 0.003 coefficient printed in the cited study's solar-geometry equation.")
        st.markdown("**Reference**")
        st.latex(r"R_s = R_a\left[0.25 + 0.50\left(\tfrac{n}{N}\right)\right],\qquad 0 \le n \le N")
        st.markdown("Here, $R_s$ is estimated global solar radiation, $R_a$ is extraterrestrial radiation, $n$ is "
                    "measured sunshine duration in hours, and $N$ is maximum possible sunshine duration in hours.")
        st.markdown("**Metrics** (Hₑ = model estimate, Hₘ = reference)")
        st.latex(r"RMSE=\sqrt{\tfrac{1}{n}\sum (H_e-H_m)^2},\quad MAE=\tfrac{1}{n}\sum |H_e-H_m|,\quad "
                 r"MBE=\tfrac{1}{n}\sum (H_e-H_m),\quad R^2 = 1-\tfrac{\sum (H_e-H_m)^2}{\sum (H_m-\bar H_m)^2}")
        st.markdown("**GPI** (y = indicator scaled to 0–1 across the 16 models, ỹ = median)")
        st.latex(r"GPI_i = \sum_j \alpha_j\,(\tilde y_j - y_{ij}),\qquad \alpha_{R^2} = -1,\ "
                 r"\alpha_{RMSE}=\alpha_{MAE}=\alpha_{MBE}=+1")
        st.caption("GPI values are rounded to 10 decimal places for ranking; tied models share the better rank. "
                   "A constant indicator contributes zero.")

    C.section("info", "Limitations")
    C.html('<div class="card-grid">'
           + _card("sensors", "Estimated reference", "<p>The reference is estimated from sunshine hours, not measured radiation.</p>")
           + _card("location_on", "Three study stations", "<p>Ahmedabad, Amreli and Okha are evaluated over station-specific daily coverage.</p>")
           + _card("travel_explore", "No direct reproduction", "<p>The supplied paper does not report these three stations.</p>")
           + '</div>')
    C.footer()
