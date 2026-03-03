import streamlit as st
from supabase import create_client

SUPABASE_URL: str = st.secrets["SUPABASE_URL"]
SUPABASE_KEY: str = st.secrets["SUPABASE_KEY"]
SERPAPI_KEY: str = st.secrets["SERPAPI_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
