import streamlit as st
from PyPDF2 import PdfReader
import pandas as pd

# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Função para processar e organizar os dados em DataFrame
def process_text_to_dataframe(text):
    # Exemplo de extração de dados, deve ser ajustado conforme o layout real do PDF
    # Aqui estamos simulando a extração de dados do PDF
    data = {
        'Placa': ['FDZ-7H43', 'FDZ-7H43', 'FDZ-7H43', 'FFY-2J42', 'FFY-2J42'],
        'Data de Emissão': ['17/04/2024', '19/04/2024', '22/04/2024', '17/04/2024', '18/04/2024'],
        'Produto': ['DIESEL S10', 'DIESEL S10', 'ARLA', 'DIESEL S10', 'DIESEL S10'],
        'Quantidade': [38.151, 46.470, 10.520, 43.401, 43.021],
        'Valor': [220.89, 269.06, 31.03, 251.29, 249.09]
    }
    df = pd.DataFrame(data)
    return df

# Carregar o arquivo PDF no Streamlit
st.title("Dashboard de Análise de Consumo de Combustível")

uploaded_file = st.file_uploader("Escolha o arquivo PDF", type="pdf")

if uploaded_file is not None:
    # Extraindo texto do PDF
    text = extract_text_from_pdf(uploaded_file)

    # Processando o texto para DataFrame
    df = process_text_to_dataframe(text)

    # Filtro por Placa
    placas_unicas = df['Placa'].unique()
    placa_selecionada = st.selectbox("Selecione a Placa", placas_unicas)

    # Filtrar os dados pela placa selecionada
    df_filtrado = df[df['Placa'] == placa_selecionada]

    # Exibindo a tabela de dados filtrados
    st.subheader(f"Tabela de Dados Filtrados - Placa: {placa_selecionada}")
    st.dataframe(df_filtrado)

    # Gráfico de barras para a placa selecionada
    st.subheader(f"Gráfico de Quantidades por Produto - Placa: {placa_selecionada}")
    st.bar_chart(df_filtrado.set_index('Produto')['Quantidade'])
