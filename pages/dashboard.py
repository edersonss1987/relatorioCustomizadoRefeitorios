import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import calendar
from utilitarios import logotipo


# Configuração da página
st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)

logo = logotipo()
    
    
# 🔐 Proteção de rota
if "token" not in st.session_state or not st.session_state.token:
    st.warning("Você precisa estar logado para acessar esta página.")
    st.switch_page("pages/login.py")
    st.stop()

# Título da página
st.title("📊 Analítico")
st.caption(
    f"Análise baseada nos dados carregados • {st.session_state.get('email', 'Usuário')}")

# Verificar se existem dados carregados da home
if "df_relatorio" not in st.session_state or st.session_state.df_relatorio is None:
    st.warning(
        "⚠️ Nenhum dado carregado. Vá para a página 'Home' e gere um relatório primeiro.")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🏠 Ir para Home", use_container_width=True, type="primary"):
            st.switch_page("pages/home.py")
    st.stop()

# Carregar dados da sessão
df = st.session_state.df_relatorio.copy()

# ========== PROCESSAMENTO DOS DADOS ==========
with st.spinner("🔄 Processando dados para o dashboard..."):

    df['time'] = pd.to_datetime(
        df['time'], utc=False, dayfirst=True, format='mixed', errors='ignore')

    # Extrair informações de data
    df['ano'] = df['time'].dt.year
    df['mes'] = df['time'].dt.month
    df['mes_ano'] = df['time'].dt.strftime('%Y-%m')
    df['nome_mes'] = df['time'].dt.month_name().map({
        'January': 'Janeiro', 'February': 'Fevereiro', 'March': 'Março',
        'April': 'Abril', 'May': 'Maio', 'June': 'Junho',
        'July': 'Julho', 'August': 'Agosto', 'September': 'Setembro',
        'October': 'Outubro', 'November': 'Novembro', 'December': 'Dezembro'
    })
    df['dia_semana'] = df['time'].dt.day_name().map({
        'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
        'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    })

    df['hora'] = df['time'].dt.hour
    df['dia'] = df['time'].dt.day

    # Separar por tipo de evento
    df_refeicoes = df[df['eventDescription'] == 'AccessGranted'].copy()
    df_nao_identificados = df[df['eventDescription'] == 'NotIdentified'].copy()
    df_desistencias = df[df['eventDescription'] == 'GiveUpAccess'].copy()
    df_refeicoes['groupDescription'] = df['groupDescription'].str.slice(0, 10)

    # Se não houver coluna de empresa, criar uma genérica
    if 'groupDescription' not in df_refeicoes.columns:
        df_refeicoes['groupDescription'] = 'Grupo Principal'
    else:
        df_refeicoes['groupDescription'] = df_refeicoes['groupDescription'].fillna(
            'Não Informado')

    # Calcular totais
    total_eventos = len(df)
    total_refeicoes = len(df_refeicoes)
    total_nao_identificados = len(df_nao_identificados)
    total_desistencias = len(df_desistencias)

    # Calcular períodos
    data_inicio = df['time'].min()
    data_fim = df['time'].max()
    dias_unicos = df['time'].dt.date.nunique()

    # Média diária
    media_diaria = total_refeicoes / dias_unicos if dias_unicos > 0 else 0

    # Taxas
    taxa_aproveitamento = (
        total_refeicoes / total_eventos * 100) if total_eventos > 0 else 0
    taxa_nao_identificados = (
        total_nao_identificados / total_eventos * 100) if total_eventos > 0 else 0
    taxa_desistencias = (total_desistencias /
                         total_eventos * 100) if total_eventos > 0 else 0

    # Mês de maior consumo
    consumo_mensal = df_refeicoes.groupby(
        ['ano', 'mes', 'nome_mes']).size().reset_index(name='quantidade')
    if not consumo_mensal.empty:
        mes_maior_consumo = consumo_mensal.loc[consumo_mensal['quantidade'].idxmax(
        )]
        mes_maior_nome = f"{mes_maior_consumo['nome_mes']}/{int(mes_maior_consumo['ano'])}"
        qtd_mes_maior = mes_maior_consumo['quantidade']
    else:
        mes_maior_nome = "N/A"
        qtd_mes_maior = 0

    # Dia da semana de maior consumo
    consumo_dia_semana = df_refeicoes.groupby(
        'dia_semana').size().reset_index(name='quantidade')
    ordem_dias = ['Segunda', 'Terça', 'Quarta',
                  'Quinta', 'Sexta', 'Sábado', 'Domingo']
    if not consumo_dia_semana.empty:
        consumo_dia_semana['dia_semana'] = pd.Categorical(
            consumo_dia_semana['dia_semana'], categories=ordem_dias, ordered=True)
        consumo_dia_semana = consumo_dia_semana.sort_values('dia_semana')
        dia_maior_consumo = consumo_dia_semana.loc[consumo_dia_semana['quantidade'].idxmax(
        )]
        nome_dia_maior = dia_maior_consumo['dia_semana']
        qtd_dia_maior = dia_maior_consumo['quantidade']
    else:
        nome_dia_maior = "N/A"
        qtd_dia_maior = 0

    # Horários de pico
    consumo_hora = df_refeicoes.groupby(
        'hora').size().reset_index(name='quantidade')
    top_horarios = consumo_hora.nlargest(
        3, 'quantidade') if not consumo_hora.empty else pd.DataFrame()

# ========== LINHA 1: CARDS PRINCIPAIS ==========
st.subheader("📈 Indicadores de Desempenho")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="🍽️ Total de Refeições",
        value=f"{total_refeicoes:,}",
        help="Número total de acessos liberados (refeições servidas)"
    )


with col2:
    st.metric(
        label="📊 Média Diária",
        value=f"{media_diaria:.1f}",
        help="Média de refeições por dia"
    )


with col3:
    st.metric(
        label="📅 Período",
        value=f"{dias_unicos} dias",
        help=f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
    )

st.divider()

# ========== LINHA 2: CARDS DE DESTAQUE ==========
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="📅 Mês de Maior Consumo",
        value=mes_maior_nome,
        delta=f"{qtd_mes_maior:,} refeições",
        delta_color="off"
    )

