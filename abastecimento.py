import streamlit as st
import pandas as pd
import openpyxl
import os

# Função para salvar dados no Excel sem sobrescrever
def save_to_excel(df, vehicle_id, calculate_total=False):
    file_name = "registros_frota.xlsx"
    
    # Se o arquivo já existir, verifica se a planilha do veículo existe
    if os.path.exists(file_name):
        with pd.ExcelFile(file_name, engine="openpyxl") as xls:
            if vehicle_id in xls.sheet_names:
                existing_data = pd.read_excel(file_name, sheet_name=vehicle_id)
                df = pd.concat([existing_data, df], ignore_index=True)
    else:
        # Se o arquivo não existir, cria um novo DataFrame vazio para o veículo
        df = df.copy()

    # Ordena os registros por data do mais antigo para o mais recente
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')  # Converte strings para datas, ignorando erros
    df = df.sort_values(by="Data")

    # Calcula a coluna Autonomia
    df['Autonomia'] = df['Km do Veículo'].diff().fillna(0)

    # Adiciona a somatória total na última linha
    if calculate_total:
        total_row = pd.DataFrame({
            "Data": [""],  # Deixa a célula de Data vazia para evitar erros
            "Litros": [""],
            "Km do Veículo": [""],
            "Preço por Litro": [""],
            "Tipo de Combustível": [""],
            "Valor Total": [df['Valor Total'].sum()],
            "Autonomia": [""]
        })
        df = pd.concat([df, total_row], ignore_index=True)

    # Escreve no Excel
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=vehicle_id, index=False)

    # Se calcular_total for True, atualiza a aba "Soma Total"
    if calculate_total:
        update_total_sheet(file_name)

# Função para atualizar a aba "Soma Total"
def update_total_sheet(file_name):
    all_sums = {}
    
    # Carregar todos os dados de cada veículo
    with pd.ExcelFile(file_name, engine="openpyxl") as xls:
        for sheet_name in xls.sheet_names:
            if sheet_name != "Soma Total":  # Ignora a aba de soma total
                data = pd.read_excel(xls, sheet_name=sheet_name)
                total_value = data["Valor Total"].sum()
                all_sums[sheet_name] = total_value

    # Criar DataFrame com os totais
    total_df = pd.DataFrame(list(all_sums.items()), columns=["Veículo", "Soma Total"])

    # Escreve ou atualiza a aba "Soma Total"
    with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        total_df.to_excel(writer, sheet_name="Soma Total", index=False)

# Função para limpar todos os registros, mantendo o arquivo
def clear_all_data():
    file_name = "registros_frota.xlsx"
    if os.path.exists(file_name):
        # Para cada veículo, cria um DataFrame vazio e escreve no Excel
        with pd.ExcelWriter(file_name, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            for i in range(12):
                df_empty = pd.DataFrame(columns=["Data", "Litros", "Km do Veículo", "Preço por Litro", "Tipo de Combustível", "Valor Total", "Autonomia"])
                df_empty.to_excel(writer, sheet_name=f"Veículo {i+1}", index=False)
        return True
    return False

# Título do aplicativo
st.title("Registro de Abastecimentos da Frota")

# Selecionar veículo
vehicle_id = st.selectbox("Selecione o Veículo", [f"Veículo {i+1}" for i in range(12)])

# Formulário de entrada de dados
with st.form(key="abastecimento_form"):
    data = st.date_input("Data do Abastecimento")
    litros = st.number_input("Litros Abastecidos", min_value=0.0, format="%.2f")
    km = st.number_input("Quilometragem do Veículo", min_value=0.0, format="%.2f")
    preco = st.number_input("Preço por Litro", min_value=0.0, format="%.2f")
    tipo_combustivel = st.selectbox("Tipo de Combustível", ["Diesel", "Arla 32"])

    submit_button = st.form_submit_button("Salvar Registro")

# Botão para somar valores da coluna "Valor Total"
calcular_soma = st.button("Calcular Soma dos Valores Totais")

# Botão para apagar todos os registros
apagar_registros = st.button("Apagar Todos os Registros")

# Ao enviar o formulário
if submit_button:
    valor_total = litros * preco  # Calcula o valor total

    novo_registro = {
        "Data": [data],
        "Litros": [litros],
        "Km do Veículo": [km],
        "Preço por Litro": [preco],
        "Tipo de Combustível": [tipo_combustivel],
        "Valor Total": [valor_total]
    }
    
    df = pd.DataFrame(novo_registro)
    
    # Salva os dados no Excel com ou sem somatória, dependendo se o botão foi pressionado
    save_to_excel(df, vehicle_id, calculate_total=calcular_soma)
    
    st.success(f"Registro de abastecimento para {vehicle_id} salvo com sucesso!")

# Ao clicar no botão para apagar registros
if apagar_registros:
    if clear_all_data():
        st.success("Todos os registros foram limpos com sucesso!")
    else:
        st.warning("Nenhum registro encontrado para limpar.")

# Exibir o conteúdo do Excel
if st.checkbox("Mostrar registros do Excel"):
    if os.path.exists("registros_frota.xlsx"):
        try:
            # Lê todos os registros de um veículo específico, se existir
            sheet = pd.read_excel("registros_frota.xlsx", sheet_name=vehicle_id)
            st.write(sheet)
        except ValueError:
            st.warning(f"Não há registros para {vehicle_id}.")
    else:
        st.warning("Nenhum registro encontrado.")
