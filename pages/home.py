import streamlit as st
from time import time
import requests
import json
from utilitarios import *
import pandas as pd
import numpy as np
from utilitarios import validar_email, logotipo

# Configuração da página
st.set_page_config(
    page_title="home",
    page_icon="🏠",
    layout="wide"
)


logo = logotipo()

st.title("🏠 Gerar Conteúdo Base")
st.caption(
    f"É Necessário selecionar o período para gerar o conteúdo base para extração dos dados")

# 🔐 Proteção de rota
if "token" not in st.session_state or not st.session_state.token:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("pages/login.py")
    st.stop()


# Configuração da API
base_rel, headers, pageSize = configurar_api()

# Seleção de datas


col1, col2, col3, col4, col5 = st.columns([1, 0.1, 1, 1, 3])
with col1:
    data_inicial = st.datetime_input(
        "Selecione a data inicial", key="data_inicial")
    data_inicial = str(data_inicial)
    data_hora_inicial = convert_data_hora_para_timestamp(data_inicial)


with col2:
    st.empty()


with col3:
    data_final = st.datetime_input(
        "Selecione a data final", key="data_final")
    data_final = str(data_final)
    data_hora_final = convert_data_hora_para_timestamp(data_final)


with col4:
    st.empty()

with col5:
    st.markdown("<div style='margin-top: 1.7rem;'></div>",
                unsafe_allow_html=True)

    iniciar_relatorio = st.button(
        "Gerar Relatório", use_container_width=True, type="primary")

    link_rel_geral = (
        f"{base_rel}/api/v1/accesslog/logs?"
        f"pageSize={pageSize}&pageNumber=1&sortOrder=desc&sortField=Time"
        f"&dtStart={data_hora_inicial}&dtEnd={data_hora_final}"
    )

st.divider()

if iniciar_relatorio:
    if data_hora_final < data_hora_inicial:
        st.error("A data final deve ser maior que a data inicial.")
        st.stop()
    with st.spinner("🔄 Buscando dados..."):
        df = gerar_relatorio(link_rel_geral, headers)

        if df is not None and not df.empty:
            st.session_state.df_relatorio = df
            st.success(f"✅ Relatório gerado com {len(df)} registros!")
        else:
            st.warning("Nenhum dado encontrado para o período selecionado.")
            # Limpar o DataFrame da sessão se existir
            if "df_relatorio" in st.session_state:
                del st.session_state.df_relatorio

# 🔥 CORREÇÃO: Verificar se df_relatorio existe antes de usar
if "df_relatorio" in st.session_state and st.session_state.df_relatorio is not None:
    df = st.session_state.df_relatorio

    # Métricas
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        st.metric("Total de Registros", len(df))
    with col2:
        if 'personName' in df.columns:
            st.metric("Pessoas Únicas", df['personName'].nunique())
    with col3:
        if 'deviceName' in df.columns:
            st.metric("Dispositivos", df['deviceName'].nunique())
    with col4:
        # Converter timestamp de volta para data
        data_ini = pd.to_datetime(
            data_hora_inicial, unit='s').strftime('%d/%m/%Y')
        data_fim = pd.to_datetime(
            data_hora_final, unit='s').strftime('%d/%m/%Y')
        st.metric("Período", f"{data_ini} **--** {data_fim}")

    st.divider()

    # Exibir DataFrame
    st.subheader("📋 Dados do Relatório")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "time": st.column_config.DatetimeColumn("Data/Hora", format="DD/MM/YYYY HH:mm:ss"),
            "personName": "Nome",
            "eventDescription": "Evento",
            "deviceName": "Dispositivo"
        }
    )

    # 🔥 CORREÇÃO: Só mostrar o número de linhas se o DataFrame existir
    col1, col2 = st.columns([6, 1])
    with col2:
        st.write(f"Linhas: {len(df)}")

    # Botão de download
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv,
            f"relatorio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            use_container_width=True
        )
