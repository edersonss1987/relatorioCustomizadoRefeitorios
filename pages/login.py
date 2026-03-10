import streamlit as st
import requests 
import regex as re
import json
import getpass
import requests as r
import os
from streamlit_theme import st_theme
from utilitarios import validar_email, logotipo
from streamlit_cookies_controller import CookieController



st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)


logo = logotipo()

token = None

# Controle de estado
if "empresas" not in st.session_state:
    st.session_state.empresas = None

if "email" not in st.session_state:
    st.session_state.email = None

if "password" not in st.session_state:
    st.session_state.password = None

if "token" not in st.session_state:
    st.session_state.token = None
 

if token is None:
    
    with st.form('login_form', clear_on_submit=False):

        st.title("🔐 Login", anchor="login")
        st.divider()

        username = st.text_input("E-mail:", placeholder="usuario@dominio.com")
        password = st.text_input("Password", type="password",placeholder="********")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submitted:

            try:
                base = "https://main.idsecure.com.br:5000"
                login_api = f"{base}/api/v1/operators/login"

                if not username or not password:
                    st.error("Preencha usuário e senha.")
                    st.stop()

                if not validar_email(username):
                    st.error("E-mail em formato inválido.")
                    st.stop()

                # Salva na sessão para possível multi-tenant
                st.session_state.email = username
                st.session_state.password = password

                payload = {
                    "email": username,
                    "password": password,
                }

                response = requests.post(login_api, json=payload)

                if response.status_code == 200:

                    content_login = response.json()

                    # 🔹 CASO 1 → LOGIN DIRETO
                    if isinstance(content_login["data"], dict) and "token" in content_login["data"]:

                        token = content_login["data"]["token"]                   
                        
                        st.session_state.token = token
                        

                        st.success("Login realizado com sucesso!")
                        st.switch_page("pages/home.py")
                        

                    # 🔹 CASO 2 → MULTI TENANT
                    elif isinstance(content_login["data"], list):

                        st.session_state.empresas = content_login["data"]

                    else:
                        st.error("Resposta inesperada da API.")

                else:
                    st.error("Usuário ou senha inválidos.")

            except Exception as e:
                st.error(f"Erro ao processar o login: {e}")



# 🔹 TELA DE MULTI-TENANT (fora do form)
if st.session_state.empresas:

    empresas = st.session_state.empresas
    lista_empresas = [item["name"] for item in empresas]

    conta_selecionada = st.selectbox(
        "Selecione a conta",
        ["Selecione a conta"] + lista_empresas
    )

    if conta_selecionada != "Selecione a conta":

        id_tenant = next(
            (item["id"] for item in empresas if item["name"] == conta_selecionada),
            None
        )

        if st.button("Entrar na conta"):

            base = "https://main.idsecure.com.br:5000"
            login_api = f"{base}/api/v1/operators/login"

            payload = {
                "email": st.session_state.email,
                "password": st.session_state.password,
                "tenantId": id_tenant,
            }

            response = r.post(login_api, json=payload)

            if response.status_code == 200:

                content_login = response.json()
                token = content_login["data"]["token"]
                

                st.session_state.token = token
                st.session_state.empresas = None

                st.success("Login realizado com sucesso!")
                st.switch_page("pages/home.py")

            else:
                st.error("Erro ao autenticar empresa.")
                


if st.session_state.token:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("pages/home.py")
    st.stop()
