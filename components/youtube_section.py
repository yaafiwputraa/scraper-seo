import pandas as pd
import streamlit as st

from components.keyword_input import render_keyword_input, reset_keyword_state
from scrapers.youtube_scraper import scrape_youtube
from utils.export import build_filename, df_to_excel

_PREFIX = "yt"
_DEFAULT_MAX_RESULTS = 20


def render() -> None:
    """Render section YouTube Search Scraper."""
    st.divider()

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">▶️ YouTube Search Scraper</div>', unsafe_allow_html=True)

    max_results = st.slider(
        "Maksimal video per keyword",
        min_value=5,
        max_value=20,
        value=_DEFAULT_MAX_RESULTS,
        step=5,
        key="yt_max_results",
        help="SerpAPI YouTube mengembalikan maks 20 video per request.",
    )

    keywords, search_clicked = render_keyword_input(
        prefix=_PREFIX,
        label="keyword YouTube",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Proses scraping ---
    if search_clicked:
        _run_scraping(keywords, max_results)

    # --- Tampilkan hasil ---
    _render_results()


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _run_scraping(keywords: list[str], max_results: int) -> None:
    all_data: list[dict] = []
    progress = st.progress(0, text="Memulai pencarian YouTube...")

    for idx, kw in enumerate(keywords):
        progress.progress(
            idx / len(keywords),
            text=f"Mencari YouTube: **{kw}** ({idx + 1}/{len(keywords)})...",
        )
        all_data.extend(scrape_youtube(kw, max_results=max_results))

    progress.progress(1.0, text="✅ Selesai!")

    if not all_data:
        st.error("❌ Tidak ada video yang ditemukan untuk keyword tersebut.")
        return

    df = pd.DataFrame(all_data)[["keyword", "title", "link", "channel", "duration", "views", "published_date", "description"]]
    df.columns = ["Keyword", "Title", "Link", "Channel", "Duration", "Views", "Published Date", "Description"]

    st.session_state["yt_df"] = df
    st.session_state["yt_keywords"] = keywords.copy()
    reset_keyword_state(_PREFIX)
    st.rerun()


def _render_results() -> None:
    if "yt_df" not in st.session_state:
        return

    df: pd.DataFrame = st.session_state["yt_df"]
    kws: list[str] = st.session_state.get("yt_keywords", [])
    kw_label = ", ".join(kws)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hasil YouTube Search</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-box">▶️ {len(df)} video ditemukan dari {len(kws)} keyword: <em>{kw_label}</em></div>',
        unsafe_allow_html=True,
    )

    # Tampilkan link yang bisa diklik
    df_display = df.copy()
    df_display["Link"] = df_display["Link"].apply(
        lambda url: f'<a href="{url}" target="_blank">{url}</a>' if url else ""
    )
    st.write(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    excel_bytes = df_to_excel(df, sheet_name="YouTube Results")
    file_name = build_filename("youtube", kws)

    st.download_button(
        label="⬇️ Download & Hapus Data YouTube",
        data=excel_bytes,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=_clear_results,
    )

    st.markdown("</div>", unsafe_allow_html=True)


def _clear_results() -> None:
    for key in ("yt_df", "yt_keywords"):
        st.session_state.pop(key, None)
