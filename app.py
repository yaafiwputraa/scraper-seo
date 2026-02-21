import streamlit as st
import pandas as pd
from serpapi import GoogleSearch
from supabase import create_client
from io import BytesIO
import os

# --- KONEKSI SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- KONFIGURASI SERPAPI ---
SERPAPI_KEY = st.secrets["SERPAPI_KEY"]

# --- PAGE CONFIG ---
st.set_page_config(page_title="Google SEO Scraper", page_icon="🔍", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
        /* Background */
        .stApp { background-color: #0e1117; color: #e0e0e0; }

        /* Sidebar & main content */
        section[data-testid="stSidebar"] { background-color: #161b22; }

        /* Input fields */
        input, textarea, select {
            background-color: #1e2530 !important;
            color: #e0e0e0 !important;
            border: 1px solid #30363d !important;
            border-radius: 8px !important;
        }

        /* Header */
        .main-header {
            background: linear-gradient(135deg, #1a237e, #1b5e20);
            padding: 2rem 2.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            color: white;
            border: 1px solid #30363d;
        }
        .main-header h1 { font-size: 2rem; margin: 0; font-weight: 700; }
        .main-header p { margin: 0.3rem 0 0; font-size: 1rem; opacity: 0.85; }

        /* Card */
        .card {
            background: #161b22;
            border-radius: 14px;
            padding: 1.5rem 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            margin-bottom: 1.5rem;
            border: 1px solid #30363d;
        }

        /* Metric box */
        .metric-box {
            background: #0d2818;
            border-left: 5px solid #34A853;
            border-radius: 10px;
            padding: 1rem 1.5rem;
            font-size: 1.05rem;
            font-weight: 600;
            color: #81c995;
            margin-bottom: 1rem;
        }

        /* Section title */
        .section-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #c9d1d9;
            margin-bottom: 0.8rem;
        }

        /* Tombol submit */
        div.stFormSubmitButton > button {
            background: linear-gradient(135deg, #1565c0, #2e7d32);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
            transition: opacity 0.2s;
        }
        div.stFormSubmitButton > button:hover { opacity: 0.85; }

        /* Tombol biasa */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            border: 2px solid #4285F4;
            color: #4285F4;
            background: #0e1117;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background: #1565c0;
            color: white;
            border-color: #1565c0;
        }

        /* Download button */
        div.stDownloadButton > button {
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            width: 100%;
        }
        div.stDownloadButton > button:hover { opacity: 0.85; }

        /* Divider */
        hr { border-color: #30363d; }

        /* Dataframe */
        .stDataFrame { border-radius: 10px; overflow: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="main-header">
        <h1>Google Scraper</h1>
    </div>
""", unsafe_allow_html=True)

# --- FUNGSI SCRAPING ---
def scrape_google(query):
    results = []
    page = 0
    max_pages = 3  # 3 halaman = 30 hasil teratas = 3 kredit per keyword

    while page < max_pages:
        try:
            params = {
                "q": query,
                "start": page * 10,
                "num": 10,
                "hl": "id",
                "gl": "id",
                "api_key": SERPAPI_KEY
            }
            search = GoogleSearch(params)
            data = search.get_dict()

            # Cek error dari SerpAPI
            if "error" in data:
                error_msg = data["error"]
                if "Invalid API key" in error_msg:
                    st.error("❌ SerpAPI Key tidak valid. Cek konfigurasi key kamu.")
                elif "limit" in error_msg.lower():
                    st.error("❌ Limit pencarian SerpAPI habis. Upgrade plan atau tunggu bulan depan.")
                else:
                    st.error(f"❌ SerpAPI Error: {error_msg}")
                break

            organic_results = data.get("organic_results", [])

            if not organic_results:
                break  # Tidak ada hasil lagi, berhenti

            if len(results) >= max_pages * 10:
                break  # Sudah mencapai batas 15 kredit

            for r in organic_results:
                results.append({
                    "keyword": query,
                    "title": r.get("title", ""),
                    "description": r.get("snippet", ""),
                    "url": r.get("link", "")
                })

            page += 1

        except Exception as e:
            error_msg = str(e)
            if "Invalid API key" in error_msg:
                st.error("❌ SerpAPI Key tidak valid. Cek konfigurasi key kamu.")
            elif "rate limit" in error_msg.lower():
                st.error("❌ Limit pencarian SerpAPI habis. Upgrade plan atau tunggu bulan depan.")
            elif "timeout" in error_msg.lower():
                st.error("❌ Koneksi timeout. Cek koneksi internet kamu.")
            else:
                st.error(f"❌ Terjadi kesalahan di halaman {page + 1}: {e}")
            break

    return results

# --- SECTION: PENCARIAN ---
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔎 Cari Kata Kunci</div>', unsafe_allow_html=True)

with st.form(key='search_form'):
    keyword = st.text_input("Kata Kunci", placeholder="Contoh: gohighlevel affiliate", label_visibility="collapsed")
    submit_button = st.form_submit_button(label='Cari dan Simpan Data')

st.markdown('</div>', unsafe_allow_html=True)

# --- LOGIKA SCRAPING ---
if submit_button:
    if not keyword:
        st.warning("⚠️ Silakan masukkan kata kunci terlebih dahulu.")
    else:
        with st.spinner(f"Sedang mengambil data untuk: **{keyword}**..."):
            raw_data = scrape_google(keyword)

            if raw_data:
                try:
                    supabase.table("scraping_results").insert(raw_data).execute()
                except Exception as e:
                    st.warning(f"⚠️ Data berhasil diambil tapi gagal disimpan ke database: {e}")

                df = pd.DataFrame(raw_data)
                df = df[['title', 'description', 'url', 'keyword']]
                df.columns = ['Title', 'Description', 'Url', 'Keyword']

                st.session_state['current_df'] = df
                st.session_state['current_keyword'] = keyword
            else:
                st.error("❌ Tidak ada data yang berhasil diambil.")

# =============================================
# TABEL: HASIL PENCARIAN TERBARU
# =============================================
if 'current_df' in st.session_state:
    df_to_show = st.session_state['current_df']
    kw = st.session_state.get('current_keyword', '')

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Hasil Pencarian Terbaru</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="metric-box">✅ {len(df_to_show)} hasil ditemukan untuk kata kunci: <em>{kw}</em></div>', unsafe_allow_html=True)
    st.dataframe(df_to_show, use_container_width=True, hide_index=True)

    # --- EXPORT & HAPUS DATA ---
    def hapus_semua_data():
        try:
            supabase.table("scraping_results").delete().neq("keyword", "").execute()
        except Exception:
            pass
        if 'current_df' in st.session_state:
            del st.session_state['current_df']
        if 'current_keyword' in st.session_state:
            del st.session_state['current_keyword']

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_to_show.to_excel(writer, index=False, sheet_name='Sheet1')

    st.download_button(
        label="Download Data",
        data=output.getvalue(),
        file_name=f"{kw}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=hapus_semua_data
    )

    st.markdown('</div>', unsafe_allow_html=True)