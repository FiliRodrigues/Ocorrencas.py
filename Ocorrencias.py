# --- Importações e Configurações Iniciais ---
import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import date, timedelta, datetime
import numpy as np

# Corrige a depreciação do tipo np.bool_
array = np.array([True, False, True], dtype=np.bool_)

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard de Ocorrências", layout="wide")


# ====================== BLOCO 1: Função para Configuração de CSS ======================
def aplicar_estilo():
    st.markdown("""
        <style>
        body {
            background-color: #f4f4f4; 
        }
        h1, h2, h3, h4, p {
            font-family: 'Verdana', sans-serif;
            color: #2C3E50;
        }
        .css-18e3th9 {
            padding: 1rem;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
        }
        .stDataFrame {
            border: 1px solid #d3d3d3;
            border-radius: 8px;
        }
        hr {
            border: 1px solid #666;
        }
        .centered-logo img {
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        .card {
            padding: 15px;
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
            font-size: 18px;
            font-weight: bold;
            color: #2C3E50;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

# Aplicar estilo
aplicar_estilo()


# ====================== BLOCO 2: Exibir Logo e Cabeçalho ======================
st.markdown("### Dashboard de Ocorrências Cidade de Paulinia")
st.image("logo.png", width=150)


# ====================== BLOCO 3: Função para Carregar Dados ======================
@st.cache_data
def carregar_dados(file_path):
    return pd.read_excel(file_path, sheet_name='Planilha1')

file_path = "Rel Outubro.xlsx"
df = carregar_dados(file_path)


# ====================== BLOCO 4: Função de Conversão da Duração ======================
def converter_duracao(duracao):
    if isinstance(duracao, str):
        duracao = duracao.strip()
        horas = minutos = 0
        match = re.match(r'(?:(\d+)h)?\s*(\d+)min?', duracao)
        if match:
            if match.group(1):
                horas = int(match.group(1))
            minutos = int(match.group(2))
        return horas * 60 + minutos
    return 0

# Aplicar conversão e ajustes no DataFrame
df['Duração (min)'] = df['Duração'].apply(converter_duracao)
df['Data/Hora inicial'] = pd.to_datetime(df['Data/Hora inicial']).dt.date
df['Guarnição'] = df['Guarnição'].str[:7]
df_reduzido = df[['Data/Hora inicial', 'Guarnição', 'Natureza', 'Endereço do fato', 'Duração (min)']]
df_reduzido['Guarnição'] = df_reduzido['Guarnição'].fillna("Sem Necessidade").astype(str)


# ====================== BLOCO 5: Seção de Resumo Geral ======================
st.markdown("## Visão Geral")
col1, col2, col3 = st.columns(3)
valor_total_atendimentos = df_reduzido.shape[0]
media_duracao_total = df_reduzido['Duração (min)'].mean()

with col1:
    st.markdown(f'<div class="card">Total de Atendimentos: {valor_total_atendimentos}</div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="card">Média de Duração (min): {media_duracao_total:.2f}</div>', unsafe_allow_html=True)
with col3:
    top_natureza = df_reduzido['Natureza'].value_counts().idxmax()
    st.markdown(f'<div class="card">Natureza Mais Frequente: {top_natureza}</div>', unsafe_allow_html=True)


# ====================== BLOCO 6: Visão Geral - Totais de Atendimentos ======================
tabs = st.tabs(["Visão Geral", "Filtros e Relatórios"])
with tabs[0]:
    st.markdown("### Totais de Atendimentos")
    
    with st.spinner("Carregando dados..."):
        total_por_natureza = df_reduzido.groupby('Natureza').size().reset_index(name='Total de Ocorrências').sort_values(by='Total de Ocorrências', ascending=False)
        total_por_viatura_completo = df_reduzido.groupby('Guarnição').size().reset_index(name='Total de Atendimentos').sort_values(by='Total de Atendimentos', ascending=False)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card">Total de Atendimentos por Natureza</div>', unsafe_allow_html=True)
        st.dataframe(total_por_natureza.style.format({"Total de Ocorrências": "{:.0f}"}), height=450)

    with col2:
        st.markdown('<div class="card">Total de Atendimentos por Viatura</div>', unsafe_allow_html=True)
        st.dataframe(total_por_viatura_completo, height=450)


# ====================== BLOCO 8: Gráfico de Atendimentos por Dia ======================
st.markdown("### Atendimentos Diários")

# Garantir que 'Data/Hora inicial' esteja no formato datetime
df_reduzido['Data/Hora inicial'] = pd.to_datetime(df_reduzido['Data/Hora inicial'])

# Agrupar os dados por data e contar as ocorrências
atendimentos_por_dia = df_reduzido.groupby('Data/Hora inicial').size().reset_index(name='Quantidade de Atendimentos').sort_values(by='Data/Hora inicial')

# Adicionar uma coluna para exibir apenas o dia
atendimentos_por_dia['Dia'] = atendimentos_por_dia['Data/Hora inicial'].dt.strftime('%d')

# Criar gráfico de barras
fig_atendimentos_dia = px.bar(
    atendimentos_por_dia,
    x='Data/Hora inicial',
    y='Quantidade de Atendimentos',
    title='Quantidade de Atendimentos por Dia',
    labels={'Data/Hora inicial': 'Data', 'Quantidade de Atendimentos': 'Atendimentos'},
    color='Data/Hora inicial', 
    text=atendimentos_por_dia['Quantidade de Atendimentos']
)

# Atualizar layout e limitar o eixo y a um máximo de 120
fig_atendimentos_dia.update_traces(texttemplate='%{text}', textposition='outside', textfont=dict(size=18))
fig_atendimentos_dia.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title='Data',
    yaxis_title='Quantidade de Atendimentos',
    yaxis=dict(range=[0, 120]),  # Limite do eixo y definido para 120
    title_font_size=20,
    title_font_family='Verdana',
    showlegend=False,
    height=500,
    width=1000,
    xaxis=dict(tickvals=atendimentos_por_dia['Data/Hora inicial'], ticktext=atendimentos_por_dia['Dia'])
)

# Exibir o gráfico
st.plotly_chart(fig_atendimentos_dia, use_container_width=True)



# ====================== BLOCO 9: Filtros de Mês, Natureza e Viatura ======================
st.markdown("### Filtros de Mês, Natureza e Viatura")

# Seleção de Mês Simplificada
st.markdown("#### Selecione o Mês")
meses_disponiveis = sorted(df_reduzido['Data/Hora inicial'].dt.strftime('%Y-%m').unique())
mes_selecionado = st.selectbox("Mês", options=meses_disponiveis, format_func=lambda x: datetime.strptime(x, '%Y-%m').strftime('%B %Y'))

# Converter o mês selecionado para o primeiro e o último dia do mês
ano_mes = datetime.strptime(mes_selecionado, '%Y-%m')
primeiro_dia_mes = ano_mes.replace(day=1)
ultimo_dia_mes = (ano_mes.replace(month=ano_mes.month % 12 + 1, day=1) - timedelta(days=1))

# Filtros de Natureza e Viatura
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Filtrar por Natureza")
    naturezas_ordenadas = ["Todas"] + df_reduzido['Natureza'].value_counts().index.tolist()
    natureza_selecionada = st.selectbox("Escolha uma Natureza", options=naturezas_ordenadas, index=0)

with col2:
    st.markdown("#### Filtrar por Viatura")
    viaturas_disponiveis = ["Todas"] + sorted(df_reduzido['Guarnição'].unique())
    viatura_selecionada = st.selectbox("Escolha uma Viatura", options=viaturas_disponiveis, index=0)

# Aplicar os filtros de Mês, Natureza e Viatura ao DataFrame
ocorrencias_filtradas = df_reduzido[
    (df_reduzido['Data/Hora inicial'] >= primeiro_dia_mes) & 
    (df_reduzido['Data/Hora inicial'] <= ultimo_dia_mes) & 
    (df_reduzido['Natureza'].isin([natureza_selecionada] if natureza_selecionada != "Todas" else df_reduzido['Natureza'].unique())) &
    (df_reduzido['Guarnição'].isin([viatura_selecionada] if viatura_selecionada != "Todas" else df_reduzido['Guarnição'].unique()))
]

# Exibir o Relatório Filtrado com base nos filtros aplicados
st.markdown("### Relatório Filtrado")
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="card">Total de Atendimentos: {len(ocorrencias_filtradas)}</div>', unsafe_allow_html=True)

with col2:
    # Viatura com maior número de atendimentos
    viatura_mais_frequente = ocorrencias_filtradas['Guarnição'].value_counts().idxmax() if not ocorrencias_filtradas.empty else "N/A"
    st.markdown(f'<div class="card">Viatura com Mais Atendimentos: {viatura_mais_frequente}</div>', unsafe_allow_html=True)

with col3:
    # Natureza mais frequente nas ocorrências filtradas
    natureza_mais_frequente = ocorrencias_filtradas['Natureza'].value_counts().idxmax() if not ocorrencias_filtradas.empty else "N/A"
    st.markdown(f'<div class="card">Natureza Mais Frequente: {natureza_mais_frequente}</div>', unsafe_allow_html=True)

# Exibir o DataFrame filtrado com largura aumentada e data formatada como DD/MM
ocorrencias_filtradas['Data/Hora inicial'] = ocorrencias_filtradas['Data/Hora inicial'].dt.strftime('%d/%m')
st.dataframe(ocorrencias_filtradas, height=500, width=1000)

# Mostrar tabela extra de natureza quando apenas uma viatura específica é selecionada e natureza = "Todas"
if natureza_selecionada == "Todas" and viatura_selecionada != "Todas":
    # Agrupar por natureza para a viatura selecionada e exibir o total de ocorrências por natureza
    total_por_natureza_viatura = ocorrencias_filtradas.groupby('Natureza').size().reset_index(name='Total de Ocorrências').sort_values(by='Total de Ocorrências', ascending=False)

    # Exibir tabela adicional ao lado da tabela principal
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="card">Total de Atendimentos por Natureza para a Viatura {viatura_selecionada}</div>', unsafe_allow_html=True)
        st.dataframe(total_por_natureza_viatura.style.format({"Total de Ocorrências": "{:.0f}"}), height=450)


# ====================== BLOCO 10: Gráfico de Atendimentos Diários da Natureza Selecionada ======================
st.markdown("### Gráfico de Atendimentos Diários")

# Filtrar para obter apenas as ocorrências da natureza e viatura selecionadas por dia
atendimentos_diarios = ocorrencias_filtradas.groupby('Data/Hora inicial').size().reset_index(name='Quantidade de Atendimentos')

# Configuração do tamanho da fonte para o texto acima das barras e da legenda
tamanho_fonte_texto = 25  # Ajuste o tamanho da fonte para os valores no topo das barras
tamanho_fonte_legenda = 20  # Ajuste o tamanho da fonte da legenda

# Criar gráfico de barras com cores diferentes para cada barra
fig_natureza_dia = px.bar(
    atendimentos_diarios,
    x='Data/Hora inicial',
    y='Quantidade de Atendimentos',
    title=f'Quantidade de Atendimentos Diários - Natureza: {natureza_selecionada if natureza_selecionada != "Todas" else "Todas"}',
    labels={'Data/Hora inicial': 'Data', 'Quantidade de Atendimentos': 'Atendimentos'},
    color='Data/Hora inicial',
    text='Quantidade de Atendimentos'
)

# Configurações de layout do gráfico
fig_natureza_dia.update_traces(
    texttemplate='%{text}',  # Quantidade de atendimentos no topo
    textposition='outside',
    textfont=dict(size=tamanho_fonte_texto)  # Define o tamanho da fonte do texto acima das barras
)
fig_natureza_dia.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis_title='Data',
    yaxis_title='Quantidade de Atendimentos',
    yaxis=dict(range=[0, 120]),  # Define o limite superior do eixo y para 120
    showlegend=False,  # Ativa a legenda
    width=1000,
    legend=dict(font=dict(size=tamanho_fonte_legenda))  # Define o tamanho da fonte da legenda
)

# Exibir o gráfico
st.plotly_chart(fig_natureza_dia, use_container_width=True)


# ====================== BLOCO 10: Função de Rodapé ======================
def exibir_rodape():
    st.markdown("""
        ---
        **Dashboard de Ocorrências** - Desenvolvido para análise e monitoramento das atividades de guarnição.
        Visualizações detalhadas por Natureza, Viatura, e Período para facilitar decisões estratégicas.
    """)

# Exibir o rodapé
exibir_rodape()
