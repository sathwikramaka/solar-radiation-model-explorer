"""Visual identity: colours, fonts, page CSS and the Plotly chart template."""
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# Colour roles (validated reference palette; one accent hue, everything else neutral)
INK, INK_2, MUTED = "#16161a", "#52514e", "#8a8984"
SURFACE, CARD, BORDER, GRID = "#fbfaf8", "#ffffff", "#e7e5df", "#eeede8"
ACCENT, ACCENT_DARK, ACCENT_SOFT = "#2a78d6", "#1c5cab", "#e8f1fc"
NEUTRAL_BAR = "#cfcdc6"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]                      # max 3 series per chart
BLUES = ["#f3f8fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"]
DIVERGING = [[0, "#c43c3b"], [0.25, "#e88f8e"], [0.5, "#f0efec"], [0.75, "#86b6ef"], [1, "#1c5cab"]]
GOOD, WARN, BAD = "#0c7a0c", "#a86b00", "#c43c3b"

FONT = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"
SERIF = "'Source Serif 4', Georgia, serif"

pio.templates["academic"] = go.layout.Template(layout=dict(
    font=dict(family=FONT, size=13, color=INK_2),
    title=dict(font=dict(family=FONT, size=15, color=INK), x=0, xanchor="left"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    colorway=SERIES,
    xaxis=dict(gridcolor=GRID, zeroline=False, linecolor=BORDER, ticks="", title_font=dict(size=12, color=MUTED)),
    yaxis=dict(gridcolor=GRID, zeroline=False, linecolor=BORDER, ticks="", title_font=dict(size=12, color=MUTED)),
    hoverlabel=dict(bgcolor="white", bordercolor=BORDER, font=dict(family=FONT, size=12, color=INK)),
    legend=dict(orientation="h", y=1.08, x=0, font=dict(size=12, color=INK_2), bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=8, r=8, t=40, b=8),
))
pio.templates.default = "academic"
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap');
html, body, .stApp, p, li, label, input, textarea, button, [data-testid="stMarkdownContainer"] {{ font-family: {FONT}; }}
[data-testid="stIconMaterial"], .material-symbols-rounded {{ font-family: "Material Symbols Rounded" !important; }}
.stApp {{ background: {SURFACE}; }}
.block-container {{ max-width: 1180px; padding-top: 4.2rem; padding-bottom: 4rem; }}
h1, h2, h3 {{ color: {INK}; letter-spacing: -0.01em; }}
h2 {{ font-size: 1.35rem !important; font-weight: 600 !important; margin-top: 1.6rem !important; }}
h3 {{ font-size: 1.05rem !important; font-weight: 600 !important; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ color: {INK_2}; line-height: 1.6; }}
#MainMenu, footer, [data-testid="stDecoration"] {{ visibility: hidden; height: 0; }}

.eyebrow {{ text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 600; color: {ACCENT_DARK}; margin-bottom: .35rem; }}
.page-title {{ font-family: {SERIF}; font-size: 2.35rem; line-height: 1.15; font-weight: 600; color: {INK}; margin: 0 0 .5rem 0; }}
.page-sub {{ font-size: 1.02rem; color: {INK_2}; max-width: 760px; margin-bottom: 1.6rem; line-height: 1.6; }}
.hero {{ background: linear-gradient(135deg, #ffffff 0%, {ACCENT_SOFT} 100%); border: 1px solid {BORDER};
         border-radius: 18px; padding: 2.4rem 2.4rem 2rem; margin-bottom: 1.6rem; }}
.hero .page-title {{ font-size: 2.7rem; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin: .4rem 0 1.4rem; }}
.kpi {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: 1rem 1.15rem;
        box-shadow: 0 1px 2px rgba(16,16,20,.04); }}
.kpi .label {{ font-size: .74rem; text-transform: uppercase; letter-spacing: .08em; color: {MUTED}; font-weight: 600; }}
.kpi .value {{ font-size: 1.65rem; font-weight: 650; color: {INK}; margin-top: .25rem; font-variant-numeric: tabular-nums; }}
.kpi .sub {{ font-size: .8rem; color: {INK_2}; margin-top: .15rem; }}
.kpi.accent {{ border-color: {ACCENT}; box-shadow: 0 0 0 3px {ACCENT_SOFT}; }}

.podium {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin: .2rem 0 1.2rem; }}
.pod {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: 1.05rem 1.2rem; position: relative; }}
.pod.first {{ border-color: {ACCENT}; box-shadow: 0 0 0 3px {ACCENT_SOFT}; }}
.pod .rank {{ font-size: .72rem; font-weight: 700; letter-spacing: .08em; color: {ACCENT_DARK}; text-transform: uppercase; }}
.pod .model {{ font-family: {SERIF}; font-size: 1.7rem; font-weight: 600; color: {INK}; line-height: 1.2; }}
.pod .author {{ font-size: .82rem; color: {INK_2}; margin-bottom: .55rem; min-height: 2.2em; }}
.pod .stats {{ display: flex; gap: 1rem; font-size: .8rem; color: {MUTED}; font-variant-numeric: tabular-nums; flex-wrap: wrap; }}
.pod .stats b {{ color: {INK}; font-weight: 600; }}

