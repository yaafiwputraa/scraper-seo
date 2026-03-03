import pandas as pd
import streamlit as st

from components.keyword_input import render_keyword_input, reset_keyword_state
from scrapers.google_scraper import scrape_paa
from utils.export import build_filename, df_to_excel

_PREFIX = "paa"


def render() -> None:
    """Render section People Also Ask Scraper."""
    st.divider()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💬 People Also Ask Scraper</div>', unsafe_allow_html=True)

    keywords, search_clicked = render_keyword_input(
        prefix=_PREFIX,
        label="keyword PAA",
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
    progress = st.progress(0, text="Memulai pencarian PAA...")

    for idx, kw in enumerate(keywords):
        progress.progress(idx / len(keywords), text=f"Mencari PAA: **{kw}** ({idx + 1}/{len(keywords)})...")
        all_data.extend(scrape_paa(kw))

    progress.progress(1.0, text="✅ Selesai!")

    if not all_data:
        st.error("❌ Tidak ada PAA yang ditemukan untuk keyword tersebut.")
        return

    st.session_state["paa_df"] = pd.DataFrame(all_data)
    st.session_state["paa_keywords"] = keywords.copy()
    reset_keyword_state(_PREFIX)
    st.rerun()


def _render_results() -> None:
    if "paa_df" not in st.session_state:
        return

    df: pd.DataFrame = st.session_state["paa_df"]
    kws: list[str] = st.session_state.get("paa_keywords", [])
    kw_label = ", ".join(kws)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hasil People Also Ask</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-box">🙋 {len(df)} pertanyaan ditemukan dari {len(kws)} keyword: <em>{kw_label}</em></div>',
        unsafe_allow_html=True,
    )
    st.dataframe(df, use_container_width=True, hide_index=True)

    excel_bytes = df_to_excel(df, sheet_name="People Also Ask")
    file_name = build_filename("paa", kws)

    st.download_button(
        label="⬇️ Download & Hapus Data PAA",
        data=excel_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=_clear_results,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def _clear_results() -> None:
    for key in ("paa_df", "paa_keywords"):
        st.session_state.pop(key, None)
