"""Reusable building blocks: HTML cards, Plotly charts and the shared results view.

The results view is used twice — for the five demonstration districts and for an uploaded file —
so both always look and behave the same. Everything here only *displays* engine output.
"""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.config import MODELS, PERIODS
from engine.models import MODEL_INFO
from ui import styles as S

UNIT = "MJ m⁻² d⁻¹"
METRICS = ["GPI", "RMSE", "MAE", "MBE", "R2"]
METRIC_INFO = {   # label, reading guide, unit, icon
    "GPI":  ("GPI", "higher is better", "", "emoji_events"),
    "RMSE": ("RMSE", "lower is better", UNIT, "straighten"),
    "MAE":  ("MAE", "lower is better", UNIT, "target"),
    "MBE":  ("MBE", "closer to 0 is better · + overestimates, − underestimates", UNIT, "balance"),
    "R2":   ("R²", "higher is better · can be negative", "", "insights"),
}
PERIOD_ICON = {"Annual": "calendar_month", "Winter": "ac_unit", "Pre-Monsoon": "wb_sunny",
               "Monsoon": "rainy", "Post-Monsoon": "partly_cloudy_day"}
PERIOD_MONTHS = {"Annual": "Jan – Dec", "Winter": "Jan – Feb", "Pre-Monsoon": "Mar – May",
                 "Monsoon": "Jun – Sep", "Post-Monsoon": "Oct – Dec"}
RANK_ICON = {1: "emoji_events", 2: "military_tech", 3: "workspace_premium"}

# Descriptive facts about each model, taken from results/model_registry.csv and the equations (display only).
MODEL_PROFILE = {
    "M1":  ("ΔT, Ra", "square-root of ΔT", "published coefficients, used as-is"),
    "M2":  ("ΔT", "linear in ΔT, no Ra", "printed result read as kWh and × 3.6 → MJ (assumption A)"),
    "M3":  ("ΔT, Ra", "power of ΔT", "recalibrated by Marif et al. (2022)"),
    "M4":  ("ΔT, Ra", "quadratic in ΔT", "recalibrated by Marif et al. (2022)"),
    "M5":  ("ΔT, Ra", "logarithm of ΔT", "recalibrated by Marif et al. (2022)"),
    "M6":  ("ΔT, Ra", "square-root of ΔT", "recalibrated by Marif et al. (2022)"),
    "M7":  ("Tmax, Tmin, Ra", "ratio Tmax/Tmin", "published coefficients"),
    "M8":  ("Tmax, Tmin, Ra", "ratio Tmin/Tmax", "Θ taken as Tmin/Tmax (assumption B)"),
    "M9":  ("ΔT, Ra", "logarithm of ΔT", "published coefficients, used as-is"),
    "M10": ("Tmean, Ra", "linear in Ra and mean temperature", "published coefficients, used as-is"),
    "M11": ("ΔT, Ra", "linear in ΔT", "published coefficients"),
    "M12": ("Tmax, Tmin, Ra", "ratio Tmin/Tmax", "published coefficients"),
    "M13": ("Tmax, Tmin, Ra", "linear in Tmax and Tmin", "recalibrated by Ghazouani et al. (2022)"),
    "M14": ("Tmean, Ra", "linear in mean temperature", "published coefficients"),
    "M15": ("ΔT, Ra", "square-root of ΔT", "recalibrated by Onyeka et al. (2021)"),
    "M16": ("ΔT, Ra", "quadratic in ΔT", "paper's printed form, without √ΔT (assumption C)"),
}
FLAGGED = {"M2": "A", "M8": "B", "M16": "C"}


def label(metric):
    return METRIC_INFO[metric][0]


def author(model):
    return MODEL_INFO[model][0]


def equation(model):
    return MODEL_INFO[model][1].split("   [")[0]


def icon(name, cls=""):
    return f'<span class="msi {cls}" aria-hidden="true">{name}</span>'


