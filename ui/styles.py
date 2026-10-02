"""Visual identity: light/dark palettes, page CSS, motion and theme-aware Plotly styling.

The theme lives in st.session_state["theme"] ("light" | "dark") for the current session.
Streamlit cannot switch its own theme at runtime, so both palettes are CSS variables and Streamlit
widgets are restyled for dark mode below. Nothing here touches the scientific engine.
"""
import streamlit as st

FONT = "Inter, -apple-system, 'Segoe UI', Roboto, sans-serif"
SERIF = "'Source Serif 4', Georgia, serif"
MONO = "'JetBrains Mono', 'Cascadia Code', Consolas, monospace"

PALETTES = {
    "light": dict(
        bg="#f6f7f9", surface="#ffffff", surface2="#f1f3f7", border="#e2e6ed", grid="#eceff4",
        ink="#111827", ink2="#475467", muted="#7c8799",
        accent="#2a78d6", accent_strong="#1c5cab", accent_soft="rgba(42,120,214,.10)",
        sun="#d98a0b", sun_soft="rgba(229,154,26,.13)",
        good="#13803a", good_soft="rgba(19,128,58,.10)", warn="#a86b00", warn_soft="rgba(168,107,0,.10)",
        bad="#c43c3b", bad_soft="rgba(196,60,59,.09)",
        shadow="0 1px 2px rgba(16,24,40,.04), 0 4px 16px rgba(16,24,40,.05)",
        shadow_hover="0 2px 4px rgba(16,24,40,.06), 0 12px 28px rgba(16,24,40,.09)",
        hero="linear-gradient(135deg,#ffffff 0%,#f3f7fd 55%,#fdf6ea 100%)",
        # chart roles
        series=["#2a78d6", "#eb6834", "#1baf7a"], bar_rest="#d3d8e0", bar_top="#2a78d6", bar_first="#1c5cab",
        ramp=["#f3f8fe", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#1c5cab", "#104281", "#0d366b"],
        diverging=[[0, "#c43c3b"], [0.25, "#e88f8e"], [0.5, "#f0efec"], [0.75, "#86b6ef"], [1, "#1c5cab"]],
        one_to_one="#7c8799",
    ),
    "dark": dict(
        bg="#0e1521", surface="#151e2c", surface2="#1b2636", border="#273347", grid="#223044",
        ink="#e8edf5", ink2="#b3bfd0", muted="#8796ab",
        accent="#5598e7", accent_strong="#86b6ef", accent_soft="rgba(85,152,231,.14)",
        sun="#f2b13c", sun_soft="rgba(242,177,60,.13)",
        good="#4cc26e", good_soft="rgba(76,194,110,.12)", warn="#e0b04a", warn_soft="rgba(224,176,74,.12)",
        bad="#ef7b7a", bad_soft="rgba(239,123,122,.12)",
        shadow="0 1px 2px rgba(0,0,0,.25), 0 6px 20px rgba(0,0,0,.25)",
        shadow_hover="0 2px 6px rgba(0,0,0,.35), 0 14px 32px rgba(0,0,0,.35)",
        hero="linear-gradient(135deg,#151e2c 0%,#16233a 60%,#231f1a 100%)",
        series=["#5598e7", "#e57a4e", "#2fbf8a"], bar_rest="#344257", bar_top="#3987e5", bar_first="#86b6ef",
        ramp=["#1a2433", "#1c3150", "#1f416d", "#23548b", "#2a68aa", "#3a80cc", "#5a99e3", "#86b6ef", "#b7d3f6"],
        diverging=[[0, "#ef7b7a"], [0.25, "#a5555a"], [0.5, "#2b3445"], [0.75, "#3a6fb2"], [1, "#86b6ef"]],
        one_to_one="#8796ab",
    ),
}


def theme():
    return st.session_state.get("theme", "light")


def P():
    """Palette of the current theme."""
    return PALETTES[theme()]


def _vars(p):
    keys = ["bg", "surface", "surface2", "border", "grid", "ink", "ink2", "muted", "accent", "accent_strong",
            "accent_soft", "sun", "sun_soft", "good", "good_soft", "warn", "warn_soft", "bad", "bad_soft",
            "shadow", "shadow_hover", "hero"]
    return "".join(f"--{k.replace('_', '-')}:{p[k]};" for k in keys)


BASE_CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, .stApp, p, li, label, input, textarea, button, [data-testid="stMarkdownContainer"] {{ font-family: {FONT}; }}
[data-testid="stIconMaterial"], .material-symbols-rounded {{ font-family: "Material Symbols Rounded" !important; }}
.stApp, [data-testid="stAppViewContainer"] {{ background: var(--bg); color: var(--ink); }}
header[data-testid="stHeader"] {{ background: color-mix(in srgb, var(--bg) 82%, transparent); backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--border); }}
.block-container {{ max-width: 1200px; padding-top: 4.6rem; padding-bottom: 4rem; }}
h1, h2, h3, h4 {{ color: var(--ink) !important; letter-spacing: -0.012em; }}
h2 {{ font-size: 1.3rem !important; font-weight: 650 !important; margin-top: 2.2rem !important; }}
h3 {{ font-size: 1.04rem !important; font-weight: 600 !important; }}
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {{ color: var(--ink2); line-height: 1.62; }}
[data-testid="stMarkdownContainer"] strong {{ color: var(--ink); }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color: var(--muted) !important; }}
#MainMenu, footer, [data-testid="stDecoration"] {{ visibility: hidden; height: 0; }}
a {{ color: var(--accent); }}

