import streamlit as st

_CSS = """
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
"""


def inject_css() -> None:
    """Inject custom CSS ke halaman Streamlit."""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_header(title: str = "Google Scraper") -> None:
    """Render header utama aplikasi."""
    st.markdown(
        f'<div class="main-header"><h1>{title}</h1></div>',
        unsafe_allow_html=True,
    )