.flow {{ display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px; margin: .6rem 0 1.4rem; }}
.flow .step {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; padding: .65rem .85rem; min-width: 112px; flex: 1 1 112px; }}
.flow .step .n {{ font-size: .68rem; font-weight: 700; color: {ACCENT_DARK}; letter-spacing: .08em; }}
.flow .step .t {{ font-size: .9rem; font-weight: 600; color: {INK}; }}
.flow .step .d {{ font-size: .76rem; color: {MUTED}; line-height: 1.35; margin-top: .15rem; }}
.flow .arrow {{ align-self: center; color: {MUTED}; font-size: 1rem; }}

.chip {{ display: inline-block; font-size: .72rem; font-weight: 600; padding: .15rem .55rem; border-radius: 999px; }}
.chip.ok {{ background: #e6f4e6; color: {GOOD}; }}
.chip.na {{ background: #f4eeee; color: {BAD}; }}
.district-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 1.2rem; }}
.district {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: .95rem 1.05rem; }}
.district .name {{ font-weight: 600; color: {INK}; font-size: 1.02rem; margin-bottom: .2rem; }}
.district .meta {{ font-size: .8rem; color: {MUTED}; margin-top: .35rem; line-height: 1.45; }}

.note {{ background: #fffaf0; border: 1px solid #f1dfb8; border-radius: 12px; padding: .9rem 1.1rem; color: #6b4d00; font-size: .9rem; margin: .4rem 0 1rem; }}
.unavailable {{ background: {CARD}; border: 1px dashed #d9b9b9; border-radius: 14px; padding: 1.4rem 1.5rem; margin: .6rem 0 1rem; }}
.unavailable .h {{ font-weight: 650; color: {BAD}; font-size: 1.05rem; }}
.unavailable .b {{ color: {INK_2}; font-size: .9rem; margin-top: .3rem; }}
.check {{ font-size: .9rem; padding: .18rem 0; color: {INK_2}; }}
.check .i {{ display: inline-block; width: 1.3rem; font-weight: 700; }}
.check.ok .i {{ color: {GOOD}; }} .check.warning .i {{ color: {WARN}; }} .check.error .i {{ color: {BAD}; }} .check.info .i {{ color: {ACCENT}; }}
.check.error {{ color: {BAD}; font-weight: 500; }}

.stepper {{ display: flex; gap: 6px; margin: .2rem 0 1.4rem; flex-wrap: wrap; }}
.stepper .s {{ flex: 1 1 110px; font-size: .78rem; font-weight: 600; color: {MUTED}; padding: .55rem .7rem; border-radius: 10px;
               background: {CARD}; border: 1px solid {BORDER}; }}
.stepper .s.done {{ color: {GOOD}; border-color: #cfe6cf; background: #f5fbf5; }}
.stepper .s.now {{ color: {ACCENT_DARK}; border-color: {ACCENT}; background: {ACCENT_SOFT}; }}
.footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid {BORDER}; font-size: .78rem; color: {MUTED}; }}

[data-testid="stPageLink-NavLink"] {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
    padding: .55rem 1rem; box-shadow: 0 1px 2px rgba(16,16,20,.05); justify-content: center; }}
[data-testid="stPageLink-NavLink"]:hover {{ border-color: {ACCENT}; background: {ACCENT_SOFT}; }}
[data-testid="stPageLink-NavLink"] p {{ font-weight: 600; color: {ACCENT_DARK}; }}
[data-testid="stTabs"] button p {{ font-size: .92rem; font-weight: 500; }}
[data-testid="stExpander"] details {{ border-radius: 12px; border-color: {BORDER}; background: {CARD}; }}
[data-testid="stFileUploaderDropzone"] {{ border-radius: 14px; background: {CARD}; }}
div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {{ border-radius: 10px; font-weight: 500; }}
[data-testid="stBaseButton-primary"] p {{ color: #ffffff !important; }}
@media (max-width: 640px) {{
  .page-title, .hero .page-title {{ font-size: 1.8rem; }}
  .hero {{ padding: 1.5rem 1.2rem; }}
  .flow .arrow {{ display: none; }}
  [data-testid="stButtonGroup"] > div {{ flex-wrap: wrap; row-gap: 6px; }}
}}
</style>
"""


def apply():
    st.markdown(CSS, unsafe_allow_html=True)
