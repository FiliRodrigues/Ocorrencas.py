import streamlit as st
import pandas as pd

# Configuração da página em modo "wide"
st.set_page_config(layout="wide")

# Título da aplicação
st.title("Leitor de Excel para DataFrame")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Ler o arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Verifica se as colunas 'Unnamed: 9' e 'Unnamed: 8' existem
    if 'Unnamed: 9' in df.columns and 'Unnamed: 8' in df.columns:
        # Criar a nova coluna 'Valor Total' com os valores da coluna 'Unnamed: 9'
        df['Valor Total'] = df['Unnamed: 9']

        # Criar a nova coluna 'Valor' com os valores da coluna 'Unnamed: 8'
        df['Valor'] = df['Unnamed: 8']

        # Manter apenas as colunas 'Valor Total' e 'Valor'
        df = df[['Valor Total', 'Valor']]

        # Remover linhas onde 'Valor Total' ou 'Valor' são 0 ou que contenham 'Observação'
        df = df[(df['Valor Total'] != 0) & (df['Valor'] != 0)]  # Remove linhas com valor 0
        df = df[~df.apply(lambda row: row.astype(str).str.contains('Observação').any(), axis=1)]  # Remove linhas com 'Observação'
        df = df.dropna()  # Remove linhas com NaN

        # Arredondar os valores para 2 casas decimais
        df['Valor Total'] = df['Valor Total'].round(2)
        df['Valor'] = df['Valor'].round(2)

        # Formatar os valores para exibição com 2 casas decimais
        df['Valor Total'] = df['Valor Total'].map('{}'.format)
        df['Valor'] = df['Valor'].map('{:,.2f}'.format)

        # Exibir o DataFrame
        st.subheader("Dados do Arquivo Excel (Apenas 'Valor Total' e 'Valor')")
        st.dataframe(df, width=1950)
    else:
        missing_columns = []
        if 'Unnamed: 9' not in df.columns:
            missing_columns.append("Unnamed: 9")
        if 'Unnamed: 8' not in df.columns:
            missing_columns.append("Unnamed: 8")
        
        st.error(f"As seguintes colunas não foram encontradas no arquivo: {', '.join(missing_columns)}")

else:
    st.write("Por favor, carregue um arquivo Excel para visualizar os dados.")
