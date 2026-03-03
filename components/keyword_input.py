import streamlit as st


def render_keyword_input(prefix: str, label: str = "keyword", max_count: int = 20) -> tuple[list[str], bool]:
    """
    Komponen input keyword yang bisa dipakai ulang di berbagai section.

    Args:
        prefix: Prefix unik untuk namespace session state (misal 'google', 'paa', 'yt').
        label: Label untuk ditampilkan di UI (misal 'keyword', 'keyword PAA').
        max_count: Jumlah maksimal keyword.

    Returns:
        Tuple (keywords, search_clicked):
         - keywords: List keyword yang sudah ditambahkan.
         - search_clicked: True jika tombol cari ditekan dan semua keyword sudah terisi.
    """
    count_key = f"{prefix}_count"
    keywords_key = f"{prefix}_keywords"

    # Inisialisasi session state
    if count_key not in st.session_state:
        st.session_state[count_key] = 1
    if keywords_key not in st.session_state:
        st.session_state[keywords_key] = []

    # Input jumlah keyword
    jumlah = st.number_input(
        f"Berapa {label} yang ingin dicari?",
        min_value=1,
        max_value=max_count,
        value=st.session_state[count_key],
        step=1,
        key=f"{prefix}_jumlah_input",
    )

    if st.session_state[count_key] != jumlah:
        st.session_state[count_key] = jumlah
        st.session_state[keywords_key] = st.session_state[keywords_key][:jumlah]
        st.rerun()

    keywords: list[str] = st.session_state[keywords_key]
    sisa = jumlah - len(keywords)

    st.markdown("<br>", unsafe_allow_html=True)

    # Input tambah keyword
    if sisa > 0:
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            new_kw = st.text_input(
                f"{label.capitalize()} ke-{len(keywords) + 1} dari {jumlah}",
                placeholder="Masukkan kata kunci...",
                key=f"{prefix}_input_{len(keywords)}",
            )
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Tambah", key=f"{prefix}_tambah_btn", use_container_width=True):
                if not new_kw.strip():
                    st.warning("⚠️ Keyword tidak boleh kosong!")
                elif new_kw.strip() in keywords:
                    st.warning("⚠️ Keyword sudah ada di daftar!")
                else:
                    st.session_state[keywords_key].append(new_kw.strip())
                    st.rerun()

    # Tampilkan daftar keyword
    if keywords:
        st.markdown("**Daftar keyword yang sudah ditambahkan:**")
        for i, kw in enumerate(keywords):
            col_num, col_kw, col_del = st.columns([0.3, 6, 1])
            with col_num:
                st.markdown(f"**{i + 1}.**")
            with col_kw:
                st.code(kw, language=None)
            with col_del:
                if st.button("🗑️", key=f"{prefix}_del_{i}", help="Hapus keyword ini"):
                    st.session_state[keywords_key].pop(i)
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    semua_terisi = len(keywords) == jumlah

    if keywords and not semua_terisi:
        st.warning(f"⚠️ Masih kurang {sisa} {label} lagi.")

    search_clicked = st.button(
        "🔍 Mulai Cari",
        disabled=not semua_terisi,
        type="primary",
        use_container_width=True,
        key=f"{prefix}_search_btn",
    )

    return keywords, (search_clicked and semua_terisi)


def reset_keyword_state(prefix: str) -> None:
    """Reset session state keyword setelah search selesai."""
    st.session_state[f"{prefix}_keywords"] = []
    st.session_state[f"{prefix}_count"] = 1
