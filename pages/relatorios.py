import streamlit as st
import pandas as pd
from datetime import datetime
from utilitarios import logotipo



# Configuração da página
st.set_page_config(
    page_title="relatórios",
    page_icon="📋",
    layout="wide"
)

logo = logotipo()
    

# 🔐 Proteção de rota
if "token" not in st.session_state or not st.session_state.token:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("pages/login.py")
    st.stop()

# Título da página
st.title("📋 Cobrança")
st.caption(
    f"Relatórios detalhados por tipo de refeição • {st.session_state.get('email', 'Usuário')}")

# Verificar se existem dados carregados da home
if "df_relatorio" not in st.session_state or st.session_state.df_relatorio is None:
    st.warning(
        "⚠️ Nenhum dado carregado. Vá para a página 'Home' e gere um relatório primeiro.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Ir para Home", use_container_width=True, type="primary"):
            st.switch_page("pages/home.py")
    st.stop()

# ========== PROCESSAMENTO DOS DADOS ==========
with st.spinner("🔄 Processando dados para relatórios..."):

    # Carregar dados da sessão
    df = st.session_state.df_relatorio.copy()

    # Processamento igual ao seu modelo original
    df = df.sort_values('time')

    # Renomear colunas para português
    df = df.rename(columns={
        'time': 'Data/Hora',
        'personName': 'Nome',
        'eventDescription': 'Autorização',
        'areaName': 'Area',
        'groupDescription': 'Grupos',
        'companyDescription': 'Empresas'
    })

    # Criar colunas de data
    df['Data/Hora'] = pd.to_datetime(
        df['Data/Hora'], utc=False, dayfirst=True, format='mixed', errors='ignore')
    df['Data'] = df['Data/Hora'].dt.date
    df['Mes'] = df['Data/Hora'].dt.month
    df['Dia da semana'] = df['Data/Hora'].dt.day_name()
    df['Hora'] = df['Data/Hora'].dt.hour

    # Selecionar colunas relevantes (igual ao seu modelo)
    colunas_base = ['Data/Hora', 'Data', 'Mes', 'Dia da semana',
                    'Hora', 'Nome', 'Autorização', 'Area', 'Grupos', 'Empresas']

    df['Grupos'] = df['Grupos'].str.slice(0, 10)
    # Manter apenas colunas que existem
    colunas_existentes = [col for col in colunas_base if col in df.columns]
    df = df[colunas_existentes].copy()

    # Filtrar apenas acessos liberados (igual ao seu modelo)
    df = df[df['Autorização'] == 'AccessGranted'].copy()

    # Remover não identificados (igual ao seu modelo)
    df = df[df['Nome'].notna()]

    # ========== CLASSIFICAÇÃO POR TIPO DE REFEIÇÃO ==========
    df['Tipo'] = None

    # Classificar por horário (igual ao seu modelo)
    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('00:01:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('05:29:59').time()), 'Tipo'] = 'Ceia'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('05:30:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('08:30:59').time()), 'Tipo'] = 'Café da Manhã'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('08:31:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('10:49:59').time()), 'Tipo'] = 'Desjejum'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('10:50:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('13:29:59').time()), 'Tipo'] = 'Almoço'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('13:30:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('16:50:59').time()), 'Tipo'] = 'Desjejum Tarde'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('16:51:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('21:29:59').time()), 'Tipo'] = 'Jantar'

    df.loc[(df['Data/Hora'].dt.time >= pd.to_datetime('21:30:00').time()) &
           (df['Data/Hora'].dt.time <= pd.to_datetime('23:59:59').time()), 'Tipo'] = 'Desjejum Noite'

    # Remover linhas sem classificação
    df = df.dropna(subset=['Tipo'])

    # ========== ATRIBUIR VALORES ==========
    df['Valor'] = 1.5  # Valor padrão

    # Valores específicos por tipo (igual ao seu modelo)
    df.loc[df['Tipo'].isin(['Ceia', 'Almoço', 'Jantar']), 'Valor'] = 15.28
    df.loc[df['Tipo'].isin(
        ['Café da Manhã', 'Desjejum Tarde', 'Desjejum Noite', 'Desjejum']), 'Valor'] = 5.5

    # Ordenar tipos para exibição
    ordem_tipos = ['Ceia', 'Café da Manhã', 'Desjejum', 'Almoço',
                   'Desjejum Tarde', 'Jantar', 'Desjejum Noite']

    df['Tipo'] = pd.Categorical(
        df['Tipo'], categories=ordem_tipos, ordered=True)

    # Preencher empresas vazias
    if 'Empresas' in df.columns:
        df['Empresas'] = df['Grupos'].fillna('Não Informado')
    else:
        df['Empresas'] = 'Não Informado'

