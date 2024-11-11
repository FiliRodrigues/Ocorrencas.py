import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Bloco 1: Configuração da página e carregamento dos dados
# ---------------------------------------------

# Configuração da página para modo wide
st.set_page_config(page_title="Dashboard de Atendimentos", layout="wide")

# Função para carregar dados com cache
@st.cache_data
def carregar_dados(file_path):
    excel_file = pd.ExcelFile(file_path)
    sheet_name = "Planilha1" if "Planilha1" in excel_file.sheet_names else excel_file.sheet_names[0]
    return pd.read_excel(excel_file, sheet_name=sheet_name)

# Caminho do arquivo
file_path = "Rel Outubro1.xlsx"
df = carregar_dados(file_path)

# Convertendo colunas de datas para formato datetime
df['Data/Hora inicial'] = pd.to_datetime(df['Data/Hora inicial'])
df['Data/Hora final'] = pd.to_datetime(df['Data/Hora final'])

# Adicionando colunas auxiliares
df['Dia'] = df['Data/Hora inicial'].dt.date
df['Mês'] = df['Data/Hora inicial'].dt.month_name()


# Bloco 2: Filtros e Configurações na Barra Lateral
# ---------------------------------------------

# Barra lateral para seleção do mês
st.sidebar.title("Filtros")
mes = st.sidebar.selectbox("Selecione o mês:", options=df['Mês'].unique(), index=0)

# Filtra o DataFrame com base no mês selecionado
df_mes = df[df['Mês'] == mes]

# Ordena Naturezas pela quantidade de ocorrências para o filtro, baseado no mês selecionado
natureza_counts = df_mes['Natureza'].value_counts().reset_index()
natureza_counts.columns = ['Natureza', 'Ocorrencias']
natureza_sorted = ["TODOS"] + natureza_counts.sort_values(by='Ocorrencias', ascending=False)['Natureza'].tolist()

# Ordena Guarnições pela quantidade de ocorrências para o filtro, baseado no mês selecionado
guarnicao_counts = df_mes['Guarnição'].value_counts().reset_index()
guarnicao_counts.columns = ['Guarnição', 'Ocorrencias']
guarnicao_sorted = ["TODOS"] + guarnicao_counts.sort_values(by='Ocorrencias', ascending=False)['Guarnição'].tolist()

# Filtros de Natureza e Guarnição na barra lateral
natureza = st.sidebar.selectbox("Selecione a Natureza:", options=natureza_sorted)
guarnicao = st.sidebar.selectbox("Selecione a Guarnição:", options=guarnicao_sorted)

# Aplicação dos filtros de Natureza e Guarnição
if natureza != "TODOS":
    df_mes = df_mes[df_mes['Natureza'] == natureza]
if guarnicao != "TODOS":
    df_mes = df_mes[df_mes['Guarnição'] == guarnicao]


# Bloco 3: KPIs - Indicadores de Desempenho
# ---------------------------------------------

# Título do Dashboard
st.title("Relatório de Atendimento")

# KPIs com média de atendimentos diários e dia com mais ocorrências

total_atendimentos_mes = len(df_mes)
dias_unicos = df_mes['Dia'].nunique()

# Calcular média de atendimentos diário apenas se houver dias únicos
media_atendimentos_diario = round(total_atendimentos_mes / dias_unicos, 2) if dias_unicos > 0 else 0

# Dia com mais ocorrências e quantidade de atendimentos no dia
if not df_mes.empty:
    dia_maior_ocorrencias = df_mes.groupby('Dia').size().idxmax()
    atendimentos_maior_dia = df_mes.groupby('Dia').size().max()
else:
    dia_maior_ocorrencias = "N/A"
    atendimentos_maior_dia = "N/A"

# Exibindo KPIs
col1, col2, col3 = st.columns(3)
col1.metric(label="Total de Atendimentos no Mês", value=total_atendimentos_mes)
col2.metric(label="Média de Atendimentos Diário", value=media_atendimentos_diario)
col3.metric(label="Dia com Mais Ocorrências", value=dia_maior_ocorrencias if dia_maior_ocorrencias == "N/A" else dia_maior_ocorrencias.strftime("%d/%m"))
col3.caption(f"Quantidade de Atendimentos: {atendimentos_maior_dia}")


