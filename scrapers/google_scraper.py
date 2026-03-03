import streamlit as st
from serpapi import GoogleSearch

from config import SERPAPI_KEY

_MAX_PAGES = 3  # 3 halaman = 30 hasil = 3 kredit per keyword


def scrape_google(query: str) -> list[dict]:
    """
    Ambil hasil pencarian organik Google untuk satu keyword.
    Maks 3 halaman (30 hasil).
    """
    results = []

    for page in range(_MAX_PAGES):
        try:
            params = {
                "q": query,
                "start": page * 10,
                "num": 10,
                "hl": "id",
                "gl": "id",
                "api_key": SERPAPI_KEY,
            }
            data = GoogleSearch(params).get_dict()

            if "error" in data:
                _handle_serpapi_error(data["error"])
                break

            organic = data.get("organic_results", [])
            if not organic:
                break

            for r in organic:
                results.append({
                    "keyword": query,
                    "title": r.get("title", ""),
                    "description": r.get("snippet", ""),
                    "url": r.get("link", ""),
                })

        except Exception as e:
            _handle_exception(e, context=f"halaman {page + 1}")
            break

    return results


def scrape_paa(query: str) -> list[dict]:
    """
    Ambil People Also Ask dari hasil pencarian Google untuk satu keyword.
    """
    results = []

    try:
        params = {
            "q": query,
            "start": 0,
            "num": 10,
            "hl": "id",
            "gl": "id",
            "api_key": SERPAPI_KEY,
        }
        data = GoogleSearch(params).get_dict()

        if "error" in data:
            _handle_serpapi_error(data["error"])
            return results

        for paa in data.get("related_questions", []):
            question = paa.get("question", "")

            snippets = []
            for block in paa.get("text_blocks", []):
                if block.get("type") == "paragraph" and block.get("snippet"):
                    snippets.append(block["snippet"])
                elif block.get("type") == "list":
                    for item in block.get("list", []):
                        if item.get("snippet"):
                            snippets.append(f"- {item['snippet']}")

            results.append({
                "Keyword": query,
                "Question": question,
                "Answer": " ".join(snippets),
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


def _handle_exception(e: Exception, context: str = "") -> None:
    msg = str(e)
    location = f" di {context}" if context else ""
    if "Invalid API key" in msg:
        st.error("❌ SerpAPI Key tidak valid. Cek konfigurasi key kamu.")
    elif "rate limit" in msg.lower():
        st.error("❌ Limit pencarian SerpAPI habis. Upgrade plan atau tunggu bulan depan.")
    elif "timeout" in msg.lower():
        st.error("❌ Koneksi timeout. Cek koneksi internet kamu.")
    else:
        st.error(f"❌ Terjadi kesalahan{location}: {e}")