with col2:
    st.metric(
        label="📆 Dia da Semana de Maior Consumo",
        value=nome_dia_maior,
        delta=f"{qtd_dia_maior:,} refeições",
        delta_color="off"
    )

with col3:
    if not top_horarios.empty:
        horario_pico = f"{int(top_horarios.iloc[0]['hora']):02d}:00"
        st.metric(
            label="⏰ Horário de Pico",
            value=horario_pico,
            delta=f"{int(top_horarios.iloc[0]['quantidade'])} refeições",
            delta_color="off"
        )
    else:
        st.metric(label="⏰ Horário de Pico", value="N/A")

with col4:
    st.metric(
        label="🏢 Empresas",
        value=f"{df_refeicoes['groupDescription'].nunique()}",
        help="Número de empresas diferentes"
    )

st.divider()

# ========== LINHA 4: GRÁFICOS PRINCIPAIS ==========
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 Consumo Mês a Mês")

    if not consumo_mensal.empty:
        consumo_mensal['ordem'] = consumo_mensal['ano'].astype(
            str) + '-' + consumo_mensal['mes'].astype(str).str.zfill(2)
        consumo_mensal = consumo_mensal.sort_values('ordem')
        consumo_mensal['rotulo'] = consumo_mensal['nome_mes'] + \
            '/' + consumo_mensal['ano'].astype(str).str[-2:]

        # GRÁFICO MODERNIZADO - Evolução Mensal
        fig = go.Figure()

        # Adicionar barras com gradiente
        fig.add_trace(go.Bar(
            x=consumo_mensal['rotulo'],
            y=consumo_mensal['quantidade'],
            name='Refeições',
            marker=dict(
                color=consumo_mensal['quantidade'],
                colorscale='Viridis',

            ),
            text=consumo_mensal['quantidade'],
            textposition='outside',
            textfont=dict(size=12, color='#2E86AB'),
            hovertemplate='<b>Mês:</b> %{x}<br><b>Refeições:</b> %{y}<extra></extra>'
        ))

        fig.update_layout(
            title=dict(
                text="Evolução Mensal",
                font=dict(size=18, color='#1E293B')
            ),
            xaxis=dict(
                tickangle=-45,
                # showgrid=False,
                title_font=dict(size=14),
                tickfont=dict(size=11)
            ),
            yaxis=dict(


                # gridwidth=1,
                title_font=dict(size=14),
                tickfont=dict(size=11)
            ),
            hovermode='x unified',

            margin=dict(l=60, r=60, t=80, b=60),
            legend=dict(
                orientation="h",
                y=1.1,
                x=0.5,
                xanchor='center',
                font=dict(size=12)
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados mensais para exibir")

with col2:
    st.subheader("⏰ Distribuição por Hora")

    if not consumo_hora.empty:
        # GRÁFICO MODERNIZADO - Distribuição por Hora
        fig = go.Figure()

        # Área preenchida com gradiente
        fig.add_trace(go.Scatter(
            x=consumo_hora['hora'],
            y=consumo_hora['quantidade'],
            mode='lines+markers',
            name='Refeições',
            line=dict(color='#2E86AB', width=4),

            fill='tozeroy',
            fillcolor='rgba(46, 134, 171, 0.2)',
            hovertemplate='<b>Hora:</b> %{x}:00<br><b>Refeições:</b> %{y}<extra></extra>'
        ))

        # Destacar horários de pico
        for _, row in top_horarios.iterrows():
            fig.add_annotation(
                x=row['hora'],
                y=row['quantidade'],
                text=f"🔥 {int(row['quantidade'])}",
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#F24236',
                font=dict(size=12, color='#F24236', weight='bold'),

                bordercolor='#F24236',
                borderwidth=1,
                borderpad=4
            )

        fig.update_layout(
            title=dict(
                text="Refeições por Hora",
                font=dict(size=18, color='#1E293B')
            ),
            xaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=2,
                showgrid=False,
                title="Hora do Dia"
            ),
            yaxis=dict(

                gridwidth=1,
                title="Número de Refeições"
            ),
            hovermode='x',

            margin=dict(l=60, r=60, t=80, b=60),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados horários para exibir")

st.divider()

# ========== LINHA 5: MAIS GRÁFICOS ==========
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Refeições por Empresa (Top 10)")

    if not df_refeicoes.empty and 'groupDescription' in df_refeicoes.columns:
        consumo_empresa = df_refeicoes.groupby(
            'groupDescription').size().reset_index(name='quantidade')
        consumo_empresa = consumo_empresa.sort_values(
            'quantidade', ascending=False).head(10)
        consumo_empresa['percentual'] = (
            consumo_empresa['quantidade'] / total_refeicoes * 100).round(1)
        consumo_empresa['rotulo'] = consumo_empresa['groupDescription'] + \
            ' (' + consumo_empresa['percentual'].astype(str) + '%)'

        # GRÁFICO MODERNIZADO - Top Empresas
        fig = px.bar(
            consumo_empresa,
            x='quantidade',
            y='groupDescription',
            orientation='h',
            title="Top 10 Empresas com Participação",
            labels={'quantidade': 'Número de Refeições',
                    'groupDescription': 'Empresa'},
            color='quantidade',
            color_continuous_scale='Viridis',
            text='quantidade'
        )

        fig.update_traces(
            textposition='outside',
            textfont=dict(size=11, color='#2E86AB', weight='bold'),
            hovertemplate='<b>%{y}</b><br>Refeições: %{x}<br>Participação: %{customdata}%<extra></extra>',
            customdata=consumo_empresa['percentual']
        )

        fig.update_layout(
            title=dict(
                text="Top 10 Empresas por Refeições",
                font=dict(size=18, color='#1E293B')
            ),
            xaxis=dict(

                gridwidth=1,
                title="Número de Refeições"
            ),
            yaxis=dict(
                showgrid=False,
                categoryorder='total ascending',
                title_font=dict(size=14)
            ),

            margin=dict(l=10, r=10, t=60, b=40),
            coloraxis_showscale=False,
            hoverlabel=dict(font_size=12)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de empresas para exibir")

with col2:
    st.subheader("📆 Refeições por Dia da Semana")

    if not consumo_dia_semana.empty:
        # GRÁFICO MODERNIZADO - Dias da Semana
        cores_dias = {
            'Segunda': '#2E86AB',
            'Terça': '#3A9BC7',
            'Quarta': '#4FB0D9',
            'Quinta': '#65C5EB',
            'Sexta': '#7BDAFF',
            'Sábado': '#F24236',
            'Domingo': '#F5655C'
        }

        cores_lista = [cores_dias[dia]
                       for dia in consumo_dia_semana['dia_semana']]

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=consumo_dia_semana['dia_semana'],
            y=consumo_dia_semana['quantidade'],
            marker_color=cores_lista,
            text=consumo_dia_semana['quantidade'],
            textposition='outside',
            textfont=dict(size=12),
            hovertemplate='<b>%{x}</b><br>Refeições: %{y}<br>%{customdata}<extra></extra>',
            customdata=[
                f"{pct:.1f}% do total" for pct in consumo_dia_semana['quantidade']/total_refeicoes*100]
        ))

        fig.update_layout(
            title=dict(
                text="Distribuição por Dia da Semana",
                font=dict(size=18, color='#1E293B')
            ),
            xaxis=dict(
                showgrid=False,
                title="Dia da Semana"
            ),
            yaxis=dict(

                gridwidth=1,
                title="Número de Refeições"
            ),

            margin=dict(l=10, r=10, t=60, b=40),
            showlegend=False,
            hoverlabel=dict(font_size=12)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de dias da semana para exibir")

st.divider()


# ========== LINHA 7: RANKING E TABELAS ==========
st.subheader("👑 Ranking de Consumo")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🥇 Top 10 Pessoas com Mais Refeições")

    if not df_refeicoes.empty and 'personName' in df_refeicoes.columns:
        top_pessoas = df_refeicoes['personName'].value_counts().head(
            10).reset_index()
        top_pessoas.columns = ['Nome', 'Refeições']

        # Adicionar coluna de percentual
        top_pessoas['% do Total'] = (
            top_pessoas['Refeições'] / total_refeicoes * 100).round(1).astype(str) + '%'

        st.dataframe(
            top_pessoas,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nome": "Nome",
                "Refeições": st.column_config.NumberColumn("Refeições", format="%d"),
                "% do Total": "Participação"
            }
        )
    else:
        st.info("Sem dados de pessoas para exibir")

with col2:
    st.markdown("### 📊 Resumo por Empresa")

    if not df_refeicoes.empty and 'groupDescription' in df_refeicoes.columns:
        resumo_empresa = df_refeicoes.groupby('groupDescription').agg({
            'id': 'count',
            'personName': 'nunique'
        }).reset_index()
        resumo_empresa.columns = ['Empresa', 'Refeições', 'Pessoas Únicas']
        resumo_empresa = resumo_empresa.sort_values(
            'Refeições', ascending=False).head(10)

        # Adicionar percentual
        resumo_empresa['% Refeições'] = (
            resumo_empresa['Refeições'] / total_refeicoes * 100).round(1).astype(str) + '%'

        st.dataframe(
            resumo_empresa,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Empresa": "Empresa",
                "Refeições": st.column_config.NumberColumn("Refeições", format="%d"),
                "Pessoas Únicas": st.column_config.NumberColumn("Pessoas Únicas", format="%d"),
                "% Refeições": "Participação"
            }
        )
    else:
        st.info("Sem dados de empresas para exibir")