# ========== RELATÓRIO 1: EXTRATO POR TIPO (IGUAL AO SEU MODELO) ==========
st.subheader("📊 Extrato por Tipo de Refeição")

# Criar extrato (igual ao seu código)
extrato = df[['Tipo', 'Valor']].groupby('Tipo', observed=True).sum()

# Criar DataFrame de contagem
extrato_contagem = df['Tipo'].value_counts().rename('Quantidade')

# Combinar os dois
extrato_completo = pd.DataFrame({
    'Quantidade': extrato_contagem,
    'Valor Total': extrato['Valor']
})

# Reordenar
extrato_completo = extrato_completo.reindex(ordem_tipos)

# Adicionar linha de total
extrato_completo.loc['Soma Final'] = extrato_completo.sum()

# Formatar valores
extrato_display = extrato_completo.copy()
extrato_display['Valor Total'] = extrato_display['Valor Total'].apply(
    lambda x: f'R$ {x:,.2f}')

st.dataframe(
    extrato_display,
    use_container_width=True,
    column_config={
        "Quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
        "Valor Total": "Valor Total"
    }
)

st.divider()

# ========== RELATÓRIO 2: RESUMO POR EMPRESA ==========
st.subheader("🏢 Resumo por Empresa")

# Agrupar por empresa
resumo_empresa = df.groupby('Grupos').agg({
    'Valor': 'sum',
    'Tipo': 'count',
    'Nome': 'nunique'
}).rename(columns={
    'Tipo': 'Total Refeições',
    'Nome': 'Pessoas Únicas'
}).reset_index()

# Adicionar detalhamento por tipo
for tipo in ordem_tipos:
    if tipo in df['Tipo'].values:
        tipo_counts = df[df['Tipo'] == tipo].groupby('Grupos').size()
        resumo_empresa[tipo] = resumo_empresa['Grupos'].map(
            tipo_counts).fillna(0).astype(int)

# Calcular ticket médio
resumo_empresa['Ticket Médio'] = resumo_empresa['Valor'] / \
    resumo_empresa['Total Refeições']

# Ordenar por valor
resumo_empresa = resumo_empresa.sort_values('Valor', ascending=False)

# Adicionar total geral
total_geral = pd.DataFrame({
    'Empresas': ['TOTAL GERAL'],
    'Total Refeições': [resumo_empresa['Total Refeições'].sum()],
    'Valor': [resumo_empresa['Valor'].sum()],
    'Pessoas Únicas': [resumo_empresa['Pessoas Únicas'].sum()],
    'Ticket Médio': [resumo_empresa['Valor'].sum() / resumo_empresa['Total Refeições'].sum()]
})

# Adicionar colunas de tipo com zero para o total
for tipo in ordem_tipos:
    if tipo in resumo_empresa.columns:
        total_geral[tipo] = resumo_empresa[tipo].sum()

resumo_empresa = pd.concat([resumo_empresa, total_geral], ignore_index=True)

# Formatar valores para exibição
resumo_display = resumo_empresa.copy()
resumo_display['Valor'] = resumo_display['Valor'].apply(
    lambda x: f'R$ {x:,.2f}')
resumo_display['Ticket Médio'] = resumo_display['Ticket Médio'].apply(
    lambda x: f'R$ {x:.2f}')

st.dataframe(
    resumo_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Empresas": "Empresa",
        "Total Refeições": st.column_config.NumberColumn("Total", format="%d"),
        "Valor": "Valor Total",
        "Pessoas Únicas": st.column_config.NumberColumn("Pessoas", format="%d"),
        "Ticket Médio": "Ticket Médio",
        **{tipo: st.column_config.NumberColumn(tipo, format="%d") for tipo in ordem_tipos if tipo in resumo_display.columns}
    }
)

st.divider()

# ========== RELATÓRIO 3: DETALHAMENTO POR EMPRESA ==========
st.subheader("🔍 Detalhamento por Empresa")

# Selectbox para escolher empresa
empresas_list = ['Todas'] + list(df['Grupos'].unique())
empresa_selecionada = st.selectbox(
    "Selecione a empresa para ver detalhes", empresas_list)

if empresa_selecionada == 'Todas':
    df_detalhe = df
else:
    df_detalhe = df[df['Grupos'] == empresa_selecionada]

