import streamlit as st

from components import google_section, paa_section, youtube_section
from styles import inject_css, render_header

st.set_page_config(page_title="SEO Scraper", page_icon="🔍", layout="wide")

inject_css()
render_header("SEO & YouTube Scraper")

google_section.render()
paa_section.render()
youtube_section.render()