st.divider()

# ========== NOVA LINHA: ANÁLISE POR TIPO DE REFEIÇÃO ==========
st.subheader("🍽️ Análise por Tipo de Refeição")

# Processar tipos de refeição
df_tipos = df_refeicoes.copy()

# Classificar por horário
df_tipos['Tipo'] = None
df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('00:01:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('05:29:59').time()), 'Tipo'] = 'Ceia'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('05:30:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('08:30:59').time()), 'Tipo'] = 'Café da Manhã'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('08:31:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('10:49:59').time()), 'Tipo'] = 'Desjejum'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('10:50:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('13:29:59').time()), 'Tipo'] = 'Almoço'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('13:30:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('16:50:59').time()), 'Tipo'] = 'Desjejum Tarde'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('16:51:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('21:29:59').time()), 'Tipo'] = 'Jantar'

df_tipos.loc[(df_tipos['time'].dt.time >= pd.to_datetime('21:30:00').time()) &
             (df_tipos['time'].dt.time <= pd.to_datetime('23:59:59').time()), 'Tipo'] = 'Desjejum Noite'

# Remover linhas sem classificação
df_tipos = df_tipos.dropna(subset=['Tipo'])

# Atribuir valores
df_tipos['Valor'] = 0.0
df_tipos.loc[df_tipos['Tipo'].isin(
    ['Ceia', 'Almoço', 'Jantar']), 'Valor'] = 15.28