# ---------------------------------------------------------------- HTML pieces
def html(markup):
    """Render HTML (lines are stripped so Markdown never turns indentation into code blocks)."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


SUN_ART = """<svg class="sunart" viewBox="0 0 400 400" aria-hidden="true">
<defs><radialGradient id="sg" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="var(--sun)" stop-opacity=".55"/>
<stop offset="55%" stop-color="var(--sun)" stop-opacity=".16"/><stop offset="100%" stop-color="var(--sun)" stop-opacity="0"/></radialGradient></defs>
<circle cx="230" cy="170" r="150" fill="url(#sg)"/>
<circle cx="230" cy="170" r="46" fill="var(--sun)" fill-opacity=".85"/>
<g fill="none" stroke="var(--accent)" stroke-opacity=".22" stroke-width="1.2">
<circle cx="230" cy="170" r="86"/><circle cx="230" cy="170" r="122" stroke-dasharray="3 6"/><circle cx="230" cy="170" r="160"/></g>
<circle cx="316" cy="170" r="5" fill="var(--accent)" fill-opacity=".7"/><circle cx="140" cy="250" r="4" fill="var(--accent)" fill-opacity=".5"/>
</svg>"""


def hero(eyebrow, title_html, subtitle, chips):
    chip_html = "".join(f'<span class="chip">{icon(i)}{escape(t)}</span>' for i, t in chips)
    html(f'<div class="hero">{SUN_ART}<div class="content"><div class="eyebrow">{icon("wb_sunny")}{eyebrow}</div>'
         f'<div class="hero-title">{title_html}</div><div class="hero-sub">{subtitle}</div>'
         f'<div class="chips">{chip_html}</div></div></div>')


def page_header(ic, eyebrow, title, subtitle=""):
    html(f'<div class="page-head"><div class="ibadge">{icon(ic)}</div><div>'
         f'<div class="eyebrow">{eyebrow}</div><div class="page-title">{title}</div>'
         + (f'<div class="page-sub">{subtitle}</div>' if subtitle else "") + '</div></div>')


def section(ic, title, sub="", first=False, tone=""):
    html(f'<div class="sec{" first" if first else ""}"><div class="ibadge {tone}">{icon(ic)}</div>'
         f'<div><div class="t">{title}</div>' + (f'<div class="s">{sub}</div>' if sub else "") + '</div></div>')


def kpis(items, cols=None):
    """items: (label, value, sub, icon, accent); cols fixes the number of columns (e.g. 3 for a 3 x 2 grid)."""
    cards = "".join(f'<div class="kpi{" accent" if acc else ""}"><div class="top"><span class="label">{escape(lab)}</span>'
                    f'{icon(ic)}</div><div class="value">{val}</div><div class="sub">{sub}</div></div>'
                    for lab, val, sub, ic, acc in items)
    html(f'<div class="kpi-grid{f" c{cols}" if cols else ""}">{cards}</div>')


def podium(top, context=""):
    """top: rows of rank 1-3 (columns model, rank, GPI, RMSE, MBE, R2)."""
    cards = ""
    for _, r in top.iterrows():
        k = int(r["rank"])
        cards += (f'<div class="pod r{k}"><div class="head"><span class="rank">{icon(RANK_ICON.get(k, "star"))}Rank {k}</span>'
                  f'<span class="ctx">{escape(context)}</span></div>'
                  f'<div class="model">{r.model}</div><div class="author">{escape(author(r.model))}</div>'
                  f'<div class="stats"><div>GPI<b>{r.GPI:.2f}</b></div><div>RMSE<b>{r.RMSE:.2f}</b></div>'
                  f'<div>MBE<b>{r.MBE:+.2f}</b></div><div>R²<b>{r.R2:.2f}</b></div></div></div>')
    html(f'<div class="podium">{cards}</div>')


def flow(steps):
    """steps: (icon, title, description)"""
    parts = [f'<div class="step">{icon(ic)}<div class="n">STEP {i}</div><div class="t">{t}</div><div class="d">{d}</div></div>'
             for i, (ic, t, d) in enumerate(steps, 1)]
    html('<div class="flow">' + "".join(parts) + '</div>')


STEP_ICON = ["upload_file", "fact_check", "location_on", "calculate", "insights"]


def stepper(names, current):
    cells = "".join(f'<div class="s {"done" if i < current else "now" if i == current else ""}">'
                    f'{icon("check_circle" if i < current else STEP_ICON[i])}{n}</div>' for i, n in enumerate(names))
    html(f'<div class="stepper" role="list" aria-label="Analysis steps">{cells}</div>')


CHECK_ICON = {"ok": "check_circle", "info": "info", "warning": "warning", "error": "error"}


def checks(messages):
    html("".join(f'<div class="check {lvl}">{icon(CHECK_ICON[lvl])}<span>{escape(text)}</span></div>'
                 for lvl, text in messages))


def state(kind, ic, title, body):
    """Polished empty / error / success / warning state. body is trusted HTML."""
    tone = {"error": "bad", "ok": "good", "warn": "warn", "empty": ""}[kind]
    html(f'<div class="state {kind}"><div class="ibadge {tone}">{icon(ic)}</div>'
         f'<div><div class="h">{title}</div><div class="b">{body}</div></div></div>')


def unavailable(body):
    state("error", "cloud_off", "Reference data unavailable for this analysis.", body)


def note(text, kind=""):
    html(f'<div class="note {kind}">{icon("info" if kind == "info" else "report")}<div>{text}</div></div>')


def progress():
    html('<div class="progress" role="progressbar" aria-label="Working"></div>')


def footer():
    html(f'<div class="footer">{icon("wb_sunny")}Solar Radiation Model Explorer · method after Karale, Misra, Ghosh &amp; '
         'Latwal (2026) · reference radiation = Ångström–Prescott from sunshine hours, not measured radiation.</div>')


# ---------------------------------------------------------------- pickers (same everywhere)
def period_picker(key, default="Annual"):
    return st.segmented_control("Season / period", PERIODS, default=default, key=key,
                                format_func=lambda p: f":material/{PERIOD_ICON[p]}: {p}") or default


def metric_picker(key, default="GPI"):
    return st.segmented_control("Metric", METRICS, default=default, key=key,
                                format_func=lambda m: f":material/{METRIC_INFO[m][3]}: {label(m)}") or default


def chart(fig, key):
    S.style_figure(fig)
    st.plotly_chart(fig, config=S.PLOTLY_CONFIG, key=key, width="stretch", theme=None)


# ---------------------------------------------------------------- charts
def _ramp():
    r = S.P()["ramp"]
    return [[i / (len(r) - 1), c] for i, c in enumerate(r)]


def metric_bar(table, metric):
    """All 16 models in GPI-rank order; Top 3 highlighted, rank 1 strongest."""
    p = S.P()
    t = table.sort_values("rank", ascending=False)               # rank 1 at the top
    colors = [p["bar_first"] if r == 1 else p["bar_top"] if r <= 3 else p["bar_rest"] for r in t["rank"]]
    text = [f"{v:.2f}" if r <= 3 else "" for v, r in zip(t[metric], t["rank"])]
    fig = go.Figure(go.Bar(
        x=t[metric], y=[f"{m}  ·  #{int(r)}" for m, r in zip(t.model, t["rank"])], orientation="h",
        marker=dict(color=colors, cornerradius=4), text=text, textposition="outside", cliponaxis=False,
        textfont=dict(color=p["ink"], size=12),
        customdata=np.stack([t.model.map(author), t.GPI, t.RMSE, t.MAE, t.MBE, t.R2], axis=-1),
        hovertemplate="<b>%{y}</b><br>%{customdata[0]}<br><br>GPI %{customdata[1]:.3f}<br>RMSE %{customdata[2]:.2f} · "
                      "MAE %{customdata[3]:.2f}<br>MBE %{customdata[4]:+.2f} · R² %{customdata[5]:.3f}<extra></extra>"))
    unit = METRIC_INFO[metric][2]
    fig.update_layout(height=540, bargap=0.3, showlegend=False, margin=dict(l=8, r=46, t=10, b=8),
                      transition=dict(duration=400, easing="cubic-in-out"),
                      xaxis_title=f"{label(metric)}{' (' + unit + ')' if unit else ''} — {METRIC_INFO[metric][1]}")
    fig.add_vline(x=0, line_width=1, line_color=p["border"])
    return fig


def _heatmap(z, x, y, text, colorscale, zmid=None, reverse=False, hover="", height=None):
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y, text=text, texttemplate="%{text}", textfont=dict(size=11),
        colorscale=colorscale, reversescale=reverse, zmid=zmid, xgap=3, ygap=3, colorbar=dict(len=0.8),
        hovertemplate=hover or "%{y} · %{x}<br>%{z:.3f}<extra></extra>", hoverongaps=False))
    fig.update_layout(height=height or 36 * len(y) + 80, margin=dict(l=8, r=8, t=10, b=8),
                      yaxis=dict(autorange="reversed", showgrid=False), xaxis=dict(side="top", showgrid=False))
    return fig


def rank_heatmap(results, highlight=None):
    """Model x period GPI rank for one site (1 = best, strongest colour)."""
    pv = results.pivot_table(index="model", columns="period", values="rank").reindex(index=MODELS, columns=PERIODS)
    text = pv.map(lambda v: "" if pd.isna(v) else f"{int(v)}")
    fig = _heatmap(pv.values, PERIODS, MODELS, text.values, _ramp(), reverse=True,
                   hover="%{y} · %{x}<br>GPI rank %{z}<extra></extra>")
    if highlight in MODELS:
        i = MODELS.index(highlight)
        fig.add_shape(type="rect", x0=-0.5, x1=len(PERIODS) - 0.5, y0=i - 0.5, y1=i + 0.5,
                      line=dict(color=S.P()["sun"], width=2.5))
    return fig


def metric_heatmap(pivot, metric):
    """Rows = models, columns = sites or periods; stronger colour = better."""
    if metric in ("GPI", "MBE"):
        scale, zmid, rev = S.P()["diverging"], 0, False
    else:
        scale, zmid, rev = _ramp(), None, metric in ("RMSE", "MAE")
    text = pivot.map(lambda v: "n/a" if pd.isna(v) else f"{v:.2f}")
    return _heatmap(pivot.values, list(pivot.columns), list(pivot.index), text.values, scale, zmid, rev,
                    hover="%{y} · %{x}<br>" + label(metric) + " %{z:.3f}<extra></extra>")


def season_dots(results, metric, models):
    """Selected models (max 3) across the five periods — dots, because periods are categories."""
    p = S.P()
    fig = go.Figure()
    for i, m in enumerate(models[:3]):
        r = results[results.model == m].set_index("period").reindex(PERIODS)
        fig.add_trace(go.Scatter(x=PERIODS, y=r[metric], name=m, mode="markers",
                                 marker=dict(size=14, color=p["series"][i], line=dict(width=2, color=p["surface"])),
                                 customdata=r["rank"],
                                 hovertemplate=f"<b>{m}</b> · %{{x}}<br>{label(metric)} %{{y:.3f}} · rank %{{customdata}}<extra></extra>"))
    unit = METRIC_INFO[metric][2]
    fig.update_layout(height=370, yaxis_title=f"{label(metric)}{' (' + unit + ')' if unit else ''}",
                      hovermode="x unified", margin=dict(l=8, r=8, t=48, b=8), scattermode="group",
                      xaxis=dict(range=[-0.6, len(PERIODS) - 0.4]))
    return fig


def model_period_bars(results, model):
    """GPI rank of one model in every period (1 = best)."""
    p = S.P()
    r = results[results.model == model].set_index("period").reindex(PERIODS)
    ranks = r["rank"].astype(float)
    colors = [p["bar_first"] if v == 1 else p["bar_top"] if v <= 3 else p["bar_rest"] for v in ranks.fillna(99)]
    fig = go.Figure(go.Bar(
        x=[f"{PERIOD_MONTHS[q]}<br><b>{q}</b>" for q in PERIODS], y=17 - ranks, marker=dict(color=colors, cornerradius=5),
        text=[f"#{int(v)}" if pd.notna(v) else "n/a" for v in ranks], textposition="outside", cliponaxis=False,
        textfont=dict(color=p["ink"], size=13),
        customdata=np.stack([r.GPI, r.RMSE, r.MAE, r.MBE, r.R2], axis=-1),
        hovertemplate="<b>%{x}</b><br>rank %{text}<br>GPI %{customdata[0]:.3f} · RMSE %{customdata[1]:.2f}<br>"
                      "MAE %{customdata[2]:.2f} · MBE %{customdata[3]:+.2f} · R² %{customdata[4]:.3f}<extra></extra>"))
    fig.update_layout(height=300, showlegend=False, margin=dict(l=8, r=8, t=24, b=8), bargap=0.45,
                      transition=dict(duration=400, easing="cubic-in-out"),
                      yaxis=dict(range=[0, 17.5], showticklabels=False, showgrid=False, title="higher bar = better rank"))
    return fig


def annual_gpi_dots(results, districts):
    """Annual GPI of all 16 models in each ranked district (one dot per district)."""
    p = S.P()
    fig = go.Figure()
    for i, d in enumerate(districts[:3]):
        t = results[(results.district == d) & (results.period == "Annual")].set_index("model").reindex(MODELS)
        fig.add_trace(go.Scatter(x=MODELS, y=t.GPI, name=d, mode="markers",
                                 marker=dict(size=13, color=p["series"][i], line=dict(width=2, color=p["surface"])),
                                 customdata=np.stack([t["rank"], t.RMSE, t.R2], axis=-1),
                                 hovertemplate=f"<b>%{{x}}</b> · {d}<br>GPI %{{y:.3f}} · rank %{{customdata[0]:.0f}}<br>"
                                               "RMSE %{customdata[1]:.2f} · R² %{customdata[2]:.2f}<extra></extra>"))
    fig.add_hline(y=0, line_width=1, line_color=p["border"])
    fig.update_layout(height=400, yaxis_title="Annual GPI (higher = better)", hovermode="x unified",
                      scattermode="group", margin=dict(l=8, r=8, t=48, b=8),
                      xaxis=dict(range=[-0.7, len(MODELS) - 0.3]))   # room for grouped dots at both ends
    return fig


def obs_pred(days, model):
    """A-P reference vs model estimate (daily), with the 1:1 line."""
    p = S.P()
    x, y = days.Rs_AP, days[model]
    lim = [0, float(np.nanmax([x.max(), y.max()])) * 1.05]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=x, y=y, mode="markers", name=model,
                               marker=dict(size=5, color=p["accent"], opacity=0.3, line=dict(width=0)),
                               customdata=days.Date.dt.strftime("%d %b %Y"),
                               hovertemplate="%{customdata}<br>A–P %{x:.2f} · " + model + " %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", name="1:1 line",
                             line=dict(color=p["one_to_one"], width=1.5, dash="dash"), hoverinfo="skip"))
    fig.update_layout(height=450, xaxis_title=f"A–P reference Rs ({UNIT})", yaxis_title=f"{model} estimate ({UNIT})",
                      xaxis_range=lim, yaxis_range=lim, showlegend=True)
    return fig


# ---------------------------------------------------------------- tables
def metrics_table(table):
    t = table.sort_values("rank")
    return pd.DataFrame({"Rank": t["rank"].astype(int), "Model": t.model, "Author": t.model.map(author),
                         "GPI": t.GPI, "RMSE": t.RMSE, "MAE": t.MAE, "MBE": t.MBE, "R²": t.R2, "Days": t.n.astype(int)})


def show_table(df, key, **kw):
    fmt = {c: st.column_config.NumberColumn(format="%.3f") for c in ("GPI", "RMSE", "MAE", "MBE", "R²")}
    st.dataframe(df, hide_index=True, width="stretch", key=key, column_config={
        **fmt, "Rank": st.column_config.NumberColumn(width="small"), "Author": st.column_config.TextColumn(width="large")}, **kw)


# ---------------------------------------------------------------- model profile
def model_profile(results, period, key, default):
    """Pick one of the 16 models and see its equation, inputs and performance in every period."""
    model = st.pills("Choose a model", MODELS, default=default, key=f"{key}_model") or default
    row = results[(results.period == period) & (results.model == model)].iloc[0]
    inputs, form, src = MODEL_PROFILE[model]
    rank = int(row["rank"])
    flag = f'<span class="tag flag">assumption {FLAGGED[model]}</span>' if model in FLAGGED else ""

    def stat(lab, val, cls=""):
        return f'<div class="mstat {cls}"><div class="l">{lab}</div><div class="v">{val}</div></div>'

    uses = inputs.replace(", Ra", "")
    html(f'<div class="model-card"><div>'
         f'<div class="code">{model}<small>{icon(RANK_ICON.get(rank, "tag"))} rank {rank} of 16 · {period}</small></div>'
         f'<div class="who">{escape(author(model))}</div>'
         f'<div class="eq">{escape(equation(model))}</div>'
         f'<span class="tag">inputs: {inputs}</span><span class="tag">{form}</span>{flag}'
         f'<div class="desc">Estimates daily solar radiation Rs from {uses}'
         f'{" and extraterrestrial radiation Ra" if "Ra" in inputs else " only (no Ra term)"}; {src}.</div></div>'
         f'<div class="mstats">{stat("GPI", f"{row.GPI:.3f}", "hi")}{stat("Rank", f"#{rank}", "sun" if rank <= 3 else "")}'
         f'{stat("Days", f"{int(row.n):,}")}{stat("RMSE", f"{row.RMSE:.2f}")}{stat("MAE", f"{row.MAE:.2f}")}'
         f'{stat("MBE", f"{row.MBE:+.2f}")}{stat("R²", f"{row.R2:.3f}")}</div></div>')
    st.caption(f"Seasonal performance of {model}: GPI rank among the 16 models in each period (hover for metrics). "
               "Periods without enough valid days show n/a.")
    chart(model_period_bars(results, model), f"{key}_mbars")


# ---------------------------------------------------------------- shared results view
STATUS_TEXT = {"no valid reference data": "No day in this period passed all inclusion rules, so there is no "
                                          "Ångström–Prescott reference to compare the models with.",
               "insufficient days (<30)": "Fewer than 30 valid days in this period — the method needs at least 30 "
                                          "to compare the models reliably. Try another period or a longer record."}


def results_view(results, period, metric, key, context, days=None, unavailable_reason=None, daily_note=None):
    """KPIs, Top 3, ranking, model profile, all metrics, seasonal comparison and observed-vs-predicted for one site."""
    table = results[results.period == period]
    status = table.status.iloc[0] if len(table) else "no valid reference data"
    if status != "ok":
        unavailable(unavailable_reason or STATUS_TEXT.get(status, status))
        return
    best = table.sort_values("rank").iloc[0]
    kpis([("Best model", best.model, escape(author(best.model)), "emoji_events", True),
          ("GPI", f"{best.GPI:.2f}", "rank-1 score", "leaderboard", False),
          ("RMSE", f"{best.RMSE:.2f}", UNIT, "straighten", False),
          ("R²", f"{best.R2:.2f}", "1 − SSE/SST", "insights", False),
          ("Days evaluated", f"{int(best.n):,}", PERIOD_MONTHS[period], "event_available", False)])
    section("military_tech", "Top 3 models", f"Highest GPI · {context}", tone="sun")
    podium(table[table["rank"] <= 3].sort_values("rank"), context)

    tabs = st.tabs([":material/leaderboard: Ranking", ":material/model_training: Model profile",
                    ":material/table_chart: All metrics", ":material/date_range: Seasonal comparison",
                    ":material/scatter_plot: Observed vs predicted"])
    with tabs[0]:
        st.caption(f"{label(metric)} of all 16 models, ordered by GPI rank (Top 3 highlighted). "
                   f"{label(metric)}: {METRIC_INFO[metric][1]}.")
        chart(metric_bar(table, metric), f"{key}_bar")
    with tabs[1]:
        model_profile(results, period, key, best.model)
    with tabs[2]:
        st.caption("All four indicators and the GPI. The GPI combines them; see Methodology. Click a column to sort.")
        show_table(metrics_table(table), f"{key}_table")
    with tabs[3]:
        st.caption("GPI rank of every model in every period (1 = best, stronger colour = better).")
        chart(rank_heatmap(results), f"{key}_rankmap")
        top = list(table.sort_values("rank").model[:3])
        chosen = st.multiselect("Compare models across periods (up to 3)", MODELS, default=top,
                                max_selections=3, key=f"{key}_lines")
        if chosen:
            chart(season_dots(results, metric, chosen), f"{key}_season")
    with tabs[4]:
        if days is None:
            state("empty", "lock", "Daily values are not part of the public demo",
                  daily_note or "The raw IMD station data are not redistributed, so the day-by-day comparison is "
                                "hidden here. Upload your own data on <b>Upload &amp; Analyze</b> to see this chart.")
        else:
            sel = days[days.used] if period == "Annual" else days[days.used & (days.Season == period)]
            m = st.selectbox("Model", MODELS, index=MODELS.index(best.model), key=f"{key}_op")
            st.caption(f"Each dot is one day ({len(sel):,} days). Dots on the dashed line = perfect agreement. "
                       "Drag to zoom, double-click to reset.")
            chart(obs_pred(sel, m), f"{key}_scatter")