/* icons */
.msi {{ font-family: "Material Symbols Rounded"; font-weight: normal; font-style: normal; font-size: 20px; line-height: 1;
       display: inline-block; vertical-align: middle; letter-spacing: normal; text-transform: none; white-space: nowrap;
       direction: ltr; font-feature-settings: 'liga'; -webkit-font-smoothing: antialiased; }}
.ibadge {{ width: 38px; height: 38px; border-radius: 11px; display: inline-flex; align-items: center; justify-content: center;
          background: var(--accent-soft); color: var(--accent); flex: none; }}
.ibadge.sun {{ background: var(--sun-soft); color: var(--sun); }}
.ibadge.good {{ background: var(--good-soft); color: var(--good); }}
.ibadge.bad {{ background: var(--bad-soft); color: var(--bad); }}
.ibadge.warn {{ background: var(--warn-soft); color: var(--warn); }}

/* motion — short, transform/opacity only, disabled for reduced motion */
@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
@keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
@keyframes indeterminate {{ 0% {{ transform: translateX(-100%); }} 100% {{ transform: translateX(250%); }} }}
.anim {{ animation: fadeUp .5s cubic-bezier(.2,.7,.2,1) both; }}
.kpi-grid > *, .podium > *, .district-grid > *, .card-grid > *, .flow > .step {{ animation: fadeUp .45s cubic-bezier(.2,.7,.2,1) both; }}
.kpi-grid > *:nth-child(2), .podium > *:nth-child(2), .district-grid > *:nth-child(2), .card-grid > *:nth-child(2) {{ animation-delay: .05s; }}
.kpi-grid > *:nth-child(3), .podium > *:nth-child(3), .district-grid > *:nth-child(3), .card-grid > *:nth-child(3) {{ animation-delay: .10s; }}
.kpi-grid > *:nth-child(4), .district-grid > *:nth-child(4), .card-grid > *:nth-child(4) {{ animation-delay: .15s; }}
.kpi-grid > *:nth-child(5), .district-grid > *:nth-child(5), .card-grid > *:nth-child(5) {{ animation-delay: .20s; }}
.kpi-grid > *:nth-child(6), .card-grid > *:nth-child(6) {{ animation-delay: .25s; }}
[data-testid="stPlotlyChart"] {{ animation: fadeIn .6s ease both; }}
@media (prefers-reduced-motion: reduce) {{ *, *::before, *::after {{ animation: none !important; transition: none !important; }} }}

/* hero */
.hero {{ position: relative; overflow: hidden; background: var(--hero); border: 1px solid var(--border); border-radius: 20px;
        padding: 2.6rem 2.6rem 2.2rem; margin-bottom: 1.1rem; box-shadow: var(--shadow); animation: fadeUp .55s ease both; }}
.hero .sunart {{ position: absolute; right: -50px; top: -60px; width: 380px; height: 380px; pointer-events: none; }}
.hero .content {{ position: relative; max-width: 700px; }}
.eyebrow {{ display: inline-flex; align-items: center; gap: .4rem; text-transform: uppercase; letter-spacing: .14em;
           font-size: .7rem; font-weight: 650; color: var(--accent); margin-bottom: .5rem; }}