# Bloco 4: Tabelas de Atendimentos por Natureza e Viatura
# ---------------------------------------------

st.markdown("### Atendimentos por Natureza e por Viatura")

# Colunas para as tabelas
col1, col2 = st.columns(2)

with col1:
    # Ordena a tabela de atendimentos por natureza do maior para o menor
    atendimentos_natureza = df_mes.groupby('Natureza').size().reset_index(name='Total de Atendimentos')
    atendimentos_natureza = atendimentos_natureza.sort_values(by='Total de Atendimentos', ascending=False).reset_index(drop=True)
    st.markdown("#### Atendimentos por Natureza")
    st.dataframe(atendimentos_natureza)

with col2:
    # Ordena a tabela de atendimentos por viatura do maior para o menor
    atendimentos_viatura = df_mes.groupby('Guarnição').size().reset_index(name='Total de Atendimentos')
    atendimentos_viatura = atendimentos_viatura.sort_values(by='Total de Atendimentos', ascending=False).reset_index(drop=True)
    st.markdown("#### Atendimentos por Viatura")
    st.dataframe(atendimentos_viatura)


import plotly.graph_objects as go

# Bloco 5: Gráfico de Atendimentos por Dia
# ---------------------------------------------

# Define tamanhos de fonte diretamente no código
font_size_x_axis = 16  # Tamanho da fonte do eixo X
font_size_text = 16    # Tamanho da fonte dos valores nas barras

