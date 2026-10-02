"""Reusable building blocks: HTML cards, Plotly charts and the shared results view.

The results view is used twice — for the five demonstration districts and for an uploaded file —
so both always look and behave the same.
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
METRIC_INFO = {
    "GPI":  ("GPI", "higher is better", ""),
    "RMSE": ("RMSE", "lower is better", UNIT),
    "MAE":  ("MAE", "lower is better", UNIT),
    "MBE":  ("MBE", "closer to 0 is better · + overestimates, − underestimates", UNIT),
    "R2":   ("R²", "higher is better · can be negative", ""),
}


def label(metric):
    return METRIC_INFO[metric][0]


def author(model):
    return MODEL_INFO[model][0]


# ---------------------------------------------------------------- HTML pieces
def html(markup):
    """Render HTML (lines are stripped so Markdown never turns indentation into code blocks)."""
    st.markdown("".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def page_header(eyebrow, title, subtitle="", hero=False):
    body = f'<div class="eyebrow">{eyebrow}</div><div class="page-title">{title}</div>' + \
           (f'<div class="page-sub">{subtitle}</div>' if subtitle else "")
    html(f'<div class="hero">{body}</div>' if hero else body)


def kpis(items):
    """items: (label, value, sub, accent)"""
    cards = "".join(f'<div class="kpi{" accent" if acc else ""}"><div class="label">{escape(lab)}</div>'
                    f'<div class="value">{val}</div><div class="sub">{sub}</div></div>'
                    for lab, val, sub, acc in items)
    html(f'<div class="kpi-grid">{cards}</div>')


def podium(top):
    """top: rows of rank 1-3 (columns model, rank, GPI, RMSE, R2)."""
    cards = ""
    for _, r in top.iterrows():
        cards += (f'<div class="pod{" first" if r["rank"] == 1 else ""}"><div class="rank">Rank {int(r["rank"])}</div>'
                  f'<div class="model">{r.model}</div><div class="author">{escape(author(r.model))}</div>'
                  f'<div class="stats"><span>GPI <b>{r.GPI:.2f}</b></span><span>RMSE <b>{r.RMSE:.2f}</b></span>'
                  f'<span>R² <b>{r.R2:.2f}</b></span></div></div>')
    html(f'<div class="podium">{cards}</div>')


def flow(steps):
    parts = []
    for i, (title, desc) in enumerate(steps, 1):
        parts.append(f'<div class="step"><div class="n">STEP {i}</div><div class="t">{title}</div><div class="d">{desc}</div></div>')
    html('<div class="flow">' + '<div class="arrow">→</div>'.join(parts) + '</div>')


def stepper(names, current):
    cells = "".join(f'<div class="s {"done" if i < current else "now" if i == current else ""}">'
                    f'{"✓" if i < current else i + 1}&nbsp; {n}</div>' for i, n in enumerate(names))
    html(f'<div class="stepper">{cells}</div>')


def checks(messages):
    icon = {"ok": "✓", "info": "i", "warning": "!", "error": "✕"}
    html("".join(f'<div class="check {lvl}"><span class="i">{icon[lvl]}</span>{escape(text)}</div>'
                 for lvl, text in messages))


def unavailable(body):
    html(f'<div class="unavailable"><div class="h">Reference data unavailable for this analysis.</div>'
         f'<div class="b">{body}</div></div>')


def note(text):
    html(f'<div class="note">{text}</div>')


def footer():
    html('<div class="footer">Solar Radiation Model Explorer · method after Karale, Misra, Ghosh &amp; Latwal (2026) · '
         'reference radiation = Ångström–Prescott from sunshine hours, not measured radiation.</div>')


# ---------------------------------------------------------------- pickers (same everywhere)
def period_picker(key, default="Annual"):
    return st.segmented_control("Period", PERIODS, default=default, key=key) or default


def metric_picker(key, default="GPI"):
    return st.segmented_control("Metric", METRICS, default=default, key=key, format_func=label) or default


def chart(fig, key):
    fig.update_layout(font_family=S.FONT, hoverlabel_font_family=S.FONT)
    st.plotly_chart(fig, config=S.PLOTLY_CONFIG, key=key, width="stretch")


# ---------------------------------------------------------------- charts
def metric_bar(table, metric):
    """All 16 models in GPI-rank order; Top 3 in the accent colour, rank 1 darkest."""
    t = table.sort_values("rank", ascending=False)               # rank 1 at the top
    colors = [S.ACCENT_DARK if r == 1 else S.ACCENT if r <= 3 else S.NEUTRAL_BAR for r in t["rank"]]
    text = [f"{v:.2f}" if r <= 3 else "" for v, r in zip(t[metric], t["rank"])]
    fig = go.Figure(go.Bar(
        x=t[metric], y=[f"{m}  ·  #{int(r)}" for m, r in zip(t.model, t["rank"])], orientation="h",
        marker=dict(color=colors, cornerradius=4), text=text, textposition="outside", cliponaxis=False,
        textfont=dict(color=S.INK, size=12),
        customdata=np.stack([t.model.map(author), t.GPI, t.RMSE, t.MAE, t.MBE, t.R2, t["rank"]], axis=-1),
        hovertemplate="<b>%{y}</b> — %{customdata[0]}<br>GPI %{customdata[1]:.3f} · RMSE %{customdata[2]:.2f} · "
                      "MAE %{customdata[3]:.2f}<br>MBE %{customdata[4]:.2f} · R² %{customdata[5]:.3f}<extra></extra>"))
    unit = METRIC_INFO[metric][2]
    fig.update_layout(height=520, bargap=0.28, showlegend=False, margin=dict(l=8, r=40, t=10, b=8),
                      xaxis_title=f"{label(metric)}{' (' + unit + ')' if unit else ''} — {METRIC_INFO[metric][1]}")
    fig.add_vline(x=0, line_width=1, line_color=S.BORDER)
    return fig


def _heatmap(z, x, y, text, colorscale, zmid=None, reverse=False, hover="", height=None, zfmt=".2f"):
    fig = go.Figure(go.Heatmap(
        z=z, x=x, y=y, text=text, texttemplate="%{text}", textfont=dict(size=11),
        colorscale=colorscale, reversescale=reverse, zmid=zmid, xgap=2, ygap=2,
        colorbar=dict(thickness=10, outlinewidth=0, len=0.8),
        hovertemplate=hover or f"%{{y}} · %{{x}}<br>%{{z:{zfmt}}}<extra></extra>", hoverongaps=False))
    fig.update_layout(height=height or 36 * len(y) + 80, margin=dict(l=8, r=8, t=10, b=8),
                      yaxis=dict(autorange="reversed", showgrid=False), xaxis=dict(side="top", showgrid=False))
    return fig


def rank_heatmap(results):
    """Model x period GPI rank for one site (1 = best, darkest)."""
    p = results.pivot_table(index="model", columns="period", values="rank").reindex(index=MODELS, columns=PERIODS)
    text = p.map(lambda v: "" if pd.isna(v) else f"{int(v)}")
    blues = [[i / (len(S.BLUES) - 1), c] for i, c in enumerate(S.BLUES)]
    return _heatmap(p.values, PERIODS, MODELS, text.values, blues, reverse=True,
                    hover="%{y} · %{x}<br>GPI rank %{z}<extra></extra>")


def metric_heatmap(pivot, metric):
    """Rows = models, columns = sites or periods; darker = better."""
    blues = [[i / (len(S.BLUES) - 1), c] for i, c in enumerate(S.BLUES)]
    if metric in ("GPI", "MBE"):
        scale, zmid, rev = S.DIVERGING, 0, False
    else:
        scale, zmid, rev = blues, None, metric in ("RMSE", "MAE")
    text = pivot.map(lambda v: "n/a" if pd.isna(v) else f"{v:.2f}")
    return _heatmap(pivot.values, list(pivot.columns), list(pivot.index), text.values, scale, zmid, rev)


def season_lines(results, metric, models):
    fig = go.Figure()
    for i, m in enumerate(models[:3]):
        r = results[results.model == m].set_index("period").reindex(PERIODS)
        fig.add_trace(go.Scatter(x=PERIODS, y=r[metric], name=m, mode="markers",   # periods are categories: no lines
                                 marker=dict(size=13, color=S.SERIES[i], line=dict(width=2, color="white")),
                                 hovertemplate=f"<b>{m}</b> · %{{x}}<br>{label(metric)} %{{y:.3f}}<extra></extra>"))
    unit = METRIC_INFO[metric][2]
    fig.update_layout(height=360, yaxis_title=f"{label(metric)}{' (' + unit + ')' if unit else ''}",
                      hovermode="x unified", margin=dict(l=8, r=8, t=40, b=8), scattermode="group")
    return fig


def obs_pred(days, model):
    """A-P reference vs model estimate (daily), with the 1:1 line."""
    x, y = days.Rs_AP, days[model]
    lim = [0, float(np.nanmax([x.max(), y.max()])) * 1.05]
    fig = go.Figure()
    fig.add_trace(go.Scattergl(x=x, y=y, mode="markers", name=model,
                               marker=dict(size=5, color=S.ACCENT, opacity=0.28, line=dict(width=0)),
                               customdata=days.Date.dt.strftime("%d %b %Y"),
                               hovertemplate="%{customdata}<br>A–P %{x:.2f} · " + model + " %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=lim, y=lim, mode="lines", name="1:1 line",
                             line=dict(color=S.MUTED, width=1.5, dash="dash"), hoverinfo="skip"))
    fig.update_layout(height=440, xaxis_title=f"A–P reference Rs ({UNIT})", yaxis_title=f"{model} estimate ({UNIT})",
                      xaxis_range=lim, yaxis_range=lim, showlegend=True)
    return fig


# ---------------------------------------------------------------- tables
def metrics_table(table):
    t = table.sort_values("rank")
    return pd.DataFrame({"Rank": t["rank"].astype(int), "Model": t.model, "Author": t.model.map(author),
                         "GPI": t.GPI, "RMSE": t.RMSE, "MAE": t.MAE, "MBE": t.MBE, "R²": t.R2, "Days": t.n.astype(int)})


def show_table(df, key):
    fmt = {c: st.column_config.NumberColumn(format="%.3f") for c in ("GPI", "RMSE", "MAE", "MBE", "R²")}
    st.dataframe(df, hide_index=True, width="stretch", key=key, column_config={
        **fmt, "Rank": st.column_config.NumberColumn(width="small"), "Author": st.column_config.TextColumn(width="large")})


# ---------------------------------------------------------------- shared results view
STATUS_TEXT = {"no valid reference data": "No day in this period passed all inclusion rules, so there is no "
                                          "Ångström–Prescott reference to compare the models with.",
               "insufficient days (<30)": "Fewer than 30 valid days in this period — the method needs at least 30."}


def results_view(results, period, metric, key, days=None, unavailable_reason=None):
    """KPIs, Top 3, ranking chart, metric table, seasonal comparison and observed-vs-predicted for one site."""
    table = results[results.period == period]
    status = table.status.iloc[0] if len(table) else "no valid reference data"
    if status != "ok":
        unavailable(unavailable_reason or STATUS_TEXT.get(status, status))
        return
    best = table.sort_values("rank").iloc[0]
    kpis([("Best model", best.model, escape(author(best.model)), True),
          ("GPI", f"{best.GPI:.2f}", "rank-1 score", False),
          ("RMSE", f"{best.RMSE:.2f}", UNIT, False),
          ("R²", f"{best.R2:.2f}", "1 − SSE/SST", False),
          ("Days evaluated", f"{int(best.n):,}", period, False)])
    st.markdown("### Top 3 models")
    podium(table[table["rank"] <= 3].sort_values("rank"))

    tabs = st.tabs(["Ranking", "All metrics", "Seasonal comparison", "Observed vs predicted"])
    with tabs[0]:
        st.caption(f"{label(metric)} of all 16 models, ordered by GPI rank (Top 3 highlighted). "
                   f"{label(metric)}: {METRIC_INFO[metric][1]}.")
        chart(metric_bar(table, metric), f"{key}_bar")
    with tabs[1]:
        st.caption("All four indicators and the GPI. The GPI combines them; see Methodology.")
        show_table(metrics_table(table), f"{key}_table")
    with tabs[2]:
        st.caption("GPI rank of every model in every period (1 = best, darker = better).")
        chart(rank_heatmap(results), f"{key}_rankmap")
        top = list(table.sort_values("rank").model[:3])
        chosen = st.multiselect("Compare models across periods (max 3)", MODELS, default=top,
                                max_selections=3, key=f"{key}_lines")
        if chosen:
            chart(season_lines(results, metric, chosen), f"{key}_season")
    with tabs[3]:
        if days is None:
            note("Daily values are not part of the public demo (raw IMD data are not redistributed). "
                 "Upload your own data to see this chart.")
        else:
            sel = days[days.used] if period == "Annual" else days[days.used & (days.Season == period)]
            m = st.selectbox("Model", MODELS, index=MODELS.index(best.model), key=f"{key}_op")
            st.caption(f"Each dot is one day ({len(sel):,} days). Dots on the dashed line = perfect agreement.")
            chart(obs_pred(sel, m), f"{key}_scatter")