df_tipos.loc[df_tipos['Tipo'].isin(
    ['Café da Manhã', 'Desjejum Tarde', 'Desjejum Noite', 'Desjejum']), 'Valor'] = 5.5

# Ordenar tipos
ordem_tipos = ['Ceia', 'Café da Manhã', 'Desjejum', 'Almoço',
               'Desjejum Tarde', 'Jantar', 'Desjejum Noite']
df_tipos['Tipo'] = pd.Categorical(
    df_tipos['Tipo'], categories=ordem_tipos, ordered=True)

# Agrupar por tipo
tipos_agg = df_tipos.groupby('Tipo', observed=True).agg({
    'Tipo': 'count',
    'Valor': 'sum'
}).rename(columns={'Tipo': 'Quantidade'}).reset_index()

# Definir paleta de cores fixa para os tipos
cores_tipos = {
    'Ceia': '#1f77b4',          # Azul
    'Café da Manhã': '#ff7f0e',  # Laranja
    'Desjejum': '#2ca02c',       # Verde
    'Almoço': '#d62728',         # Vermelho
    'Desjejum Tarde': '#9467bd',  # Roxo
    'Jantar': '#8c564b',         # Marrom
    'Desjejum Noite': '#e377c2'  # Rosa
}

# Gráficos lado a lado
col1, col2 = st.columns(2)