.eyebrow .msi {{ font-size: 16px; }}
.hero-title {{ font-family: {SERIF}; font-size: 3.05rem; line-height: 1.03; font-weight: 600; color: var(--ink); margin: 0 0 .85rem; letter-spacing: -.015em; }}
.hero-title span {{ color: var(--accent); }}
.hero-sub {{ font-size: 1.06rem; color: var(--ink2); line-height: 1.6; margin-bottom: 1.1rem; max-width: 600px; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.chip {{ display: inline-flex; align-items: center; gap: .35rem; font-size: .78rem; font-weight: 550; padding: .3rem .7rem;
        border-radius: 999px; background: var(--surface); border: 1px solid var(--border); color: var(--ink2); }}
.chip .msi {{ font-size: 16px; color: var(--accent); }}
.chip.ok {{ background: var(--good-soft); border-color: transparent; color: var(--good); }}
.chip.na {{ background: var(--bad-soft); border-color: transparent; color: var(--bad); }}
.chip.ok .msi {{ color: var(--good); }} .chip.na .msi {{ color: var(--bad); }}

/* page header */
.page-head {{ display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 1.4rem; animation: fadeUp .45s ease both; }}
.page-head .ibadge {{ width: 50px; height: 50px; border-radius: 14px; }}
.page-head .ibadge .msi {{ font-size: 27px; }}
.page-title {{ font-family: {SERIF}; font-size: 2.15rem; line-height: 1.15; font-weight: 600; color: var(--ink); margin: 0 0 .3rem; }}
.page-sub {{ font-size: 1rem; color: var(--ink2); max-width: 780px; line-height: 1.6; }}

/* section header */
.sec {{ display: flex; align-items: center; gap: .75rem; margin: 2.4rem 0 .95rem; padding-top: 1.4rem; border-top: 1px solid var(--border); }}
.sec.first {{ border-top: 0; padding-top: 0; margin-top: .9rem; }}
.sec .t {{ font-size: 1.17rem; font-weight: 650; color: var(--ink); letter-spacing: -.01em; line-height: 1.25; }}
.sec .s {{ font-size: .85rem; color: var(--muted); margin-top: .1rem; }}

/* cards */
.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.15rem 1.25rem;
        box-shadow: var(--shadow); transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }}
.card.hover:hover, .kpi:hover, .pod:hover, .district:hover {{ transform: translateY(-2px); box-shadow: var(--shadow-hover); }}
.card-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin: .4rem 0 1.2rem; }}
.card h4 {{ margin: .6rem 0 .3rem; font-size: 1rem; font-weight: 650; }}
.card p, .card li {{ color: var(--ink2); font-size: .87rem; line-height: 1.55; margin: 0; }}
.card ul {{ margin: .2rem 0 0 1.05rem; padding: 0; }}

.kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 14px; margin: .5rem 0 1.4rem; }}
.kpi-grid.c3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
@media (max-width: 900px) {{ .kpi-grid.c3 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.kpi {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1rem 1.1rem;
       box-shadow: var(--shadow); transition: transform .18s ease, box-shadow .18s ease; position: relative; }}
.kpi .top {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; }}
.kpi .label {{ font-size: .71rem; text-transform: uppercase; letter-spacing: .09em; color: var(--muted); font-weight: 650; }}
.kpi .top .msi {{ font-size: 19px; color: var(--muted); }}
.kpi .value {{ font-size: 1.7rem; font-weight: 680; color: var(--ink); margin-top: .35rem; font-variant-numeric: tabular-nums; letter-spacing: -.02em; }}
.kpi .sub {{ font-size: .8rem; color: var(--ink2); margin-top: .1rem; line-height: 1.4; }}
.kpi.accent {{ border-color: color-mix(in srgb, var(--accent) 50%, var(--border)); background:
    linear-gradient(180deg, var(--accent-soft), transparent 75%), var(--surface); }}
.kpi.accent .top .msi {{ color: var(--accent); }}

/* top-3 */
.podium {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; margin: .3rem 0 1.3rem; }}
.pod {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1.15rem 1.2rem 1rem;
       box-shadow: var(--shadow); transition: transform .18s ease, box-shadow .18s ease; position: relative; overflow: hidden; }}
.pod::before {{ content: ""; position: absolute; inset: 0 0 auto 0; height: 3px; background: var(--border); }}
.pod.r1 {{ border-color: color-mix(in srgb, var(--sun) 45%, var(--border)); }}
.pod.r1::before {{ background: linear-gradient(90deg, var(--sun), color-mix(in srgb, var(--sun) 25%, transparent)); }}
.pod.r2::before {{ background: var(--accent); }}
.pod.r3::before {{ background: color-mix(in srgb, var(--accent) 45%, var(--border)); }}
.pod .head {{ display: flex; align-items: center; justify-content: space-between; gap: .5rem; }}
.pod .rank {{ display: inline-flex; align-items: center; gap: .35rem; font-size: .72rem; font-weight: 700; letter-spacing: .09em;
             text-transform: uppercase; color: var(--muted); }}