# Gráfico de atendimentos por dia com cores alternadas e eixo x com todos os dias do mês
atendimentos_por_dia = df_mes.groupby('Dia').size().reindex(pd.date_range(start=df_mes['Dia'].min(), end=df_mes['Dia'].max()), fill_value=0).reset_index(name='Total de Atendimentos')
atendimentos_por_dia.columns = ['Dia', 'Total de Atendimentos']
cores = ["lightgreen", "lightblue"] * (len(atendimentos_por_dia) // 2 + 1)

# Criando o gráfico com barras alternadas e sem legenda
fig = go.Figure()

for i, row in atendimentos_por_dia.iterrows():
    fig.add_trace(
        go.Bar(
            x=[row['Dia']],
            y=[row['Total de Atendimentos']],
            marker_color=cores[i],
            text=row['Total de Atendimentos'],
            textposition='outside',
            textfont=dict(size=font_size_text)  # Define o tamanho da fonte dos valores nas barras
        )
    )

# Configuração do layout do gráfico
fig.update_layout(
    title="Atendimentos por Dia",
    xaxis_title="Dia do Mês",
    yaxis_title="Quantidade de Atendimentos",
    yaxis=dict(range=[0, 120]),  # Limite do eixo y para 120
    xaxis=dict(tickformat="%d", tickvals=atendimentos_por_dia['Dia'], tickfont=dict(size=font_size_x_axis))  # Define o tamanho da fonte do eixo x
)

# Exibindo gráfico no Streamlit
st.plotly_chart(fig)


import pandas as pd
import plotly.graph_objects as go

# Bloco 6: Filtro de Dia e Exibição Condicional de Gráfico ou Tabela
# ---------------------------------------------

# Converte 'Data/Hora inicial' para datetime, tratando valores inválidos como NaT
df_mes['Data/Hora inicial'] = pd.to_datetime(df_mes['Data/Hora inicial'], errors='coerce')

# Cria a coluna 'Dia' extraindo apenas a data e elimina valores nulos para evitar problemas com NaT
df_mes['Dia'] = df_mes['Data/Hora inicial'].dt.date

# Opção para habilitar ou desabilitar o filtro por dia
filtro_por_dia = st.checkbox("Habilitar filtro por dia para análise de natureza e viatura")

# Filtro de seleção do dia (aparece apenas se o filtro estiver habilitado)
if filtro_por_dia:
    # Extrai valores únicos de 'Dia' e os ordena, formatando diretamente sem uso de `.dt`
    dias_unicos = sorted(df_mes['Dia'].dropna().unique())
    dias_formatados = [dia.strftime('%d/%m/%Y') for dia in dias_unicos]

    dia_selecionado = st.selectbox("Selecione o Dia para ver a distribuição das naturezas de atendimento:", options=dias_formatados)
    # Converte o dia selecionado para o formato de data para filtrar o DataFrame
    dia_selecionado = pd.to_datetime(dia_selecionado, format='%d/%m/%Y').date()
    # Filtra os atendimentos para o dia selecionado
    df_dia = df_mes[df_mes['Dia'] == dia_selecionado]
else:
    # Sem filtro por dia, usa todos os dados do mês
    df_dia = df_mes

# Define tamanhos de fonte diretamente no código
font_size_x_axis = 18  # Tamanho da fonte do eixo X
font_size_text = 20    # Tamanho da fonte dos valores nas barras

# Define as cores alternadas para as barras (verde claro e azul claro)
colors = ["lightgreen", "lightblue"] * 1  # Multiplicado para garantir cores suficientes

# Condicional para exibir KPIs e o gráfico de barras de acordo com os filtros selecionados
if natureza != "TODOS" and guarnicao == "TODOS":
    # KPI 1: Quantidade de atendimentos para a natureza selecionada no dia/mês
    total_atendimentos_natureza = df_dia[df_dia['Natureza'] == natureza].shape[0]
    
    # KPI 2: Viatura que mais atendeu para a natureza selecionada no dia/mês
    viatura_counts = df_dia[df_dia['Natureza'] == natureza]['Guarnição'].value_counts()
    viatura_mais_ativa = viatura_counts.idxmax()[:7]  # Limita a guarnição aos primeiros 7 caracteres
    total_atendimentos_viatura = viatura_counts.max()
    
    # Exibindo os KPIs com estilo personalizado
    col1, col2 = st.columns(2)
    col1.metric(label=f"Atendimentos de '{natureza}'", value=total_atendimentos_natureza)
    col2.metric(
        label="Viatura com Mais Atendimentos",
        value=f"{viatura_mais_ativa}",
        delta=f"{total_atendimentos_viatura} atendimentos",
        delta_color="normal"
    )
    
    # Customiza o estilo da legenda do KPI
    col2.markdown(f"<style> div[data-testid='metric-container'] > label {{ font-size: 14px; }} </style>", unsafe_allow_html=True)

    # Prepara os dados para o gráfico de barras das guarnições
    guarnicao_counts = df_dia[df_dia['Natureza'] == natureza]['Guarnição'].value_counts().reset_index()
    guarnicao_counts.columns = ['Guarnição', 'Total de Atendimentos']
    guarnicao_counts['Guarnição'] = guarnicao_counts['Guarnição'].str[:7]  # Limita a Guarnição a 7 caracteres

    # Cria o gráfico de barras com cores alternadas e configurações de fonte
    fig = go.Figure(data=[
        go.Bar(
            x=guarnicao_counts['Guarnição'],
            y=guarnicao_counts['Total de Atendimentos'],
            text=guarnicao_counts['Total de Atendimentos'],
            textposition='outside',
            marker_color=colors[:len(guarnicao_counts)],  # Aplica cores alternadas
            textfont=dict(size=font_size_text)  # Define o tamanho da fonte dos valores nas barras
        )
    ])

    # Configuração do layout do gráfico
    fig.update_layout(
        title=f"Distribuição das Viaturas para a Natureza '{natureza}'" + (f" no Dia {dia_selecionado.strftime('%d/%m/%Y')}" if filtro_por_dia else " no Mês"),
        xaxis_title="Guarnição",
        yaxis_title="Quantidade de Atendimentos",
        yaxis=dict(range=[0, 15]),  # Limite do eixo y para 15
        xaxis=dict(tickfont=dict(size=font_size_x_axis))  # Define o tamanho da fonte do eixo x
    )

    # Exibe o gráfico no Streamlit
    st.plotly_chart(fig)

elif natureza != "TODOS" or guarnicao != "TODOS":
    # Quando um dos filtros está selecionado, exibe as naturezas
    natureza_counts = df_dia['Natureza'].value_counts().reset_index()
    natureza_counts.columns = ['Natureza', 'Total de Atendimentos']

    # Cria um gráfico de barras para mostrar a distribuição das naturezas
    fig = go.Figure(data=[
        go.Bar(
            x=natureza_counts['Natureza'].str[:6],  # Limita a Natureza a 6 caracteres
            y=natureza_counts['Total de Atendimentos'],
            text=natureza_counts['Total de Atendimentos'],
            textposition='outside',
            marker_color=colors[:len(natureza_counts)],  # Aplica cores alternadas
            textfont=dict(size=font_size_text)  # Define o tamanho da fonte dos valores nas barras
        )
    ])

    # Configuração do layout do gráfico
    fig.update_layout(
        title=f"Distribuição das Naturezas" + (f" no Dia {dia_selecionado.strftime('%d/%m/%Y')}" if filtro_por_dia else " no Mês"),
        xaxis_title="Natureza",
        yaxis_title="Quantidade de Atendimentos",
        yaxis=dict(range=[0,100]),  # Limite do eixo y para 15
        xaxis=dict(tickfont=dict(size=font_size_x_axis))  # Define o tamanho da fonte do eixo x
    )

    # Exibe o gráfico no Streamlit
    st.plotly_chart(fig)

else:
    # Exibe a tabela com a soma de cada natureza para o dia ou mês
    natureza_counts = df_dia['Natureza'].value_counts().reset_index()
    natureza_counts.columns = ['Natureza', 'Total de Atendimentos']
    st.markdown(f"### Total de Atendimentos por Natureza" + (f" no Dia {dia_selecionado.strftime('%d/%m/%Y')}" if filtro_por_dia else " no Mês"))
    st.dataframe(natureza_counts)

# Bloco final: Tabelas de Quantidade de Atendimentos por Turno e Viatura no Mês Selecionado
# ---------------------------------------------

# Adiciona uma coluna 'Hora' extraída do horário de início para classificação por turno
df_mes['Hora'] = df_mes['Data/Hora inicial'].dt.time

# Função para categorizar o turno com base na hora
def definir_turno(horario):
    if pd.Timestamp("05:30:00").time() <= horario < pd.Timestamp("13:50:00").time():
        return "Manhã"
    elif pd.Timestamp("13:50:00").time() <= horario < pd.Timestamp("21:50:00").time():
        return "Tarde"
    else:
        return "Madrugada"

# Aplica a função para criar a coluna 'Turno' no DataFrame filtrado pelo mês
df_mes['Turno'] = df_mes['Hora'].apply(definir_turno)

# Conta a quantidade total de atendimentos por turno
total_atendimentos_por_turno = df_mes['Turno'].value_counts().reset_index()
total_atendimentos_por_turno.columns = ['Turno', 'Total de Atendimentos']

# Conta a quantidade de atendimentos por viatura dentro de cada turno
atendimentos_por_turno_e_viatura = df_mes.groupby(['Turno', 'Guarnição']).size().reset_index(name='Atendimentos por Viatura')

# Limita a Guarnição aos primeiros 7 caracteres
atendimentos_por_turno_e_viatura['Guarnição'] = atendimentos_por_turno_e_viatura['Guarnição'].str[:7]

# Ordena os dados para exibição organizada por turno e por quantidade de atendimentos (maior para menor)
turno_order = ["Manhã", "Tarde", "Madrugada"]
total_atendimentos_por_turno['Turno'] = pd.Categorical(total_atendimentos_por_turno['Turno'], categories=turno_order, ordered=True)
atendimentos_por_turno_e_viatura['Turno'] = pd.Categorical(atendimentos_por_turno_e_viatura['Turno'], categories=turno_order, ordered=True)

total_atendimentos_por_turno = total_atendimentos_por_turno.sort_values(by='Turno')
atendimentos_por_turno_e_viatura = atendimentos_por_turno_e_viatura.sort_values(by=['Turno', 'Atendimentos por Viatura'], ascending=[True, False])

# Divide os dados em tabelas separadas para cada turno e remove a coluna 'Turno'
tabela_manha = atendimentos_por_turno_e_viatura[atendimentos_por_turno_e_viatura['Turno'] == 'Manhã'].drop(columns=['Turno'])
tabela_tarde = atendimentos_por_turno_e_viatura[atendimentos_por_turno_e_viatura['Turno'] == 'Tarde'].drop(columns=['Turno'])
tabela_madrugada = atendimentos_por_turno_e_viatura[atendimentos_por_turno_e_viatura['Turno'] == 'Madrugada'].drop(columns=['Turno'])

# Obtém o total de atendimentos para cada turno, verificando se existe algum dado
tabela_manha_total = total_atendimentos_por_turno[total_atendimentos_por_turno['Turno'] == 'Manhã']['Total de Atendimentos'].values
tabela_tarde_total = total_atendimentos_por_turno[total_atendimentos_por_turno['Turno'] == 'Tarde']['Total de Atendimentos'].values
tabela_madrugada_total = total_atendimentos_por_turno[total_atendimentos_por_turno['Turno'] == 'Madrugada']['Total de Atendimentos'].values

# Exibe as tabelas em colunas lado a lado com verificação para evitar erros
col1, col2, col3 = st.columns(3)

with col1:
    if tabela_manha_total.size > 0:
        st.markdown(f"### Turno da Manhã ({tabela_manha_total[0]} atendimentos)")
        st.dataframe(tabela_manha)
    else:
        st.markdown("### Turno da Manhã")
        st.write("Nenhum atendimento registrado.")

with col2:
    if tabela_tarde_total.size > 0:
        st.markdown(f"### Turno da Tarde ({tabela_tarde_total[0]} atendimentos)")
        st.dataframe(tabela_tarde)
    else:
        st.markdown("### Turno da Tarde")
        st.write("Nenhum atendimento registrado.")

with col3:
    if tabela_madrugada_total.size > 0:
        st.markdown(f"### Turno da Madrugada ({tabela_madrugada_total[0]} atendimentos)")
        st.dataframe(tabela_madrugada)
    else:
        st.markdown("### Turno da Madrugada")
        st.write("Nenhum atendimento registrado.")

# Bloco 7: Filtro de Turno, KPIs e Visualizações Condicionais
# ---------------------------------------------

# Converte 'Data/Hora inicial' para datetime, tratando valores inválidos como NaT (se ainda não estiver em datetime)
df_mes['Data/Hora inicial'] = pd.to_datetime(df_mes['Data/Hora inicial'], errors='coerce')

# Cria a coluna 'Dia' extraindo apenas a data (se ainda não estiver presente) e elimina valores nulos para evitar problemas com NaT
if 'Dia' not in df_mes.columns:
    df_mes['Dia'] = pd.to_datetime(df_mes['Data/Hora inicial'].dt.date, errors='coerce')

# Cria a coluna 'Turno' com base no horário da 'Data/Hora inicial'
def definir_turno(horario):
    if pd.Timestamp("05:30:00").time() <= horario < pd.Timestamp("13:50:00").time():
        return "Manhã"
    elif pd.Timestamp("13:50:00").time() <= horario < pd.Timestamp("21:50:00").time():
        return "Tarde"
    else:
        return "Madrugada"

df_mes['Hora'] = df_mes['Data/Hora inicial'].dt.time
df_mes['Turno'] = df_mes['Hora'].apply(definir_turno)

# Filtro de Turno na barra lateral
turno_selecionado = st.sidebar.selectbox(
    "Selecione o Turno:",
    options=["TODOS", "Manhã", "Tarde", "Madrugada"]
)

# Filtra os dados com base no turno selecionado
if turno_selecionado != "TODOS":
    df_turno = df_mes[df_mes['Turno'] == turno_selecionado]
else:
    df_turno = df_mes

# Exibe a tabela, KPIs e o gráfico apenas quando um turno específico é selecionado
if turno_selecionado != "TODOS":
    # Tabela com a soma das naturezas para o turno selecionado
    natureza_counts = df_turno['Natureza'].value_counts().reset_index()
    natureza_counts.columns = ['Natureza', 'Total de Atendimentos']
    
    # KPIs
    quantidade_atendimentos_turno = df_turno.shape[0]
    natureza_mais_atendida = natureza_counts.iloc[0]['Natureza'] if not natureza_counts.empty else "N/A"
    quantidade_natureza_mais_atendida = int(natureza_counts.iloc[0]['Total de Atendimentos']) if not natureza_counts.empty else 0  # Conversão para int
    
    viatura_mais_ativa_counts = df_turno['Guarnição'].value_counts()
    viatura_mais_ativa = viatura_mais_ativa_counts.idxmax()[:7] if not viatura_mais_ativa_counts.empty else "N/A"
    
    # Verificação para garantir que há dados para a viatura mais ativa antes de calcular a natureza
    if viatura_mais_ativa != "N/A":
        natureza_mais_atendida_viatura_series = df_turno[df_turno['Guarnição'] == viatura_mais_ativa]['Natureza'].mode()
        natureza_mais_atendida_viatura = natureza_mais_atendida_viatura_series[0] if not natureza_mais_atendida_viatura_series.empty else "N/A"
    else:
        natureza_mais_atendida_viatura = "N/A"

    # Layout dos KPIs ao lado esquerdo da tabela
    kpi1, kpi2 = st.columns(2)
    kpi3, kpi4 = st.columns(2)

    kpi1.metric(label="Quantidade de Atendimentos do Turno", value=quantidade_atendimentos_turno)
    kpi2.metric(label="Natureza com Mais Atendimentos", value=natureza_mais_atendida, delta=quantidade_natureza_mais_atendida)
    kpi3.metric(label="Viatura com Mais Atendimentos", value=viatura_mais_ativa)
    kpi4.metric(label="Natureza Mais Atendida pela Viatura", value=natureza_mais_atendida_viatura)

    # Exibe a tabela de atendimentos por natureza para o turno selecionado
    st.markdown(f"### Total de Atendimentos por Natureza no Turno {turno_selecionado}")
    st.dataframe(natureza_counts)

    # Gráfico com a distribuição de atendimentos por dia no mês
    atendimentos_por_dia = df_turno.groupby('Dia').size().reset_index(name='Total de Atendimentos')
    atendimentos_por_dia['Dia'] = pd.to_datetime(atendimentos_por_dia['Dia'], errors='coerce')  # Garante que 'Dia' está em datetime
    max_valor_dia = atendimentos_por_dia['Total de Atendimentos'].max() + 10

    # Gráfico com cores alternadas (verde claro e azul claro)
    colors = ["lightgreen" if i % 2 == 0 else "lightblue" for i in range(len(atendimentos_por_dia))]
    
    fig = go.Figure(data=[
        go.Bar(
            x=atendimentos_por_dia['Dia'].dt.strftime('%d/%m'),
            y=atendimentos_por_dia['Total de Atendimentos'],
            text=atendimentos_por_dia['Total de Atendimentos'],
            textposition='outside',
            marker_color=colors
        )
    ])
    
    fig.update_layout(
        title=f"Distribuição de Atendimentos por Dia no Turno {turno_selecionado}",
        xaxis_title="Dia",
        yaxis_title="Quantidade de Atendimentos",
        yaxis=dict(range=[0, max_valor_dia])
    )
    
    st.plotly_chart(fig)
else:
    st.markdown("### Exibindo dados completos do mês, sem filtro por turno.")
    # Aqui você pode adicionar um resumo geral ou outros componentes caso deseje mostrar algo para "TODOS"
