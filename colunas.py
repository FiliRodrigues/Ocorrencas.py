import pandas as pd

# Substitua o caminho abaixo pelo caminho do seu arquivo
file_path = 'arquivo_com_filtros.xlsx'

# Carregar a planilha 'FilteredData' e listar as colunas
df = pd.read_excel(file_path, sheet_name='FilteredData')
print(df.columns.tolist())
