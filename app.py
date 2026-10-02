"""Solar Radiation Model Explorer — Streamlit entry point.

Run locally:  streamlit run app.py
"""
import streamlit as st

st.set_page_config(page_title="Solar Radiation Model Explorer", page_icon=":material/wb_sunny:", layout="wide")

from ui import styles, pages  # noqa: E402  (after set_page_config)

styles.apply()          # light/dark palette from st.session_state["theme"]
styles.theme_toggle()   # sun/moon switch, pinned top-right
pages.NAV.update(
    overview=st.Page(pages.overview, title="Overview", icon=":material/home:", url_path="overview", default=True),
    explorer=st.Page(pages.explorer, title="Model Explorer", icon=":material/insights:", url_path="explorer"),
    upload=st.Page(pages.upload, title="Upload & Analyze", icon=":material/upload_file:", url_path="upload"),
    method=st.Page(pages.methodology, title="Methodology", icon=":material/menu_book:", url_path="methodology"),
)
st.navigation(list(pages.NAV.values()), position="top").run()