with col1:
    # GRÁFICO MODERNIZADO - Quantidade por Tipo (Vertical)
    fig = go.Figure()

    for tipo in tipos_agg['Tipo']:
        dados = tipos_agg[tipos_agg['Tipo'] == tipo].iloc[0]
        fig.add_trace(go.Bar(
            name=tipo,
            x=[tipo],
            y=[dados['Quantidade']],
            marker_color=cores_tipos[tipo],
            text=[dados['Quantidade']],
            textposition='outside',
            textfont=dict(size=12, color='#2E86AB', weight='bold'),
            hovertemplate=f'<b>{tipo}</b><br>Quantidade: %{{y}}<br>Valor: R$ {dados["Valor"]:.2f}<extra></extra>',
            width=0.6
        ))

    fig.update_layout(
        title=dict(
            text="Quantidade por Tipo de Refeição",
            font=dict(size=18, color='#1E293B')
        ),
        xaxis=dict(
            showgrid=False,
            tickangle=-45,
            title_font=dict(size=14)
        ),
        yaxis=dict(

            gridwidth=1,
            title="Número de Refeições"
        ),

        margin=dict(l=10, r=10, t=60, b=80),
        showlegend=False,
        hoverlabel=dict(font_size=12),
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # GRÁFICO MODERNIZADO - Valor por Tipo (Horizontal)
    fig = go.Figure()

    for tipo in tipos_agg['Tipo']:
        dados = tipos_agg[tipos_agg['Tipo'] == tipo].iloc[0]
        fig.add_trace(go.Bar(
            name=tipo,
            y=[tipo],
            x=[dados['Valor']],
            orientation='h',
            marker_color=cores_tipos[tipo],
            text=[f"R$ {dados['Valor']:.2f}"],
            textposition='outside',
            textfont=dict(size=11, color='#F24236', weight='bold'),
            hovertemplate=f'<b>{tipo}</b><br>Valor: R$ %{{x:.2f}}<br>Quantidade: {dados["Quantidade"]}<extra></extra>',
            width=0.6
        ))

    fig.update_layout(
        title=dict(
            text="Valor Total por Tipo de Refeição",
            font=dict(size=18, color='#1E293B')
        ),
        xaxis=dict(

            gridwidth=1,
            title="Valor Total (R$)",
            tickprefix="R$ "
        ),
        yaxis=dict(
            showgrid=False,
            title_font=dict(size=14),
            categoryorder='array',
            categoryarray=ordem_tipos[::-1]  # Inverter para manter ordem
        ),

        margin=dict(l=10, r=10, t=60, b=40),
        showlegend=False,
        hoverlabel=dict(font_size=12),
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)

# Gráfico de barras comparativo (MODERNIZADO)
st.subheader("📊 Comparativo por Tipo")

fig = go.Figure()

# Adicionar barras de quantidade
for tipo in tipos_agg['Tipo']:
    dados = tipos_agg[tipos_agg['Tipo'] == tipo].iloc[0]
    fig.add_trace(go.Bar(
        name=tipo,
        x=[tipo],
        y=[dados['Quantidade']],
        marker_color=cores_tipos[tipo],
        yaxis='y',
        legendgroup=tipo,
        showlegend=True,
        text=[dados['Quantidade']],
        textposition='inside',
        textfont=dict(color='white', weight='bold'),
        hovertemplate=f'<b>{tipo}</b><br>Quantidade: %{{y}}<extra></extra>',
        offsetgroup=0
    ))

# Adicionar barras de valor
for tipo in tipos_agg['Tipo']:
    dados = tipos_agg[tipos_agg['Tipo'] == tipo].iloc[0]
    fig.add_trace(go.Bar(
        name=f"{tipo} (R$)",
        x=[tipo],
        y=[dados['Valor']],
        marker_color=cores_tipos[tipo],
        yaxis='y2',
        legendgroup=tipo,
        showlegend=False,
        text=[f"R$ {dados['Valor']:.2f}"],
        textposition='inside',
        textfont=dict(color='white', weight='bold'),
        hovertemplate=f'<b>{tipo}</b><br>Valor: R$ %{{y:.2f}}<extra></extra>',
        offsetgroup=1
    ))

fig.update_layout(
    title=dict(
        text="Quantidade vs Valor por Tipo de Refeição",
        font=dict(size=18, color='#1E293B')
    ),
    xaxis=dict(
        title="Tipo de Refeição",
        showgrid=False,
        tickangle=-45
    ),
    yaxis=dict(
        title="Quantidade",
        side='left',

        gridwidth=1,
        title_font=dict(color='#2E86AB')
    ),
    yaxis2=dict(
        title="Valor (R$)",
        side='right',
        overlaying='y',
        showgrid=False,
        title_font=dict(color='#F24236'),
        tickprefix="R$ "
    ),
    legend=dict(
        orientation='h',
        y=1.15,
        x=0.5,
        xanchor='center',
        font=dict(size=11),


        borderwidth=1
    ),

    margin=dict(l=60, r=60, t=100, b=80),
    barmode='group',
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)

# Tabela resumo dos tipos (modernizada)
st.subheader("📋 Resumo por Tipo")

# Adicionar coluna de participação percentual
tipos_agg['% Quantidade'] = (
    tipos_agg['Quantidade'] / tipos_agg['Quantidade'].sum() * 100).round(1).astype(str) + '%'
tipos_agg['% Valor'] = (
    tipos_agg['Valor'] / tipos_agg['Valor'].sum() * 100).round(1).astype(str) + '%'

st.dataframe(
    tipos_agg,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Tipo": "Tipo de Refeição",
        "Quantidade": st.column_config.NumberColumn("Quantidade", format="%d"),
        "Valor": st.column_config.NumberColumn("Valor Total", format="R$ %.2f"),
        "% Quantidade": "Participação (Qtd)",
        "% Valor": "Participação (R$)"
    }
)

