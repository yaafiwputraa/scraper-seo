import pandas as pd
import streamlit as st

from components.keyword_input import render_keyword_input, reset_keyword_state
from config import supabase
from scrapers.google_scraper import scrape_google
from utils.export import build_filename, df_to_excel

_PREFIX = "google"


def render() -> None:
    """Render section Google Search Scraper."""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔎 Google Search Scraper</div>', unsafe_allow_html=True)

    keywords, search_clicked = render_keyword_input(
        prefix=_PREFIX,
        label="keyword",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Proses scraping ---
    if search_clicked:
        _run_scraping(keywords)

    # --- Tampilkan hasil ---
    _render_results()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _run_scraping(keywords: list[str]) -> None:
    all_data: list[dict] = []
    progress = st.progress(0, text="Memulai pencarian...")

    for idx, kw in enumerate(keywords):
        progress.progress(idx / len(keywords), text=f"Mencari: **{kw}** ({idx + 1}/{len(keywords)})...")
        all_data.extend(scrape_google(kw))

    progress.progress(1.0, text="✅ Selesai!")

    if not all_data:
        st.error("❌ Tidak ada data yang berhasil diambil.")
        return

    # Simpan ke Supabase
    try:
        supabase.table("scraping_results").insert(all_data).execute()
    except Exception as e:
        st.warning(f"⚠️ Data berhasil diambil tapi gagal disimpan ke database: {e}")

    df = pd.DataFrame(all_data)[["title", "description", "url", "keyword"]]
    df.columns = ["Title", "Description", "Url", "Keyword"]

    st.session_state["google_df"] = df
    st.session_state["google_keywords"] = keywords.copy()
    reset_keyword_state(_PREFIX)
    st.rerun()


def _render_results() -> None:
    if "google_df" not in st.session_state:
        return

    df: pd.DataFrame = st.session_state["google_df"]
    kws: list[str] = st.session_state.get("google_keywords", [])
    kw_label = ", ".join(kws)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hasil Pencarian Google</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-box">✅ {len(df)} hasil ditemukan dari {len(kws)} keyword: <em>{kw_label}</em></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    excel_bytes = df_to_excel(df, sheet_name="Sheet1")
    file_name = build_filename("", kws)

    st.download_button(
        label="⬇️ Download & Hapus Data",
        data=excel_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=_clear_results,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def _clear_results() -> None:
    for key in ("google_df", "google_keywords"):
        st.session_state.pop(key, None)
    try:
        supabase.table("scraping_results").delete().neq("keyword", "").execute()
    except Exception:
        pass