.pod.r1 .rank {{ color: var(--sun); }}
.pod .rank .msi {{ font-size: 19px; }}
.pod .ctx {{ font-size: .72rem; color: var(--muted); text-align: right; }}
.pod .model {{ font-family: {SERIF}; font-size: 1.9rem; font-weight: 600; color: var(--ink); line-height: 1.15; margin-top: .4rem; }}
.pod .author {{ font-size: .82rem; color: var(--ink2); margin-bottom: .75rem; min-height: 2.3em; line-height: 1.4; }}
.pod .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; border-top: 1px solid var(--border); padding-top: .65rem; }}
.pod .stats div {{ font-size: .66rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }}
.pod .stats b {{ display: block; font-size: .95rem; color: var(--ink); letter-spacing: 0; text-transform: none;
                font-variant-numeric: tabular-nums; font-weight: 620; margin-top: .1rem; }}

/* flow */
.flow {{ display: grid; grid-template-columns: repeat(8, minmax(0, 1fr)); gap: 14px; margin: .6rem 0 1.2rem; }}
@media (max-width: 1050px) {{ .flow {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }} .flow .step:nth-child(4n)::after {{ display: none; }} }}
@media (max-width: 600px) {{ .flow {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} .flow .step:nth-child(2n)::after {{ display: none; }} }}
.flow .step {{ position: relative; background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: .8rem .8rem;
              box-shadow: var(--shadow); }}
.flow .step:not(:last-child)::after {{ content: "›"; position: absolute; right: -11px; top: 50%; transform: translateY(-50%);
              color: var(--muted); font-size: 1.1rem; font-weight: 600; }}
.card-grid.c3 {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
@media (max-width: 900px) {{ .card-grid.c3 {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }} }}
.flow .step .msi {{ font-size: 22px; color: var(--accent); }}
.flow .step .n {{ font-size: .63rem; font-weight: 700; color: var(--muted); letter-spacing: .1em; margin-top: .4rem; }}
.flow .step .t {{ font-size: .9rem; font-weight: 640; color: var(--ink); }}
.flow .step .d {{ font-size: .75rem; color: var(--muted); line-height: 1.35; margin-top: .15rem; }}
.flow .arrow {{ align-self: center; color: var(--muted); }}

/* districts */
.district-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(195px, 1fr)); gap: 12px; margin-bottom: 1.2rem; }}
.district {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 1rem 1.05rem;
            box-shadow: var(--shadow); transition: transform .18s ease, box-shadow .18s ease; }}
.district .name {{ display: flex; align-items: center; gap: .35rem; font-weight: 650; color: var(--ink); font-size: 1.02rem; margin-bottom: .5rem; }}
.district .name .msi {{ font-size: 19px; color: var(--accent); }}
.district .meta {{ font-size: .8rem; color: var(--muted); margin-top: .6rem; line-height: 1.6; }}
.district .meta b {{ color: var(--ink); }}

/* winner matrix */
.matrix-wrap {{ overflow-x: auto; margin: .4rem 0 1.2rem; border-radius: 16px; border: 1px solid var(--border);
               box-shadow: var(--shadow); animation: fadeUp .5s ease both; }}
.matrix {{ width: 100%; border-collapse: collapse; background: var(--surface); font-size: .86rem; }}
.matrix th {{ text-align: left; font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted);
             font-weight: 650; padding: .8rem .95rem; border-bottom: 1px solid var(--border); background: var(--surface2); white-space: nowrap; }}
.matrix th .msi {{ font-size: 16px; margin-right: .3rem; }}
.matrix td {{ padding: .75rem .95rem; border-bottom: 1px solid var(--border); color: var(--ink2); white-space: nowrap; }}
.matrix tr:last-child td {{ border-bottom: 0; }}
.matrix tbody tr:hover td {{ background: var(--surface2); }}
.matrix td.d {{ font-weight: 650; color: var(--ink); }}
.matrix .m1 {{ display: inline-block; font-weight: 700; color: var(--ink); background: var(--sun-soft); border-radius: 6px; padding: .05rem .4rem; }}
.matrix .na {{ color: var(--muted); font-style: italic; }}
.matrix td.eqcell {{ font-family: {MONO}; font-size: .8rem; color: var(--ink); }}
.matrix td.d .msi {{ font-size: 17px; color: var(--accent); margin-right: .25rem; }}

/* model profile */
.model-card {{ display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); gap: 1.4rem; background: var(--surface);
              border: 1px solid var(--border); border-radius: 18px; padding: 1.4rem 1.5rem; box-shadow: var(--shadow);
              margin: .4rem 0 1rem; animation: fadeUp .45s ease both; }}
.model-card .code {{ display: flex; align-items: baseline; gap: .7rem; font-family: {SERIF}; font-size: 2.5rem; font-weight: 600; color: var(--ink); line-height: 1; }}
.model-card .code small {{ font-family: {FONT}; font-size: .78rem; font-weight: 650; color: var(--muted); letter-spacing: .08em; text-transform: uppercase; }}
.model-card .who {{ color: var(--ink2); font-size: .93rem; margin: .4rem 0 .85rem; }}
.model-card .desc {{ color: var(--ink2); font-size: .86rem; line-height: 1.55; margin-top: .3rem; }}
.eq {{ font-family: {MONO}; font-size: .88rem; color: var(--ink); background: var(--surface2); border: 1px solid var(--border);
      border-radius: 12px; padding: .8rem 1rem; margin: .2rem 0 .8rem; overflow-x: auto; white-space: nowrap; }}
