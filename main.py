import streamlit as st
from core.session import restore_session

st.set_page_config(
    page_title="Nutrs Dashboard",
    page_icon="📊",
    layout="wide"
)

# 🔹 CSS GLOBAL
st.markdown("""
    <style>
        .main {
            background-color: #f5f7fa;
        }
        .stButton>button {
            border-radius: 8px;
            height: 40px;
        }
        .block-container {
            padding-top: 3rem;
        }
    </style>
""", unsafe_allow_html=True)

restore_session()

pg = st.navigation([
    st.Page("pages/login.py", title="Login"),
    st.Page("pages/home.py", title="Home"),
    st.Page("pages/dashboard.py", title="Dashboard"),
    st.Page("pages/relatorios.py", title="Relatórios"),
], expanded=False)

pg.run()