# Criar extrato detalhado por tipo para a empresa selecionada
extrato_detalhe = df_detalhe.groupby('Tipo', observed=True).agg({
    'Valor': 'sum',
    'Tipo': 'count'
}).rename(columns={'Tipo': 'Quantidade'})

extrato_detalhe = extrato_detalhe.reindex(ordem_tipos).dropna()

# Adicionar total
extrato_detalhe.loc['TOTAL'] = extrato_detalhe.sum()

# Formatar
extrato_detalhe_display = extrato_detalhe.copy()
extrato_detalhe_display['Valor'] = extrato_detalhe_display['Valor'].apply(
    lambda x: f'R$ {x:,.2f}')

st.dataframe(
    extrato_detalhe_display,
    use_container_width=True,
    column_config={
        "Quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
        "Valor": "Valor Total"
    }
)

# Mostrar primeiros registros da empresa
with st.expander("📋 Ver primeiros registros da empresa"):
    st.dataframe(
        df_detalhe[['Data/Hora', 'Nome', 'Tipo', 'Valor']].head(50),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Data/Hora": st.column_config.DatetimeColumn("Data/Hora", format="DD/MM/YYYY HH:mm:ss"),
            "Nome": "Nome",
            "Tipo": "Tipo",
            "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
        }
    )

st.divider()

# ========== RELATÓRIO 4: RESUMO MENSAL ==========
st.subheader("📅 Resumo Mensal")

# Criar coluna de mês/ano
df['Mês/Ano'] = df['Data/Hora'].dt.strftime('%m/%Y')

# Resumo mensal por tipo
resumo_mensal = df.groupby(['Mês/Ano', 'Tipo'], observed=True).agg({
    'Valor': 'sum',
    'Tipo': 'count'
}).rename(columns={'Tipo': 'Quantidade'}).reset_index()

# Pivot table para visualização
pivot_mensal = resumo_mensal.pivot_table(
    index='Mês/Ano',
    columns='Tipo',
    values='Quantidade',
    fill_value=0,
    aggfunc='sum'
)

# Reordenar colunas
pivot_mensal = pivot_mensal.reindex(columns=ordem_tipos, fill_value=0)

# Adicionar total
pivot_mensal['Total'] = pivot_mensal.sum(axis=1)

st.dataframe(
    pivot_mensal,
    use_container_width=True,
    column_config={col: st.column_config.NumberColumn(
        col, format="%d") for col in pivot_mensal.columns}
)

st.divider()

# ========== RELATÓRIO 5: EXTRATO FINANCEIRO ==========
st.subheader("💰 Extrato Financeiro")

# Criar extrato financeiro por tipo (igual ao seu modelo)
extrato_financeiro = df[['Tipo', 'Valor']].groupby('Tipo', observed=True).agg({
    'Valor': ['sum', 'count']
}).round(2)

extrato_financeiro.columns = ['Valor Total', 'Quantidade']
extrato_financeiro = extrato_financeiro.reindex(ordem_tipos)

# Adicionar totais
extrato_financeiro.loc['SOMA FINAL'] = extrato_financeiro.sum()

# Formatar
extrato_financeiro_display = extrato_financeiro.copy()
extrato_financeiro_display['Valor Total'] = extrato_financeiro_display['Valor Total'].apply(
    lambda x: f'R$ {x:,.2f}')

st.dataframe(
    extrato_financeiro_display,
    use_container_width=True,
    column_config={
        "Valor Total": "Valor Total",
        "Quantidade": st.column_config.NumberColumn("Quantidade", format="%d")
    }
)

# ========== BOTÕES DE DOWNLOAD ==========
st.divider()

col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

with col1:
    # Download extrato por tipo
    csv_extrato = extrato_completo.to_csv()
    st.download_button(
        "📥 Download Extrato",
        csv_extrato,
        f"extrato_tipos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col2:
    # Download resumo empresas
    csv_empresas = resumo_empresa.to_csv(index=False)
    st.download_button(
        "📥 Download Empresas",
        csv_empresas,
        f"resumo_empresas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col3:
    # Download dados completos
    csv_completo = df.to_csv(index=False)
    st.download_button(
        "📥 Download Completo",
        csv_completo,
        f"dados_completos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        "text/csv",
        use_container_width=True
    )

with col4:
    if st.button("📊 Ir para Dashboard", use_container_width=True):
        st.switch_page("pages/dashboard.py")

with col5:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("pages/home.py")

# ========== FOOTER ==========
st.divider()
st.caption(
    "Nutrs Analytics • Relatórios para Cobrança • Valores sujeitos a alteração")