.tag {{ display: inline-block; font-size: .7rem; font-weight: 650; padding: .16rem .5rem; border-radius: 6px; margin: 0 .3rem .3rem 0;
       background: var(--surface2); color: var(--ink2); border: 1px solid var(--border); }}
.tag.flag {{ background: var(--warn-soft); color: var(--warn); border-color: transparent; }}
.mstats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; align-content: start; }}
.mstat {{ background: var(--surface2); border-radius: 12px; padding: .7rem .8rem; }}
.mstat .l {{ font-size: .66rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); font-weight: 650; }}
.mstat .v {{ font-size: 1.25rem; font-weight: 680; color: var(--ink); font-variant-numeric: tabular-nums; margin-top: .15rem; }}
.mstat.hi {{ background: var(--accent-soft); }}
.mstat.hi .v {{ color: var(--accent-strong); }}
.mstat.sun {{ background: var(--sun-soft); }}

/* states */
.state {{ display: flex; gap: 1rem; align-items: flex-start; background: var(--surface); border: 1px solid var(--border);
         border-radius: 16px; padding: 1.15rem 1.25rem; margin: .5rem 0 1rem; box-shadow: var(--shadow); animation: fadeUp .4s ease both; }}
.state.error {{ border-color: color-mix(in srgb, var(--bad) 40%, var(--border)); background: linear-gradient(180deg, var(--bad-soft), transparent 85%), var(--surface); }}
.state.ok {{ border-color: color-mix(in srgb, var(--good) 40%, var(--border)); background: linear-gradient(180deg, var(--good-soft), transparent 85%), var(--surface); }}
.state.warn {{ border-color: color-mix(in srgb, var(--warn) 40%, var(--border)); background: linear-gradient(180deg, var(--warn-soft), transparent 85%), var(--surface); }}
.state.empty {{ border-style: dashed; box-shadow: none; background: transparent; }}
.state .h {{ font-weight: 650; color: var(--ink); font-size: 1rem; }}
.state .b {{ color: var(--ink2); font-size: .9rem; margin-top: .25rem; line-height: 1.55; }}
.state .b ul {{ margin: .35rem 0 0 1.1rem; padding: 0; }}
.state .b code {{ font-family: {MONO}; font-size: .82rem; background: var(--surface2); padding: .05rem .3rem; border-radius: 5px; color: var(--ink); }}
.note {{ display: flex; gap: .8rem; align-items: flex-start; background: var(--warn-soft); border: 1px solid transparent; border-radius: 14px;
        padding: .95rem 1.1rem; color: var(--ink2); font-size: .88rem; margin: .4rem 0 1rem; line-height: 1.55; }}
.note .msi {{ color: var(--warn); }}
.note b {{ color: var(--ink); }}
.note.info {{ background: var(--accent-soft); }}
.note.info .msi {{ color: var(--accent); }}
.check {{ display: flex; gap: .55rem; align-items: flex-start; font-size: .9rem; padding: .22rem 0; color: var(--ink2); }}
.check .msi {{ font-size: 18px; margin-top: .05rem; }}
.check.ok .msi {{ color: var(--good); }} .check.warning .msi {{ color: var(--warn); }}
.check.error .msi {{ color: var(--bad); }} .check.info .msi {{ color: var(--accent); }}
.check.error {{ color: var(--bad); font-weight: 550; }}

/* upload */
.dropinfo {{ display: grid; grid-template-columns: auto 1fr; gap: 1.1rem; align-items: start; }}
.dropinfo .ibadge {{ width: 54px; height: 54px; border-radius: 15px; }}
.dropinfo .ibadge .msi {{ font-size: 29px; }}
.dropinfo .h {{ font-weight: 650; font-size: 1.08rem; color: var(--ink); }}
.dropinfo .b {{ color: var(--ink2); font-size: .9rem; margin-top: .2rem; line-height: 1.55; }}
.cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; margin-top: .95rem; }}
.colspec {{ background: var(--surface2); border-radius: 12px; padding: .7rem .8rem; border: 1px solid var(--border); }}
.colspec .k {{ display: flex; align-items: center; gap: .35rem; font-family: {MONO}; font-weight: 600; color: var(--ink); font-size: .88rem; }}
.colspec .k .msi {{ font-size: 17px; color: var(--accent); }}
.colspec .u {{ font-size: .75rem; color: var(--muted); margin-top: .2rem; line-height: 1.4; }}
.progress {{ height: 3px; border-radius: 3px; background: var(--accent-soft); overflow: hidden; margin: .5rem 0 .3rem; }}
.progress::after {{ content: ""; display: block; width: 40%; height: 100%; background: var(--accent); border-radius: 3px;
                   animation: indeterminate 1.1s ease-in-out infinite; }}
