"""The four pages: Overview, Model Explorer, Upload & Analyze, Methodology."""
import hashlib
import io
from pathlib import Path

import pandas as pd
import streamlit as st

from engine.config import (DISTRICTS, LATITUDE, MODELS, PERIODS, SEASON_OF_MONTH, MIN_DAYS,
                           FIRST_YEAR, LAST_YEAR, A_AP, B_AP)
from engine.models import MODEL_INFO
from engine.pipeline import prepare_days, evaluate_all_periods, top3
from engine.validation import (read_table, detect_columns, ambiguous_columns, build_input,
                               exclusion_reasons, TEMPLATE)
from ui import components as C

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "data" / "demo"
PRIVATE_DAILY = ROOT / "data" / "private" / "daily_predictions.csv"
NAV = {}   # page objects, filled by app.py (used for in-page links)

UNAVAILABLE = {
    "Surat": "The IMD sunshine record of Surat could not be used in any year of 2002–2023: 22 % of days are "
             "missing, 17 years have fewer than 200 sunshine days, and 2002 is shifted by about 10 days against "
             "satellite cloudiness. Without a usable sunshine record there is no Ångström–Prescott reference, "
             "so the models cannot be ranked (project README §8, results/qc_report.csv).",
    "Deesa": "The Deesa record starts only in 2012, and every year matches satellite cloudiness only when it is "
             "shifted by 50–75 days (a date shift in the sunshine record). The record failed the project's "
             "sunshine-quality check in every year, so there is no Ångström–Prescott reference and no ranking "
             "(project README §8, results/qc_report.csv).",
}
DISTRICT_NOTE = {"Ahmedabad": "all 22 sunshine-years used", "Amreli": "15 of 22 sunshine-years used",
                 "Okha": "2002–2021 used (2022–23 failed QC)", "Surat": "sunshine record unusable",
                 "Deesa": "sunshine record unusable"}


# ================================================================= data
@st.cache_data(show_spinner=False)
def load_demo():
    results = pd.concat([pd.read_csv(DEMO / "annual_gpi.csv"), pd.read_csv(DEMO / "seasonal_gpi.csv")],
                        ignore_index=True)
    return results, pd.read_csv(DEMO / "district_comparison.csv")


@st.cache_data(show_spinner=False)
def load_demo_daily():
    """Daily values are private (raw IMD data, decision D7): returns {} when the file is absent."""
    if not PRIVATE_DAILY.exists():
        return {}
    d = pd.read_csv(PRIVATE_DAILY, parse_dates=["Date"])
    return {k: g.reset_index(drop=True) for k, g in d.groupby("district")}


@st.cache_data(show_spinner=False, max_entries=8)
def run_analysis(clean, latitude, site):
    """Uploaded data through the same engine (no sunshine-year filter, all dates: decisions D1, D2)."""
    days = prepare_days(clean, latitude)
    days["source_row"] = clean.source_row.to_numpy()
    days["exclusion_reason"] = exclusion_reasons(days)
    return days, evaluate_all_periods(days, site)


# ================================================================= Overview
def overview():
    results, comparison = load_demo()
    C.page_header("MSc Agriculture Analytics · Gujarat, India", "Solar Radiation Model Explorer",
                  "Which temperature-based model best estimates daily solar radiation where only "
                  "Tmax, Tmin and sunshine records exist? Sixteen published models are compared against the "
                  "Ångström–Prescott reference and ranked with the Global Performance Indicator (GPI) — "
                  "for the whole year and for each IMD season.", hero=True)
    c1, c2, _ = st.columns([1, 1, 2])
    c1.page_link(NAV["explorer"], label="Explore the models", icon=":material/insights:")
    c2.page_link(NAV["upload"], label="Analyze your own data", icon=":material/upload_file:")

    used = int(comparison["days used"].sum())
    C.kpis([("Models compared", "16", "M1 – M16, published coefficients", True),
            ("Districts", "5", "3 ranked · 2 without reference", False),
            ("Periods", "5", "Annual + 4 IMD seasons", False),
            ("Study period", f"{FIRST_YEAR}–{LAST_YEAR}", "22 years", False),
            ("Days evaluated", f"{used:,}", "district-days in the ranking", False)])

    st.markdown("## Demonstration districts")
    cards = ""
    for d in DISTRICTS:
        row = comparison[comparison.district == d].iloc[0]
        ok = row["days used"] > 0
        top = row["Top 3 Annual"] if ok else "—"
        cards += (f'<div class="district"><div class="name">{d}</div>'
                  f'<span class="chip {"ok" if ok else "na"}">{"Ranked" if ok else "Reference unavailable"}</span>'
                  f'<div class="meta">{LATITUDE[d]:.2f}° N · {int(row["days used"]):,} days<br>{DISTRICT_NOTE[d]}'
                  f'<br>Annual Top 3: <b>{top}</b></div></div>')
    C.html(f'<div class="district-grid">{cards}</div>')

    st.markdown("## How the comparison works")
    C.flow([("Input", "Tmax, Tmin, sunshine hours"), ("QC", "inclusion rules"),
            ("Solar geometry", "Ra and day length N"), ("A–P reference", "Rs from sunshine"),
            ("16 models", "Rs from temperature"), ("Metrics", "RMSE · MAE · MBE · R²"),
            ("GPI", "one combined score"), ("Ranking", "Top 3 per period")])
    st.page_link(NAV["method"], label="Read the methodology", icon=":material/menu_book:")

    st.markdown("## Purpose")
    st.markdown("Solar radiation drives crop growth and evapotranspiration, yet it is measured at few stations. "
                "Temperature is recorded almost everywhere, so temperature-based models are a practical substitute. "
                "Their accuracy changes with season and place — this dashboard shows **which model to use, "
                "where and when**, using the method of Karale et al. (2026).")
    C.footer()


