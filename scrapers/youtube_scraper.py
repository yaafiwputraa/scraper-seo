import streamlit as st
from serpapi import GoogleSearch

from config import SERPAPI_KEY


def scrape_youtube(query: str, max_results: int = 20) -> list[dict]:
    """
    Ambil judul dan link video YouTube berdasarkan keyword menggunakan SerpAPI.

    Args:
        query: Kata kunci pencarian.
        max_results: Batas maksimal video yang dikembalikan (default 20).

    Returns:
        List of dict berisi data video YouTube.
    """
    results = []

    try:
        params = {
            "engine": "youtube",
            "search_query": query,
            "api_key": SERPAPI_KEY,
        }
        data = GoogleSearch(params).get_dict()

        if "error" in data:
            _handle_serpapi_error(data["error"])
            return results

        for video in data.get("video_results", [])[:max_results]:
            results.append({
                "keyword": query,
                "title": video.get("title", ""),
                "link": video.get("link", ""),
                "channel": video.get("channel", {}).get("name", ""),
                "duration": video.get("length", ""),
                "published_date": video.get("published_date", ""),
                "views": video.get("views", ""),
                "description": video.get("description", ""),
            })

    except Exception as e:
        _handle_exception(e)

    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _handle_serpapi_error(error_msg: str) -> None:
    if "Invalid API key" in error_msg:
        st.error("❌ SerpAPI Key tidak valid. Cek konfigurasi key kamu.")
    elif "limit" in error_msg.lower():
        st.error("❌ Limit pencarian SerpAPI habis. Upgrade plan atau tunggu bulan depan.")
    else:
        st.error(f"❌ SerpAPI Error: {error_msg}")


def _handle_exception(e: Exception) -> None:
    msg = str(e)
    if "Invalid API key" in msg:
        st.error("❌ SerpAPI Key tidak valid. Cek konfigurasi key kamu.")
    elif "rate limit" in msg.lower():
        st.error("❌ Limit pencarian SerpAPI habis. Upgrade plan atau tunggu bulan depan.")
    elif "timeout" in msg.lower():
        st.error("❌ Koneksi timeout. Cek koneksi internet kamu.")
    else:
        st.error(f"❌ Terjadi kesalahan: {e}")
