import pandas as pd
import streamlit as st

# Configuração da página em modo "wide"
st.set_page_config(layout="wide")

# Título da aplicação
st.title("Visualização Completa e Relatórios por Coluna do Excel")

# CSS para mudar a cor do texto dos filtros para verde e aumentar a fonte
st.markdown(
    """
    <style>
    .stSelectbox {
        font-size: 20px;  /* Aumenta o tamanho da fonte */
        padding: 10px;     /* Aumenta o padding para aumentar o tamanho do selectbox */
        width: 400px;      /* Define uma largura específica */
    }
    .stRadio {
        color: green;
        font-size: 20px;  /* Aumenta o tamanho da fonte dos radios */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=["xlsx"])

if uploaded_file is not None:
    # Ler o arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Remover as colunas indesejadas
    colunas_para_remover = ['Id', 'N', 'N° Talão', 'N° BO GCM', 'Anexos', 'Suporte à guarnição', 'Status']
    df = df.drop(columns=[coluna for coluna in colunas_para_remover if coluna in df.columns])

    # Exibir toda a tabela sem as colunas removidas
    st.subheader("Tabela Completa")
    st.dataframe(df, width=1950)  # Exibir toda a tabela


    # Separação e relatórios por colunas
    st.subheader("Relatórios de Colunas")

    # Criação de colunas para exibir os relatórios lado a lado
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Relatório: Guarnição")
        guarnicao_counts = df['Guarnição'].value_counts()
        st.write(guarnicao_counts, width=1950)

    with col2:
        st.subheader("Relatório: Natureza (Códigos Completos)")
        df['Código Natureza'] = df['Natureza'].str.split(' - ').str[0]
        df['Nome Natureza'] = df['Natureza']
        natureza_counts = df['Nome Natureza'].value_counts().nlargest(10)
        st.write(natureza_counts, width=1950)

    # Criação de um filtro para escolher qual relatório visualizar
    st.subheader("Visualizar Relatórios Específicos")

    relatorios =  [f'Código: {codigo}' for codigo in natureza_counts.index]
    selected_relatorio = st.selectbox("Selecione um Relatório:", relatorios)

    # Exibir o relatório selecionado
    if selected_relatorio == 'Código 46':
        st.subheader("Relatório: Código 46")
        df_cod_46 = df[df['Código Natureza'].str.contains('46', na=False)]
        
        # Verifique se as colunas de data/hora existem
        if 'Data/Hora inicial' in df_cod_46.columns and 'Data/Hora final' in df_cod_46.columns:
            # Calcular a duração
            df_cod_46['Duração'] = pd.to_datetime(df_cod_46['Data/Hora final']) - pd.to_datetime(df_cod_46['Data/Hora inicial'])
            media_duracao = df_cod_46['Duração'].mean()

            # Exibir a duração média
            st.write(f"Duração média das ocorrências (Código 46): {media_duracao}")

        # Seleciona apenas as colunas relevantes
        if not df_cod_46.empty:
            report_cod_46 = df_cod_46[['Nome Natureza', 'Data/Hora inicial', 'Endereço do fato', 'Guarnição']]
            st.write(report_cod_46, width=1950)

            # Contagem de ocorrências por local
            ocorrencias_local = df_cod_46['Endereço do fato'].value_counts()
            st.subheader("Ocorrências por Local (Código 46)")
            st.write(ocorrencias_local, width=1950)
        else:
            st.write("Não há registros para o Código 46.", width=1950)

    else:
        codigo = selected_relatorio.split(': ')[-1]
        st.subheader(f"Relatório para o Código: {codigo}")
        df_cod = df[df['Nome Natureza'] == codigo]
        report_cod = df_cod[['Nome Natureza', 'Data/Hora inicial', 'Endereço do fato', 'Guarnição']]
        
        if not report_cod.empty:
            st.write(report_cod, width=1950)

            # Contagem de ocorrências por local
            ocorrencias_local = df_cod['Endereço do fato'].value_counts()
            st.subheader(f"Ocorências por Local (Código {codigo})")
            st.write(ocorrencias_local, width=1950)
        else:
            st.write(f"Não há registros para o Código: {codigo}.", width=1950)

else:
    st.write("Por favor, carregue um arquivo Excel para visualizar os dados e gerar os relatórios.")
