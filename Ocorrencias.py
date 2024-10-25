import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import date, timedelta
import numpy as np

# Substituir np.bool8 por np.bool_
array = np.array([True, False, True], dtype=np.bool_)

# Configuração da página
st.set_page_config(page_title="Dashboard de Ocorrências", layout="wide")

# Estilo CSS atualizado para um design mais atrativo
st.markdown("""
    <style>
    body {
        background-color: #f0f4f8;  /* Cor neutra */
    }
    h1, h2, h3, h4, p {
        font-family: 'Verdana', sans-serif;
        color: #333;  /* Melhor contraste */
    }
    .css-18e3th9 {
        padding: 1rem;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);  /* Sombra sutil */
    }
    .stDataFrame {
        border: 1px solid #d3d3d3;
        border-radius: 8px;
    }
    hr {
        border: 1px solid #666;
    }
    .logo {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .centered-logo img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .sidebar .stCheckbox {
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# Exibir logo centralizada
st.markdown('<div class="centered-logo"><img src="logo.png" width="150"></div>', unsafe_allow_html=True)

# Caminho do arquivo
file_path = "Relatorio 1 a 25.xlsx"

# Carregar os dados do Excel
df = pd.read_excel(file_path, sheet_name='Planilha1')

# Função para converter duração para minutos
def converter_duracao(duracao):
    if isinstance(duracao, str):  # Verifica se é uma string
        duracao = duracao.strip()
        horas = minutos = 0
        match = re.match(r'(?:(\d+)h)?\s*(\d+)min?', duracao)
        if match:
            if match.group(1):
                horas = int(match.group(1))
            minutos = int(match.group(2))
        return horas * 60 + minutos
    return 0  # Retorna 0 se o valor não for uma string (caso seja NaN)


# Aplicar conversões e formatar a data
df['Duração (min)'] = df['Duração'].apply(converter_duracao)
df['Data/Hora inicial'] = pd.to_datetime(df['Data/Hora inicial']).dt.date
df['Guarnição'] = df['Guarnição'].str[:7]  # Manter apenas as 7 primeiras letras da Guarnição

# Selecionar colunas relevantes
colunas_relevantes = ['Data/Hora inicial', 'Guarnição', 'Natureza', 'Endereço do fato']
df_reduzido = df[colunas_relevantes + ['Duração (min)']]

# Exibir o relatório por natureza sempre
st.title("Relatório de Ocorrências Transito Cidade de Paulinia")


# Barra de progresso para carregamento de dados
with st.spinner("Carregando os dados..."):
    total_por_natureza = (
        df_reduzido.groupby('Natureza').size()
        .reset_index(name='Total de Ocorrências')
        .sort_values(by='Total de Ocorrências', ascending=False)
    )

    # Total de atendimentos por viatura para todos os atendimentos
    total_por_viatura_completo = (
        df_reduzido.groupby('Guarnição').size()
        .reset_index(name='Total de Atendimentos')
        .sort_values(by='Total de Atendimentos', ascending=False)
    )

# Calcular o valor total de atendimentos
valor_total_atendimentos = total_por_natureza['Total de Ocorrências'].sum()

# Exibir total de ocorrências por natureza e total de atendimentos por viatura (todos os atendimentos)
col1, col2 = st.columns(2)
with col1:
    st.subheader(f"Total de Atendimentos por Natureza")
    st.subheader(f"Total de atendimentos: {valor_total_atendimentos}")
    st.dataframe(total_por_natureza.style.format({"Total de Ocorrências": "{:.0f}"}), height=450)

with col2:
    st.subheader("Total de Atendimentos por Viatura")
    st.subheader("")
    st.dataframe(total_por_viatura_completo, height=450)


# Linha divisória formal
st.markdown("<hr>", unsafe_allow_html=True)

# --- FILTROS INDEPENDENTES ---

st.sidebar.title("Filtros de Ocorrências")

# Opção de mostrar relatório por Natureza ou Viatura
mostrar_natureza = st.sidebar.checkbox("Filtrar por Natureza")
mostrar_viatura = st.sidebar.checkbox("Filtrar por Viatura")

# --- FILTRO DE NATUREZA ---
if mostrar_natureza:
    # Ordenar as opções do filtro de Natureza do maior para o menor
    naturezas_ordenadas = (
        df_reduzido['Natureza']
        .value_counts()
        .index.tolist()  # Obtem uma lista de naturezas ordenadas por frequência
    )

    # Filtro simples para Natureza
    natureza_selecionada = st.sidebar.selectbox("Selecione a Natureza:", options=naturezas_ordenadas)

    # Período padrão de um mês a partir de hoje
    hoje = date.today()
    data_inicial, data_final = st.sidebar.date_input("Selecione o Período:", value=[hoje - timedelta(days=30), hoje])

    # Filtrar ocorrências pelo período e natureza
    ocorrencias_filtradas = df_reduzido[
        (df_reduzido['Natureza'] == natureza_selecionada) &
        (df_reduzido['Data/Hora inicial'] >= data_inicial) &
        (df_reduzido['Data/Hora inicial'] <= data_final)
    ]


    # Exibir relatório de ocorrências detalhado
    if not ocorrencias_filtradas.empty:
        st.subheader(f"Ocorrências Atendidas - {natureza_selecionada}")

        # KPIs no Topo com feedback visual (cores para destacar métricas)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Atendimentos", len(ocorrencias_filtradas))
        with col2:
            top_endereco = (
                ocorrencias_filtradas['Endereço do fato']
                .value_counts().idxmax() if not ocorrencias_filtradas.empty else "N/A"
            )
            st.metric("Endereço Mais Frequente", top_endereco)
        with col3:
            media_duracao = ocorrencias_filtradas['Duração (min)'].mean()
            st.metric("Tempo Médio (min)", f"{media_duracao:.2f}" if not pd.isna(media_duracao) else "N/A")

        # Exibir Tabela de Ocorrências
        st.dataframe(ocorrencias_filtradas, height=500)
    else:
        st.subheader("Sem ocorrências para a natureza e período selecionados.")

# Linha divisória formal
st.markdown("<hr>", unsafe_allow_html=True)

# --- FILTRO DE VIATURA ---
if mostrar_viatura:
    # Filtro simples para Viatura com opções em ordem crescente
    viaturas_ordenadas = sorted(df_reduzido['Guarnição'].unique())
    viatura_selecionada = st.sidebar.selectbox("Selecione a Viatura:", options=viaturas_ordenadas)

    # Filtrar ocorrências pela viatura selecionada
    atendimentos_viatura = df_reduzido[df_reduzido['Guarnição'] == viatura_selecionada]

    # Exibir relatório de atendimentos por viatura
    st.subheader(f"Atendimentos da Viatura {viatura_selecionada}")

    # Exibir o total de atendimentos da viatura selecionada
    total_atendimentos_viatura = len(atendimentos_viatura)
    st.metric("Total de Atendimentos - Viatura Selecionada", total_atendimentos_viatura)

    if not atendimentos_viatura.empty:
        # Tabela de atendimentos da viatura
        st.dataframe(atendimentos_viatura, height=400)

        # Relatório por Natureza para a viatura, ordenado do maior para o menor
        ocorrencias_por_natureza_viatura = (
            atendimentos_viatura.groupby('Natureza').size()
            .reset_index(name='Total de Ocorrências')
            .sort_values(by='Total de Ocorrências', ascending=False)  # Ordenar em ordem decrescente
        )

        # Criar uma coluna com os 7 primeiros caracteres de Natureza
        ocorrencias_por_natureza_viatura['Natureza (curta)'] = ocorrencias_por_natureza_viatura['Natureza'].str[:7]

        # Layout com gráfico ao lado do relatório
        col1, col2 = st.columns([1, 1.5])

        with col1:
            st.subheader("Ocorrências por Natureza - Viatura Selecionada")
            st.dataframe(ocorrencias_por_natureza_viatura, height=400)

        with col2:
            # Gráfico de Ocorrências por Natureza usando a coluna curta
            fig_natureza_viatura = px.bar(
                ocorrencias_por_natureza_viatura, x='Natureza (curta)', y='Total de Ocorrências',
                labels={'Natureza (curta)': 'Natureza', 'Total de Ocorrências': 'Ocorrências'},
                height=500
            )
            fig_natureza_viatura.update_traces(texttemplate='%{y}', textposition='outside')
            fig_natureza_viatura.update_layout(
                title='Distribuição de Ocorrências por Natureza - Viatura Selecionada',
                xaxis_title='Natureza',
                yaxis_title='Número de Ocorrências',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                bargap=0.3
            )
            st.plotly_chart(fig_natureza_viatura, use_container_width=True)
    else:
        st.write("Sem atendimentos registrados para a viatura selecionada.")