.stepper {{ display: flex; gap: 6px; margin: .2rem 0 1.4rem; flex-wrap: wrap; }}
.stepper .s {{ flex: 1 1 120px; display: flex; align-items: center; gap: .45rem; font-size: .8rem; font-weight: 600; color: var(--muted);
              padding: .62rem .75rem; border-radius: 12px; background: var(--surface); border: 1px solid var(--border); transition: all .25s ease; }}
.stepper .s .msi {{ font-size: 18px; }}
.stepper .s.done {{ color: var(--good); border-color: color-mix(in srgb, var(--good) 35%, var(--border)); background: var(--good-soft); }}
.stepper .s.now {{ color: var(--accent); border-color: var(--accent); background: var(--accent-soft); box-shadow: 0 0 0 3px var(--accent-soft); }}
.footer {{ margin-top: 3.2rem; padding-top: 1.1rem; border-top: 1px solid var(--border); font-size: .78rem; color: var(--muted);
          display: flex; gap: .5rem; align-items: center; }}
.footer .msi {{ font-size: 16px; color: var(--sun); }}

/* Streamlit widgets (both themes) */
[data-testid="stPageLink-NavLink"] {{ background: var(--surface); border: 1px solid var(--border); border-radius: 11px;
    padding: .55rem 1.05rem; box-shadow: var(--shadow); justify-content: center; transition: all .18s ease; }}