# ================================================================= Model Explorer
def explorer():
    results, comparison = load_demo()
    daily = load_demo_daily()
    C.page_header("Validated project results", "Model Explorer",
                  "Results of the five Gujarat districts, exactly as produced and validated by the project notebook.")
    c1, c2 = st.columns([1, 1.25])
    with c1:
        district = st.segmented_control("District", DISTRICTS, default="Ahmedabad", key="ex_d") or "Ahmedabad"
    with c2:
        period = C.period_picker("ex_p")
    metric = C.metric_picker("ex_m")

    st.markdown(f"## {district} · {period}")
    C.results_view(results[results.district == district], period, metric, key="ex",
                   days=daily.get(district), unavailable_reason=UNAVAILABLE.get(district))

    st.markdown("## Across districts")
    st.caption(f"{C.label(metric)} of every model in each district · {period} · {C.METRIC_INFO[metric][1]}. "
               "n/a = reference data unavailable.")
    sel = results[results.period == period]
    pivot = sel.pivot_table(index="model", columns="district", values=metric, dropna=False) \
        .reindex(index=MODELS, columns=DISTRICTS)
    C.chart(C.metric_heatmap(pivot, metric), "ex_cross")
    st.markdown("### Top 3 by district and period")
    st.dataframe(comparison.drop(columns=["annual rank-1 R2", "annual rank-1 RMSE"]), hide_index=True,
                 width="stretch")

    with st.expander("Download the validated results (CSV)"):
        cols = st.columns(4)
        for col, name in zip(cols, ["annual_gpi", "seasonal_gpi", "top_3_models", "model_ranking"]):
            col.download_button(name.replace("_", " ").title(), (DEMO / f"{name}.csv").read_bytes(),
                                f"{name}.csv", "text/csv", key=f"dl_{name}", width="stretch")
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
    daily = _days.drop(columns=["Year", "Tmean", "temperature_ok", "sunshine_year_ok"])
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
    about = pd.DataFrame({"item": ["Station", "Latitude (deg)", "Method", "Reference", "Sunshine-year check",
                                   "Period", "Minimum days per period"],
                          "value": [site, latitude, "Karale et al. (2026); 16 models, RMSE/MAE/MBE/R2, GPI",
                                    f"Angstrom-Prescott, a = {A_AP}, b = {B_AP}",
                                    "NOT applied (needs satellite data; project decision D1)",
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


def upload():
    C.page_header("Run the method on your data", "Upload & Analyze",
                  "Upload daily station data. It is processed locally by the same engine that reproduces the "
                  "project results — nothing is sent elsewhere and your values are never altered.")
    step_slot = st.empty()

    with st.expander("What file do I need?", expanded=False):
        st.markdown("One row per day, with these columns (names are detected automatically; you can also "
                    "assign them by hand):")
        st.dataframe(pd.DataFrame({
            "Variable": ["Date", "Tmax", "Tmin", "SSH"],
            "Meaning": ["Calendar date — or three columns Year, Month, Day",
                        "Daily maximum air temperature", "Daily minimum air temperature",
                        "Bright sunshine duration (n)"],
            "Unit": ["e.g. 2020-01-31 or 31/01/2020", "°C", "°C", "hours"],
            "Recognised names": ["Date · YEAR + MN + DT", "Tmax, MAX, Max Temp", "Tmin, MIN, Min Temp",
                                 "SSH, Sunshine, BSS"]}), hide_index=True, width="stretch")
        st.markdown("Blank cells are treated as missing. Leave gaps as blanks — do not fill them.")
        t1, t2, _ = st.columns([1, 1, 2])
        t1.download_button("Template (.xlsx)", _template_bytes("xlsx"), "solar_template.xlsx", width="stretch")
        t2.download_button("Template (.csv)", _template_bytes("csv"), "solar_template.csv", "text/csv", width="stretch")
        st.caption("Template rows are illustrative only — replace them with your station's data.")

    file = st.file_uploader("Upload an Excel (.xlsx) or CSV file", type=["xlsx", "csv", "xls"])
    if file is None:
        _stepper(step_slot, 0)
        C.footer()
        return
    data = file.getvalue()
    try:
        sheets = read_table(file.name, data)
    except ValueError as exc:
        C.checks([("error", str(exc))])
        _stepper(step_slot, 0)
        return
    sheet = st.selectbox("Sheet", list(sheets), key="up_sheet") if len(sheets) > 1 else next(iter(sheets))
    raw = sheets[sheet]

    # ---------------------------------------------------------------- Validate & map
    st.markdown("## 1 · Check the columns")
    st.caption(f"{len(raw):,} rows × {len(raw.columns)} columns read from “{file.name}”. First rows:")
    st.dataframe(raw.head(6), hide_index=True, width="stretch")
    cols = [None] + list(raw.columns)
    found = detect_columns(list(raw.columns))
    ambiguous = {v: c for v, c in ambiguous_columns(list(raw.columns)).items()
                 if not (found["Date"] is not None and v in ("Year", "Month", "Day"))}
    if ambiguous:
        C.checks([("warning", f"Several columns could be {v}: " + ", ".join(f"“{x}”" for x in c)
                   + ". It was not assigned automatically — please choose the right one below.")
                  for v, c in ambiguous.items()])
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
    C.checks(messages)
    if clean is None:
        _stepper(step_slot, 1)
        return
    if len(excluded):
        with st.expander(f"{len(excluded)} row(s) excluded before the analysis — show"):
            st.dataframe(excluded, hide_index=True, width="stretch")
    with st.expander("Preview of the data as it will be analysed"):
        st.dataframe(clean.head(10), hide_index=True, width="stretch")

    # ---------------------------------------------------------------- Location
    st.markdown("## 2 · Station location")
    a, b = st.columns([1.3, 1])
    site = a.text_input("Station name", value=Path(file.name).stem, key="up_site").strip() or "Uploaded station"
    latitude = b.number_input("Latitude (decimal degrees, north positive)", min_value=-66.0, max_value=66.0,
                              value=None, step=0.01, format="%.4f", placeholder="e.g. 23.0667", key="up_lat",
                              help="Needed for extraterrestrial radiation Ra and day length N. "
                                   "Limited to ±66° (the sunset-hour-angle formula is undefined in polar day/night).")
    if latitude is None:
        C.note("Enter the station latitude to continue.")
        _stepper(step_slot, 2)
        return

    # ---------------------------------------------------------------- Calculate
    st.markdown("## 3 · Calculate")
    signature = hashlib.sha1(repr((file.name, hashlib.sha1(data).hexdigest(), sheet, sorted(mapping.items()),
                                   dayfirst, latitude, site)).encode()).hexdigest()
    if st.button("Run the 16 models", type="primary", icon=":material/play_arrow:"):
        with st.spinner("Calculating solar geometry, reference radiation, 16 models, metrics and GPI …"):
            st.session_state["up_result"] = (signature, *run_analysis(clean, latitude, site))
    stored = st.session_state.get("up_result")
    if not stored or stored[0] != signature:
        st.caption("Press the button to run the analysis. Changing any setting above requires a new run.")
        _stepper(step_slot, 3)
        return
    _, days, results = stored
    _stepper(step_slot, 4)

    # ---------------------------------------------------------------- Results
    st.markdown(f"## 4 · Results — {site}")
    used = int(days.used.sum())
    C.kpis([("Rows in file", f"{len(raw):,}", "as uploaded", False),
            ("Excluded before analysis", f"{len(excluded):,}", "invalid / duplicate dates", False),
            ("Excluded by method rules", f"{len(days) - used:,}", "see breakdown below", False),
            ("Days evaluated", f"{used:,}", f"{days.Date.min():%Y} – {days.Date.max():%Y}", True)])
    reasons = days.exclusion_reason[days.exclusion_reason != ""].value_counts()
    if len(reasons):
        with st.expander("Why were days excluded?"):
            st.dataframe(reasons.rename_axis("reason").reset_index(name="days"), hide_index=True, width="stretch")
            st.caption("Each day is counted once, under the first rule it fails. Values are never filled or clipped.")
    C.note("The project's satellite cross-check of the sunshine record (used for the five demonstration districts) "
           "cannot be run on uploaded data. Results assume your sunshine record is correct and correctly dated.")

    c1, c2 = st.columns([1.25, 1])
    with c1:
        period = C.period_picker("up_p")
    with c2:
        metric = C.metric_picker("up_m")
    C.results_view(results, period, metric, key="up", days=days)

    st.markdown("## Download")
    files = _downloads(signature, days, results, excluded, messages, site, latitude)
    st.caption("The workbook holds every table below plus the validation messages, excluded rows and settings used.")
    st.download_button("All results (Excel workbook)", files["xlsx"], f"{site}_solar_model_results.xlsx",
                       type="primary", icon=":material/download:")
    a, b, c, d = st.columns(4)
    a.download_button("Metrics & GPI (CSV)", files["metrics"], f"{site}_metrics_gpi.csv", width="stretch")
    b.download_button("Ranking (CSV)", files["ranking"], f"{site}_ranking.csv", width="stretch")
    c.download_button("Top 3 (CSV)", files["top3"], f"{site}_top3.csv", width="stretch")
    d.download_button("Daily predictions (CSV)", files["daily"], f"{site}_daily_predictions.csv", width="stretch")
    C.footer()


# ================================================================= Methodology
def methodology():
    C.page_header("How the results are produced", "Methodology",
                  "The dashboard implements the final project notebook without changes. Each step below maps to "
                  "one file in the engine/ folder.")
    C.flow([("Input", "Tmax, Tmin, sunshine n, latitude"),
            ("QC", "keep only valid days"),
            ("Solar geometry", "Ra, day length N (FAO-56)"),
            ("A–P reference", "Rs = (0.25 + 0.50 n/N) Ra"),
            ("16 models", "Rs from temperature"),
            ("Metrics", "RMSE · MAE · MBE · R²"),
            ("GPI", "combine the four"),
            ("Ranking", "highest GPI = rank 1")])

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown("### 1 · Inputs")
        st.markdown("- **Tmax, Tmin** (°C) — daily air temperature; ΔT = Tmax − Tmin drives most models\n"
                    "- **n** (h) — bright sunshine hours, used only for the reference\n"
                    "- **Latitude** — fixes the Sun's geometry")
        st.markdown("### 2 · Quality control")
        st.markdown("A day is used only if **all** hold:\n"
                    "- Tmax and Tmin present and **ΔT > 0**\n"
                    "- sunshine present and **0 ≤ n ≤ N**\n"
                    "- all 16 models give a finite value\n"
                    "- *(demo districts only)* the year passed the satellite sunshine check\n\n"
                    f"A period needs **≥ {MIN_DAYS} days**. Nothing is filled, clipped or recalibrated.")
        st.markdown("### 3 · Solar geometry and 4 · reference")
        st.markdown("Extraterrestrial radiation **Ra** and day length **N** follow FAO-56. The reference is the "
                    "Ångström–Prescott radiation **Rs = (0.25 + 0.50·n/N)·Ra** — a sunshine-based standard, "
                    "*not* measured radiation.")
    with right:
        st.markdown("### 6 · Metrics")
        st.dataframe(pd.DataFrame({
            "Metric": ["RMSE", "MAE", "MBE", "R²"],
            "Measures": ["typical error size (penalises large errors)", "average error size",
                         "systematic bias (+ over, − under)", "share of variation explained"],
            "Best": ["0", "0", "0", "1"]}), hide_index=True, width="stretch")
        st.markdown("### 7 · GPI and 8 · ranking")
        st.markdown("Within one site and period, each metric is scaled to 0–1 across the 16 models. "
                    "A model scores for every metric on which it beats the **median** model:\n\n"
                    "GPI = Σ α · (median − scaled value), α = −1 for R², +1 for RMSE, MAE, MBE.\n\n"
                    "Highest GPI → rank 1; the three highest form the **Top 3**.")
        st.markdown("### Seasons (IMD)")
        seasons = {}
        for m, s in SEASON_OF_MONTH.items():
            seasons.setdefault(s, []).append(pd.Timestamp(2001, m, 1).strftime("%b"))
        st.dataframe(pd.DataFrame({"Period": PERIODS,
                                   "Months": ["Jan – Dec"] + [f"{v[0]} – {v[-1]}" for v in seasons.values()]}),
                     hide_index=True, width="stretch")

    st.markdown("### 5 · The sixteen models")
    st.dataframe(pd.DataFrame([{"Model": m, "Author": a, "Equation (Rs, Ra in MJ m⁻² d⁻¹)": e}
                               for m, (a, e) in MODEL_INFO.items()]), hide_index=True, width="stretch", height=597)
    st.caption("Published coefficients from Karale et al. (2026), Table 2 — nothing is calibrated.")

    st.markdown("### Assumptions not yet settled by the group")
    C.note("<b>Rankings are conditional on these interpretations</b> (project README §7):<br>"
           "<b>A</b> · M2 multiplied by 3.6 (printed result read as kWh → MJ)<br>"
           "<b>B</b> · M8 uses Θ = Tmin/Tmax (Θ is undefined in the paper)<br>"
           "<b>C</b> · M16 in the paper's printed form (no √ΔT)<br>"
           "<b>D</b> · R² = 1 − SSE/SST, the paper's formula (its printed values behave like r²)<br>"
           "<b>E</b> · MBE enters the GPI with its sign, as in the paper")

    with st.expander("Uploaded data — what differs from the demonstration districts"):
        st.markdown("- The satellite sunshine-record check is **not** applied (it needs NASA POWER data). "
                    "Years with < 200 sunshine values are flagged.\n"
                    "- All dates in the file are used (the demo uses 2002–2023).\n"
                    "- Rows with a duplicated date are all excluded; rows with an invalid date are excluded.\n"
                    "- Temperatures outside −10 … 55 °C are flagged but kept.\n"
                    "- Latitude is entered by the user.")

    with st.expander("Technical details — equations"):
        st.markdown("**Solar geometry** (J = day of year, φ = latitude in radians, Gsc = 0.0820 MJ m⁻² min⁻¹)")
        st.latex(r"d_r = 1 + 0.033\cos\!\left(\tfrac{2\pi J}{365}\right),\quad "
                 r"\delta = 0.409\sin\!\left(\tfrac{2\pi J}{365} - 1.39\right),\quad "
                 r"\omega_s = \arccos(-\tan\varphi\,\tan\delta)")
        st.latex(r"N = \tfrac{24}{\pi}\,\omega_s,\qquad R_a = \tfrac{24\cdot 60}{\pi} G_{sc}\, d_r "
                 r"\left[\omega_s \sin\varphi \sin\delta + \cos\varphi \cos\delta \sin\omega_s\right]")
        st.caption("The paper prints 0.003 in dr; this is a typo and FAO-56's 0.033 is used.")
        st.markdown("**Reference**")
        st.latex(r"R_{s,AP} = \left(0.25 + 0.50\,\tfrac{n}{N}\right) R_a \qquad (0 \le n \le N)")
        st.markdown("**Metrics** (Hₑ = model estimate, Hₘ = reference)")
        st.latex(r"RMSE=\sqrt{\tfrac{1}{n}\sum (H_e-H_m)^2},\quad MAE=\tfrac{1}{n}\sum |H_e-H_m|,\quad "
                 r"MBE=\tfrac{1}{n}\sum (H_e-H_m),\quad R^2 = 1-\tfrac{\sum (H_e-H_m)^2}{\sum (H_m-\bar H_m)^2}")
        st.markdown("**GPI** (y = indicator scaled to 0–1 across the 16 models, ỹ = median)")
        st.latex(r"GPI_i = \sum_j \alpha_j\,(\tilde y_j - y_{ij}),\qquad \alpha_{R^2} = -1,\ "
                 r"\alpha_{RMSE}=\alpha_{MAE}=\alpha_{MBE}=+1")
        st.caption("Ties share the better rank. If all models have the same value of one indicator, "
                   "the scaling is undefined and the GPI is not computed.")

    st.markdown("### Limitations")
    st.markdown("- The reference is **estimated** from sunshine hours, not measured radiation.\n"
                "- Surat and Deesa have no usable sunshine record, so they are not ranked.\n"
                "- None of the five stations is in the paper; no direct numerical reproduction is possible.\n"
                "- NASA POWER satellite data were used only to check sunshine records, never as the reference.")
    C.footer()
