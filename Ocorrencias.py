# --- Importações e Configurações Iniciais ---
import streamlit as st
import pandas as pd
import re
import plotly.express as px
from datetime import date, timedelta
import numpy as np

# Corrige a depreciação do tipo np.bool_
array = np.array([True, False, True], dtype=np.bool_)

# --- Configuração da Página ---
st.set_page_config(page_title="Dashboard de Ocorrências", layout="wide")

# --- Estilo CSS aprimorado para o Dashboard ---
st.markdown("""
    <style>
    body {
        background-color: #f4f4f4; /* Cor de fundo neutra */
    }
    h1, h2, h3, h4, p {
        font-family: 'Verdana', sans-serif;
        color: #2C3E50;  /* Cor corporativa ou cor escura */
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

# --- Exibir Logo Centralizada ---
st.markdown("### Dashboard de Ocorrências")
st.image("logo.png", width=150)
    

# --- Seção: Visão Geral ---
st.markdown("### Visão Geral")

# --- Carregamento dos Dados ---
file_path = "Relatorio 1 a 28.xlsx"
df = pd.read_excel(file_path, sheet_name='Planilha1')

# --- Função de Conversão da Duração ---
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

# --- Aplicar Conversões e Selecionar Colunas Relevantes ---
df['Duração (min)'] = df['Duração'].apply(converter_duracao)
df['Data/Hora inicial'] = pd.to_datetime(df['Data/Hora inicial']).dt.date
df['Guarnição'] = df['Guarnição'].str[:7]  # Manter apenas as 7 primeiras letras da Guarnição

# Criar o DataFrame reduzido
colunas_relevantes = ['Data/Hora inicial', 'Guarnição', 'Natureza', 'Endereço do fato']
df_reduzido = df[colunas_relevantes + ['Duração (min)']]

# Substituir NaN por "Sem Necessidade" na coluna 'Guarnição'
df_reduzido['Guarnição'] = df_reduzido['Guarnição'].fillna("Sem Necessidade")




# Garantir que todos os valores em 'Guarnição' são strings
df_reduzido['Guarnição'] = df_reduzido['Guarnição'].astype(str)


# Barra de progresso para carregamento de dados
with st.spinner("Carregando os dados..."):
    total_por_natureza = (
        df_reduzido.groupby('Natureza').size()
        .reset_index(name='Total de Ocorrências')
        .sort_values(by='Total de Ocorrências', ascending=False)
    )

    total_por_viatura_completo = (
        df_reduzido.groupby('Guarnição').size()
        .reset_index(name='Total de Atendimentos')
        .sort_values(by='Total de Atendimentos', ascending=False)
    )

# --- Seção: Totais de Atendimentos ---
st.markdown("### Totais de Atendimentos")
st.markdown("<br>", unsafe_allow_html=True)

# --- Exibir KPIs em formato de cartão ---
valor_total_atendimentos = total_por_natureza['Total de Ocorrências'].sum()

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card">Total de Atendimentos por Natureza: {}</div>'.format(valor_total_atendimentos), unsafe_allow_html=True)
    st.dataframe(total_por_natureza.style.format({"Total de Ocorrências": "{:.0f}"}), height=450)

with col2:
    st.markdown('<div class="card">Total de Atendimentos por Viatura</div>', unsafe_allow_html=True)
    st.dataframe(total_por_viatura_completo, height=450)

# Linha Divisória
st.markdown("<hr>", unsafe_allow_html=True)

# --- Gráfico de Atendimentos por Dia ---
st.markdown("### Gráfico de Atendimentos por Dia")
atendimentos_por_dia = (
    df_reduzido.groupby('Data/Hora inicial').size()
    .reset_index(name='Quantidade de Atendimentos')
    .sort_values(by='Data/Hora inicial')
)

fig_atendimentos_dia = px.bar(
    atendimentos_por_dia,
    x='Data/Hora inicial',
    y='Quantidade de Atendimentos',
    labels={'Data/Hora inicial': 'Data', 'Quantidade de Atendimentos': 'Atendimentos'},
    title='Quantidade de Atendimentos por Dia'
)
fig_atendimentos_dia.update_traces(texttemplate='%{y}', textposition='outside')
fig_atendimentos_dia.update_layout(
    xaxis_title='Data',
    yaxis_title='Quantidade de Atendimentos',
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    bargap=0.2
)
st.plotly_chart(fig_atendimentos_dia, use_container_width=True)

# --- Configuração da Barra Lateral de Filtros ---
st.sidebar.title("Filtros de Ocorrências")
mostrar_natureza = st.sidebar.checkbox("Filtrar por Natureza")
mostrar_viatura = st.sidebar.checkbox("Filtrar por Viatura")

# --- Seção: Relatórios por Natureza ---
if mostrar_natureza:
    st.markdown("### Relatório de Ocorrências por Natureza")
    st.markdown("<br>", unsafe_allow_html=True)

    naturezas_ordenadas = df_reduzido['Natureza'].value_counts().index.tolist()
    natureza_selecionada = st.sidebar.selectbox("Selecione a Natureza:", options=naturezas_ordenadas)
    hoje = date.today()
    data_inicial, data_final = st.sidebar.date_input("Selecione o Período:", value=[hoje - timedelta(days=30), hoje])

    ocorrencias_filtradas = df_reduzido[
        (df_reduzido['Natureza'] == natureza_selecionada) &
        (df_reduzido['Data/Hora inicial'] >= data_inicial) &
        (df_reduzido['Data/Hora inicial'] <= data_final)
    ]

    if not ocorrencias_filtradas.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="card">Total de Atendimentos: {}</div>'.format(len(ocorrencias_filtradas)), unsafe_allow_html=True)
        with col2:
            top_endereco = ocorrencias_filtradas['Endereço do fato'].value_counts().idxmax() if not ocorrencias_filtradas.empty else "N/A"
            st.markdown('<div class="card">Endereço Mais Frequente: {}</div>'.format(top_endereco), unsafe_allow_html=True)
        with col3:
            media_duracao = ocorrencias_filtradas['Duração (min)'].mean()
            st.markdown('<div class="card">Tempo Médio (min): {:.2f}</div>'.format(media_duracao), unsafe_allow_html=True)

        st.dataframe(ocorrencias_filtradas, height=500)

        # Relatório por viatura para a natureza selecionada
        st.markdown("### Total de Atendimentos por Viatura para a Natureza Selecionada")
        atendimentos_por_viatura_natureza = (
            ocorrencias_filtradas.groupby('Guarnição').size()
            .reset_index(name='Total de Atendimentos')
            .sort_values(by='Total de Atendimentos', ascending=False)
        )
        st.dataframe(atendimentos_por_viatura_natureza, height=300)

        # Gráfico de Atendimentos por Dia para a Natureza Selecionada
        atendimentos_por_dia_natureza = (
            ocorrencias_filtradas.groupby('Data/Hora inicial').size()
            .reset_index(name='Quantidade de Atendimentos')
            .sort_values(by='Data/Hora inicial')
        )
        fig_atendimentos_dia_natureza = px.bar(
            atendimentos_por_dia_natureza,
            x='Data/Hora inicial',
            y='Quantidade de Atendimentos',
            labels={'Data/Hora inicial': 'Data', 'Quantidade de Atendimentos': 'Atendimentos'},
            title=f'Quantidade de Atendimentos por Dia - {natureza_selecionada}'
        )
        fig_atendimentos_dia_natureza.update_traces(texttemplate='%{y}', textposition='outside')
        fig_atendimentos_dia_natureza.update_layout(
            xaxis_title='Data',
            yaxis_title='Quantidade de Atendimentos',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=0.2
        )
        st.plotly_chart(fig_atendimentos_dia_natureza, use_container_width=True)
    else:
        st.subheader("Sem ocorrências para a natureza e período selecionados.")

st.markdown("<hr>", unsafe_allow_html=True)

# --- Filtro por Viatura ---
if mostrar_viatura:
    st.markdown("### Relatório de Ocorrências por Viatura")

    # Ajusta as viaturas disponíveis com base no filtro de natureza
    viaturas_disponiveis = ocorrencias_filtradas['Guarnição'].unique() if mostrar_natureza and not ocorrencias_filtradas.empty else sorted(df_reduzido['Guarnição'].unique())
    viatura_selecionada = st.sidebar.selectbox("Selecione a Viatura:", options=viaturas_disponiveis)

    # Filtra os atendimentos da viatura selecionada (considerando o filtro de natureza se aplicado)
    atendimentos_viatura = ocorrencias_filtradas if mostrar_natureza else df_reduzido
    atendimentos_viatura = atendimentos_viatura[atendimentos_viatura['Guarnição'] == viatura_selecionada]

    st.subheader(f"Atendimentos da Viatura {viatura_selecionada}")
    st.markdown('<div class="card">Total de Atendimentos - Viatura Selecionada: {}</div>'.format(len(atendimentos_viatura)), unsafe_allow_html=True)

    if not atendimentos_viatura.empty:
        st.dataframe(atendimentos_viatura, height=400)

        if not mostrar_natureza:
            ocorrencias_por_natureza_viatura = (
                atendimentos_viatura.groupby('Natureza').size()
                .reset_index(name='Total de Ocorrências')
                .sort_values(by='Total de Ocorrências', ascending=False)
            )
            ocorrencias_por_natureza_viatura['Natureza (curta)'] = ocorrencias_por_natureza_viatura['Natureza'].str[:7]

            # Layout com coluna para tabela e gráfico
            col1, col2 = st.columns([1, 1.5])

            with col1:
                st.subheader("Ocorrências por Natureza - Viatura Selecionada")
                st.dataframe(ocorrencias_por_natureza_viatura, height=400)

            with col2:
                fig_natureza_viatura = px.bar(
                    ocorrencias_por_natureza_viatura, x='Natureza (curta)', y='Total de Ocorrências',
                    labels={'Natureza (curta)': 'Natureza', 'Total de Ocorrências': 'Ocorrências'},
                      # Aplicação da altura global
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

        # --- Conversão de tipos para 'Data/Hora inicial' e 'Quantidade de Atendimentos' ---
        atendimentos_por_dia_viatura = (
            atendimentos_viatura.groupby('Data/Hora inicial').size()
            .reset_index(name='Quantidade de Atendimentos')
            .sort_values(by='Data/Hora inicial')
        )

        # Assegurar que 'Data/Hora inicial' é datetime e 'Quantidade de Atendimentos' é numérico
        atendimentos_por_dia_viatura['Data/Hora inicial'] = pd.to_datetime(atendimentos_por_dia_viatura['Data/Hora inicial'], errors='coerce')
        atendimentos_por_dia_viatura['Quantidade de Atendimentos'] = pd.to_numeric(atendimentos_por_dia_viatura['Quantidade de Atendimentos'], errors='coerce')

        # Criação do Gráfico com altura e largura ajustáveis
        fig_atendimentos_dia_viatura = px.bar(
            atendimentos_por_dia_viatura,
            x='Data/Hora inicial',
            y='Quantidade de Atendimentos',
            labels={'Data/Hora inicial': 'Data', 'Quantidade de Atendimentos': 'Atendimentos'},
            title=f'Quantidade de Atendimentos por Dia - Viatura {viatura_selecionada}',
               # Altura do controle global
            width=1000                # Defina a largura desejada
        )

        fig_atendimentos_dia_viatura.update_traces(texttemplate='%{y}', textposition='outside')
        fig_atendimentos_dia_viatura.update_layout(
            xaxis_title='Data',
            yaxis_title='Quantidade de Atendimentos',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            bargap=0.3                 # Ajuste do espaçamento entre barras
        )

        st.plotly_chart(fig_atendimentos_dia_viatura, use_container_width=True)
    else:
        st.write("Sem atendimentos registrados para a viatura selecionada.")