[data-testid="stPageLink-NavLink"]:hover {{ border-color: var(--accent); background: var(--accent-soft); transform: translateY(-1px); }}
[data-testid="stPageLink-NavLink"] p {{ font-weight: 620; color: var(--accent) !important; }}
[data-testid="stPageLink-NavLink"] [data-testid="stIconMaterial"] {{ color: var(--accent); }}
.st-key-cta_primary [data-testid="stPageLink-NavLink"] {{ background: var(--accent); border-color: var(--accent); }}
.st-key-cta_primary [data-testid="stPageLink-NavLink"] p, .st-key-cta_primary [data-testid="stIconMaterial"] {{ color: #fff !important; }}
.st-key-cta_primary [data-testid="stPageLink-NavLink"]:hover {{ filter: brightness(1.08); background: var(--accent); }}
div[data-testid="stDownloadButton"] button, div[data-testid="stButton"] button {{ border-radius: 11px; font-weight: 550; transition: all .18s ease; }}
div[data-testid="stDownloadButton"] button:hover, div[data-testid="stButton"] button:hover {{ transform: translateY(-1px); }}
[data-testid="stBaseButton-primary"] {{ background: var(--accent) !important; border-color: var(--accent) !important; }}
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{ color: #ffffff !important; }}
[data-testid="stTabs"] button[role="tab"] p {{ font-size: .92rem; font-weight: 560; }}
[data-testid="stExpander"] details {{ border-radius: 14px; border-color: var(--border); background: var(--surface); }}
[data-testid="stFileUploaderDropzone"] {{ border-radius: 16px; background: var(--surface); border: 1.5px dashed color-mix(in srgb, var(--accent) 45%, var(--border));
    padding: 1.5rem; transition: all .18s ease; }}
[data-testid="stFileUploaderDropzone"]:hover {{ background: var(--accent-soft); border-color: var(--accent); }}
[data-testid="stPlotlyChart"] {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 0; overflow: hidden; box-shadow: var(--shadow); }}
[data-testid="stElementContainer"]:has(> [data-testid="stPageLink"]), [data-testid="stPageLink"],
[data-testid="stPageLink"] > div, [data-testid="stPageLink-NavLink"] {{ width: 100% !important; }}
.st-key-ex_filters, .st-key-up_filters {{ background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
    padding: 1rem 1.2rem 1.1rem; box-shadow: var(--shadow); animation: fadeUp .45s ease both; }}
[data-testid="stButtonGroup"] > div {{ flex-wrap: wrap; row-gap: 6px; }}
[data-testid="stButtonGroup"] button {{ transition: background .15s ease, border-color .15s ease; }}
.st-key-theme_toggle {{ position: fixed; top: .55rem; right: 1rem; z-index: 1000001; width: auto !important; }}
.st-key-theme_toggle button {{ border-radius: 999px !important; padding: .2rem .85rem !important; min-height: 2.1rem;
    background: var(--surface) !important; border: 1px solid var(--border) !important; box-shadow: var(--shadow); }}
.st-key-theme_toggle button p, .st-key-theme_toggle [data-testid="stIconMaterial"] {{ color: var(--ink) !important; font-size: .82rem; }}
@media (max-width: 760px) {{
  .hero {{ padding: 1.6rem 1.25rem; }} .hero-title {{ font-size: 2.05rem; }} .hero .sunart {{ opacity: .35; width: 260px; height: 260px; }}
  .page-title {{ font-size: 1.65rem; }} .flow .arrow {{ display: none; }}
  .model-card {{ grid-template-columns: 1fr; }} .pod .stats {{ grid-template-columns: repeat(2, 1fr); }}
  [data-testid="stButtonGroup"] > div {{ flex-wrap: wrap; row-gap: 6px; }}
  .st-key-theme_toggle {{ right: .6rem; }}
}}
"""

# Streamlit draws its widgets with its own (light) theme; in dark mode they are restyled here.
DARK_WIDGETS_CSS = """
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label, .stRadio label p, [data-testid="stCheckbox"] p { color: var(--ink2) !important; }
[data-testid="stTopNavLink"] span, [data-testid="stTopNavLink"] p, [data-testid="stTopNavLink"] [data-testid="stIconMaterial"] { color: var(--ink2) !important; }
[data-testid="stTopNavLink"]:hover { background: var(--surface2) !important; }
[data-testid="stToolbar"] *, [data-testid="stHeader"] [data-testid="stIconMaterial"], [data-testid="stExpandSidebarButton"] * { color: var(--ink2) !important; }
[data-baseweb="select"] > div, [data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"],
[data-testid="stNumberInputContainer"], input, textarea { background: var(--surface2) !important; border-color: var(--border) !important; color: var(--ink) !important; }
[data-baseweb="select"] *, [data-baseweb="input"] input { color: var(--ink) !important; }
.react-aria-ComboBox > div, .react-aria-Select > div { background: var(--surface2) !important; border-color: var(--border) !important; }
.react-aria-ComboBox button, .react-aria-ComboBox svg { background: transparent !important; color: var(--ink2) !important; fill: var(--ink2) !important; }
.react-aria-Popover, .react-aria-ListBox { background: var(--surface) !important; border-color: var(--border) !important; color: var(--ink) !important; }
.react-aria-ListBoxItem, .react-aria-ListBoxItem * { color: var(--ink) !important; }
.react-aria-ListBoxItem[data-focused], .react-aria-ListBoxItem[data-hovered], .react-aria-ListBoxItem[data-selected] { background: var(--surface2) !important; }
[data-testid="stRadio"] .e1mpz0hj4 { box-shadow: 0 0 0 1px var(--muted); }
[data-testid="stRadio"] .e1mpz0hj5 { background: var(--surface) !important; }
[data-testid="stNumberInputStepDown"], [data-testid="stNumberInputStepUp"] { background: var(--surface2) !important; color: var(--ink2) !important; }
input::placeholder, textarea::placeholder { color: var(--muted) !important; }
[data-baseweb="popover"] > div, [data-baseweb="menu"], [data-baseweb="popover"] ul, [role="listbox"] { background: var(--surface) !important; border-color: var(--border) !important; }
[data-baseweb="popover"] li, [role="option"] { color: var(--ink) !important; background: transparent !important; }
[data-baseweb="popover"] li:hover, [role="option"][aria-selected="true"], [role="option"]:hover { background: var(--surface2) !important; }
[data-baseweb="tag"] { background: var(--accent-soft) !important; }
[data-baseweb="tag"] span { color: var(--accent-strong) !important; }
[data-baseweb="tooltip"] > div, [data-baseweb="tooltip"] div, [data-testid="stTooltipContent"] { background: var(--surface2) !important; color: var(--ink) !important; }
[data-testid="stButtonGroup"] button { background: var(--surface2) !important; border-color: var(--border) !important; }
[data-testid="stButtonGroup"] button p, [data-testid="stButtonGroup"] button [data-testid="stIconMaterial"] { color: var(--ink2) !important; }
[data-testid="stButtonGroup"] button:hover { border-color: var(--accent) !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[aria-pressed="true"] {
    background: var(--accent-soft) !important; border-color: var(--accent) !important; }
[data-testid="stButtonGroup"] button[aria-checked="true"] p, [data-testid="stButtonGroup"] button[aria-pressed="true"] p,
[data-testid="stButtonGroup"] button[aria-checked="true"] [data-testid="stIconMaterial"],
[data-testid="stButtonGroup"] button[aria-pressed="true"] [data-testid="stIconMaterial"] { color: var(--accent-strong) !important; }
[data-testid^="stBaseButton-secondary"], [data-testid="stBaseButton-segmented_control"], [data-testid="stBaseButton-pills"] {
    background: var(--surface) !important; border-color: var(--border) !important; color: var(--ink2) !important; }
[data-testid^="stBaseButton-secondary"] p, [data-testid="stBaseButton-segmented_control"] p, [data-testid="stBaseButton-pills"] p,
[data-testid^="stBaseButton-secondary"] [data-testid="stIconMaterial"], [data-testid="stBaseButton-segmented_control"] [data-testid="stIconMaterial"],
[data-testid="stBaseButton-pills"] [data-testid="stIconMaterial"] { color: var(--ink2) !important; }
[data-testid="stBaseButton-segmented_controlActive"], [data-testid="stBaseButton-pillsActive"] {
    background: var(--accent-soft) !important; border-color: var(--accent) !important; }
[data-testid="stBaseButton-segmented_controlActive"] p, [data-testid="stBaseButton-pillsActive"] p,
[data-testid="stBaseButton-segmented_controlActive"] [data-testid="stIconMaterial"], [data-testid="stBaseButton-pillsActive"] [data-testid="stIconMaterial"] { color: var(--accent-strong) !important; }
[data-testid="stTabs"] button[role="tab"] p { color: var(--ink2); }
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p { color: var(--accent-strong); }
[data-baseweb="tab-border"] { background: var(--border) !important; }
[data-baseweb="tab-highlight"] { background: var(--accent) !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p, [data-testid="stExpander"] summary [data-testid="stIconMaterial"] { color: var(--ink) !important; }
[data-testid="stExpander"] summary:hover { background: var(--surface2); }
[data-testid="stFileUploaderDropzoneInstructions"] *, [data-testid="stFileUploaderFile"] *, [data-testid="stFileUploader"] small { color: var(--ink2) !important; }
[data-testid="stFileUploaderFileName"] { color: var(--ink) !important; }
[data-testid="stFileChip"], [data-testid="stTextInputRootElement"] { background: var(--surface2) !important; border-color: var(--border) !important; }
[data-testid="stFileChip"] *, [data-testid="stTextInputRootElement"] input { color: var(--ink) !important; }
[data-testid="stDataFrame"], [data-testid="stTable"] { filter: invert(.9) hue-rotate(180deg); }
.katex, .katex * { color: var(--ink) !important; }
[data-testid="stStatusWidget"] *, [data-testid="stSpinner"] * { color: var(--ink2) !important; }
[data-testid="stAlert"] * { color: var(--ink) !important; }
hr { border-color: var(--border) !important; }
"""


def apply():
    p = P()
    css = f":root{{{_vars(p)}color-scheme:{theme()};}}" + BASE_CSS + (DARK_WIDGETS_CSS if theme() == "dark" else "")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def theme_toggle():
    """Sun/moon switch, pinned top-right; the choice is kept in session_state for this session."""
    dark = theme() == "dark"

    def flip():
        st.session_state["theme"] = "light" if dark else "dark"

    with st.container(key="theme_toggle"):
        st.button("Light" if dark else "Dark", icon=":material/light_mode:" if dark else ":material/dark_mode:",
                  on_click=flip, key="theme_btn", help=f"Switch to {'light' if dark else 'dark'} mode")


# ---------------------------------------------------------------- Plotly
PLOTLY_CONFIG = {"displaylogo": False, "responsive": True, "displayModeBar": "hover",
                 "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d", "toggleSpikelines"],
                 "toImageButtonOptions": {"format": "png", "scale": 2}}


def style_figure(fig):
    """Apply the current theme to a figure (fonts, colours, grid, hover, legend, margins)."""
    p = P()
    m = fig.layout.margin
    fig.update_layout(margin=dict(l=max(m.l or 0, 18), r=max(m.r or 0, 22), t=max(m.t or 0, 18), b=max(m.b or 0, 16)))
    axis = dict(gridcolor=p["grid"], linecolor=p["border"], zeroline=False, automargin=True, ticks="",
                tickfont=dict(color=p["ink2"], size=12), title_font=dict(color=p["muted"], size=12))
    fig.update_layout(
        font=dict(family=FONT, size=13, color=p["ink2"]),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor=p["surface"], bordercolor=p["border"], font=dict(family=FONT, size=12, color=p["ink"])),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=12, color=p["ink2"]), bgcolor="rgba(0,0,0,0)"),
        modebar=dict(bgcolor="rgba(0,0,0,0)", color=p["muted"], activecolor=p["accent"]),
        colorway=p["series"])
    fig.update_xaxes(**axis)
    fig.update_yaxes(**axis)
    fig.update_traces(colorbar=dict(tickfont=dict(color=p["ink2"]), outlinewidth=0, thickness=10),
                      selector=dict(type="heatmap"))
    return fig
