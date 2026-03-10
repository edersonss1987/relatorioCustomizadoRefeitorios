import streamlit as st

def restore_session():
    # Se existir token na URL e não existir na sessão
    if "token" in st.query_params and not st.session_state.get("token"):
        st.session_state.token = st.query_params["token"]

def save_session(token):
    st.session_state.token = token
    st.query_params["token"] = token

def clear_session():
    st.session_state.clear()
    st.query_params.clear()