st.divider()

# ========== LINHA 8: TABELA RESUMO MENSAL ==========
st.subheader("📋 Resumo Mensal Detalhado")

resumo_mensal = df_refeicoes.groupby(['ano', 'nome_mes']).agg({
    'id': 'count',
    'personName': 'nunique',
    'groupDescription': 'nunique'
}).reset_index()

resumo_mensal.columns = ['Ano', 'Mês',
                         'Total Refeições', 'Pessoas Únicas', 'Empresas']
resumo_mensal = resumo_mensal.sort_values(['Ano', 'Mês'])

if not resumo_mensal.empty:
    # Calcular média por pessoa
    resumo_mensal['Média por Pessoa'] = (
        resumo_mensal['Total Refeições'] / resumo_mensal['Pessoas Únicas']).round(1)

    # Adicionar coluna de crescimento
    resumo_mensal['Crescimento'] = resumo_mensal['Total Refeições'].pct_change().mul(
        100).round(1).fillna(0).astype(str) + '%'

    st.dataframe(
        resumo_mensal,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ano": st.column_config.NumberColumn("Ano", format="%d"),
            "Mês": "Mês",
            "Total Refeições": st.column_config.NumberColumn("Total Refeições", format="%d"),
            "Pessoas Únicas": st.column_config.NumberColumn("Pessoas Únicas", format="%d"),
            "Empresas": st.column_config.NumberColumn("Empresas", format="%d"),
            "Média por Pessoa": st.column_config.NumberColumn("Média por Pessoa", format="%.1f"),
            "Crescimento": "Crescimento"
        }
    )
else:
    st.info("Sem dados mensais para exibir")

# ========== LINHA 9: ALERTAS E INSIGHTS ==========
st.divider()


st.markdown("### 📌 Recomendações")
st.markdown("""
- **Horário de pico:** Reforce equipe nos horários de maior movimento
- **Dias de maior movimento:** Ajuste estoque conforme demanda
- **Tipos de refeição:** Analise os mais consumidos para otimizar cardápio
- **Empresas:** Considere programas de fidelidade para as top 5
""")

# ========== BOTÕES DE AÇÃO ==========
st.divider()
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 2])

with col2:
    if st.button("🔄 Atualizar Dashboard", use_container_width=True):
        st.rerun()

with col4:
    # Botão para voltar à home
    if st.button("🏠 Ir para Home", use_container_width=True):
        st.switch_page("pages/home.py")

# ========== FOOTER ==========
st.divider()
st.caption("Nutrs Analytics • Dashboard Completo • Análise Estratégica • Dados atualizados em tempo real")
