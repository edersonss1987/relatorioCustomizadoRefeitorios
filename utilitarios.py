import re
import requests
import regex as re
import streamlit as st
import json
import datetime
from datetime import datetime
import pandas as pd
import numpy as np
from streamlit_theme import st_theme

#################################################################################################################################################
###############                                     transforma datas                      #######################################################
#################################################################################################################################################


# Conversão de DATA E HORA no formato TIMESTAMP /  # definindo a função que convert TIMESTAMP >> DATA E HORA
def convert_data_hora_para_timestamp(data_hora):
    # Substitua 'data_string' pela sua data e hora no formato 'AAAA-MM-DD HH:MM:SS'
    data_string = data_hora
    formato = '%Y-%m-%d %H:%M:%S'

    # Convertendo a string de data e hora para um objeto datetime
    data_objeto = datetime.strptime(data_string, formato)

#  Convertendo o objeto datetime para timestamp
    timestamp = datetime.timestamp(data_objeto)
    return timestamp


def transformames():
    # criação de colunas para meses
    mesespt = {
        'January': 'Janeiro',
        'February': 'Fevereiro',
        'March': 'Março',
        'April': 'Abril',
        'May': 'Maio',
        'June': 'Junho',
        'July': 'Julho',
        'August': 'Agosto',
        'September': 'Setembro',
        'October': 'Outubro',
        'November': 'Novembro',
        'December': 'Dezembro',
    }
    return mesespt


def transformadia():
    # Criando uma chave com valores, para alteração da lingua conforme datas, meses e dias
    diaspt = {
        'Sunday': 'Domingo',
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado'
    }
    return diaspt


def validar_email(email):
    # Regex para validar e-mails
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None


def selecionar_datas():

    data_inicial = st.datetime_input(
        "Selecione a data inicial", key="data_inicial")
    data_inicial = str(data_inicial)
    data_hora_inicial = convert_data_hora_para_timestamp(data_inicial)

    data_final = st.datetime_input(
        "Selecione a data final", key="data_final")
    data_final = str(data_final)
    data_hora_final = convert_data_hora_para_timestamp(data_final)

    if data_hora_final < data_hora_inicial:
        st.error("A data final deve ser maior que a data inicial.")
        st.stop()

    return data_hora_inicial, data_hora_final


# ... (suas outras funções permanecem iguais) ...


@st.cache_data(show_spinner=True)
def gerar_relatorio(link, headers):
    """
    Busca dados da API e retorna DataFrame
    """
    try:
        response = requests.get(link, headers=headers, timeout=30)

        if response.status_code != 200:
            st.error(f"Erro ao buscar dados: {response.status_code}")
            return None

        dados_json = response.json()

        # Verifica se a resposta tem a estrutura esperada
        if "data" not in dados_json:
            st.error("Formato inesperado da resposta da API.")
            st.json(dados_json)  # Mostra a resposta para debug
            return None

        # Acessa os dados corretamente
        if isinstance(dados_json["data"], dict) and "data" in dados_json["data"]:
            dados = dados_json["data"]["data"]
        elif isinstance(dados_json["data"], list):
            dados = dados_json["data"]
        else:
            dados = dados_json["data"]

        df = pd.DataFrame(dados)
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Erro na requisição: {e}")
        return None
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
        return None


def configurar_api():

    # Base da API
    base_rel = "https://report.idsecure.com.br:5000"

    # Validação do token
    if "token" not in st.session_state or not st.session_state.token:
        st.error("Token não encontrado. Faça login novamente.")
        st.stop()

    token = st.session_state.token

    # Cabeçalho da requisição
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Authorization": f"Bearer {token}"
    }

    pageSize = 5000000

    return base_rel, headers, pageSize


def logotipo():
    
    # Capturar tema atual
    tema = st_theme()
    try:
        
        tema = tema["base"] # Pega o tema base (light ou dark)
    
    except TypeError as e:
        print(f"tema erro {e}")


    # Definir caminho do logo baseado no tema
    if tema == 'dark':
        st.logo('assets/logo_branco.png')
    else:
        st.logo('assets/logo_preto.png')
        
    return tema
        

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)
