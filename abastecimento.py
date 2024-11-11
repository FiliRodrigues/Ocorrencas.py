# Importação de Bibliotecas
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Configuração da Página
st.set_page_config(layout="wide", page_title="Dashboard de Consumo de Veículos")

# =======================
# Funções Auxiliares
# =======================

# Função para carregar e preparar dados com cache
@st.cache_data
def carregar_dados(filepath):
    data = pd.read_csv(filepath, sep=';', encoding='utf-8')
    data['Data/Hora'] = pd.to_datetime(data['Data/Hora'], dayfirst=True, errors='coerce')
    data['Dia'] = data['Data/Hora'].dt.date
    data['Dia'] = pd.to_datetime(data['Dia'])  # Forçando 'Dia' a ser datetime
    data['Dia_Formatado'] = data['Data/Hora'].dt.strftime('%d/%m')
    data['Mês'] = data['Data/Hora'].dt.month
    data['Valor Venda'] = pd.to_numeric(data['Valor Venda'].str.replace(',', '.'), errors='coerce').fillna(0)
    return data


# =======================
# Função para Exibir Gráfico Total por Mês com Título, Subtítulo, Comparação Dinâmica e Gráficos de Barras e Linhas
# =======================
def exibir_grafico_total_por_mes(data):
    # Título e Subtítulo do Dashboard
    st.markdown("<h1 style='text-align: center; color: #4A90E2;'>Histórico de Consumo de Veículos Paulinia 2024</h1>", unsafe_allow_html=True)
    st.write("""
    Este dashboard fornece uma análise detalhada do consumo de veículos da cidade de Paulinia no ano de 2024 
    """)

    st.markdown("### Gastos Mensais")
    
    # Calcula o valor total gasto em cada mês
    total_por_mes = data.groupby('Mês')['Valor Venda'].sum().reset_index()
    
    # Nome dos meses para exibir no eixo X
    meses_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    total_por_mes['Mês Nome'] = total_por_mes['Mês'].map(meses_nomes)
    
    # Definir cores diferentes para cada barra
    cores = [
        "rgb(31, 119, 180)", "rgb(255, 127, 14)", "rgb(44, 160, 44)", "rgb(214, 39, 40)",
        "rgb(148, 103, 189)", "rgb(140, 86, 75)", "rgb(227, 119, 194)", "rgb(127, 127, 127)",
        "rgb(188, 189, 34)", "rgb(23, 190, 207)", "rgb(255, 165, 0)", "rgb(255, 69, 0)"
    ]

    # Adiciona uma coluna para a comparação percentual com o mês anterior
    total_por_mes['Variação (%)'] = total_por_mes['Valor Venda'].pct_change() * 100

    # Gráfico de barras para o total gasto em cada mês
    fig = go.Figure()

    # Adiciona as barras com cores distintas e tamanho do texto aumentado
    fig.add_trace(go.Bar(
        x=total_por_mes['Mês Nome'],
        y=total_por_mes['Valor Venda'],
        text=[f"R$ {v:,.2f}".replace(',', '.') for v in total_por_mes['Valor Venda']],
        textposition='inside',
        name="Total Gasto",
        marker_color=cores[:len(total_por_mes)],  # Aplica uma cor para cada mês
        textfont=dict(size=20)  # Define o tamanho do texto dentro das barras para 20
    ))

    # Gráfico de linha para o total gasto em cada mês
    fig.add_trace(go.Scatter(
        x=total_por_mes['Mês Nome'],
        y=total_por_mes['Valor Venda'],
        mode='lines+markers',
        name="Tendência Mensal",
        line=dict(color="black", width=2, dash="solid"),
        marker=dict(size=6)
    ))

    # Configuração do layout com a legenda do mês em destaque
    fig.update_layout(
        title="Total Gasto por Mês",
        xaxis_title="Mês",
        yaxis_title="Valor Total (R$)",
        template="plotly_white",
        title_x=0.5,
        xaxis=dict(
            tickfont=dict(size=20)  # Aumenta o tamanho da fonte dos nomes dos meses
        )
    )

    # Exibir o gráfico combinado em destaque
    st.plotly_chart(fig, use_container_width=True)

    # Comparação com o mês anterior de forma dinâmica (apenas para os 3 meses mais recentes)
    st.markdown("### Comparativo Mês a Mês")
    # Seleciona os 3 últimos meses para exibição e ordena cronologicamente
    comparativo_meses = total_por_mes.tail(3).sort_values(by="Mês")
    colunas = st.columns(3)  # Cria 3 colunas para os 3 meses mais recentes

    # Exibe cada um dos últimos 3 meses com valor total e variação percentual
    for i, row in enumerate(comparativo_meses.iterrows()):
        _, row_data = row
        mes_nome = row_data['Mês Nome']
        valor_atual = row_data['Valor Venda']
        variacao = row_data['Variação (%)']

        # Adiciona a seta e a cor com base na variação percentual
        if pd.notna(variacao) and variacao > 0:
            variacao_texto = f" {variacao:.2f}%"
            delta_color = "off"  # Vermelho para indicar aumento
        elif pd.notna(variacao) and variacao < 0:
            variacao_texto = f" {abs(variacao):.2f}%"
            delta_color = "off"  # Verde para indicar redução
        else:
            variacao_texto = None
            delta_color = "off"

        # Exibe a métrica com o valor total e a variação percentual em destaque
        with colunas[i]:  # Usa o índice da coluna diretamente
            st.metric(label=mes_nome, value=f"R$ {valor_atual:,.2f}", delta=variacao_texto, delta_color=delta_color)

# Função para exibir a introdução e o filtro de mês
def exibir_introducao_e_filtro(data):
    st.write("### Selecione o Mês para Visualização")
    # Mapeamento dos números dos meses para os nomes dos meses
    meses_nomes = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }
    
    # Obter os meses disponíveis no conjunto de dados
    meses_disponiveis = sorted(data['Mês'].unique())
    meses_disponiveis_nomes = [meses_nomes[mes] for mes in meses_disponiveis]

    # Seleção de mês com nome por extenso
    mes_selecionado_nome = st.selectbox("", meses_disponiveis_nomes)

    # Converter o nome do mês selecionado de volta para o número correspondente
    mes_selecionado = [num for num, nome in meses_nomes.items() if nome == mes_selecionado_nome][0]
    
    # Filtrar dados pelo mês selecionado
    data_filtrado = data[data['Mês'] == mes_selecionado]
    
    return data_filtrado

# =======================
# Funções de Exibição
# =======================

def exibir_visao_geral_com_tendencias_e_insights(data_filtrado):
    st.subheader("Visão Detalhada do Mês")

    # Cálculo dos KPIs com base no conjunto de dados filtrado
    gasto_total_mes = data_filtrado['Valor Venda'].sum()
    dias_maior_consumo = data_filtrado.groupby('Dia')['Valor Venda'].sum().idxmax()
    maior_consumo = data_filtrado.groupby('Dia')['Valor Venda'].sum().max()
    media_gasto_dia = data_filtrado.groupby('Dia')['Valor Venda'].sum().mean()
    media_abastecimentos_dia = data_filtrado.groupby('Dia')['Valor Venda'].count().mean()
    dia_maior_abastecimento = data_filtrado.groupby('Dia')['Valor Venda'].count().idxmax()
    maior_abastecimento = data_filtrado.groupby('Dia')['Valor Venda'].count().max()

    # Exibir KPIs usando o conjunto de dados filtrado
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gasto Total no Mês", f"R$ {gasto_total_mes:,.2f}".replace(',', '.'))
        st.write(f"**Dia com maior consumo:** {dias_maior_consumo.strftime('%d/%m')} com R$ {maior_consumo:,.2f}".replace(',', '.'))
    
    with col2:
        st.metric("Média de Gasto por Dia", f"R$ {media_gasto_dia:,.2f}".replace(',', '.'))

    with col3:
        st.metric("Média de Abastecimentos por Dia", f"{media_abastecimentos_dia:.2f}")
        st.write(f"**Dia com mais abastecimentos:** {dia_maior_abastecimento.strftime('%d/%m')} com {maior_abastecimento} abastecimentos")

    # Configuração de tamanhos da fonte no gráfico
    tamanho_fonte_valores = 20  # Tamanho da fonte dos valores nas barras
    tamanho_fonte_legenda = 16  # Tamanho da fonte dos rótulos no eixo X

    # Gráfico de valor total de consumo por dia com linha de média mensal, usando dados filtrados
    valor_diario = data_filtrado.groupby('Dia')['Valor Venda'].sum().reset_index()
    valor_diario['Dia'] = pd.to_datetime(valor_diario['Dia'])
    valor_diario['Dia_Formatado'] = valor_diario['Dia'].dt.strftime('%d/%m')
    
    # Calcular a média mensal com os dados filtrados
    media_mensal = valor_diario['Valor Venda'].mean()

    # Criar gráfico com barras de consumo diário e linha de média mensal
    fig_valor_diario = go.Figure()

    # Barras para o valor diário, com cores alternadas
    cores_barras = ["rgb(31, 119, 180)", "rgb(144, 238, 144)"]  # Azul e verde claro
    fig_valor_diario.add_trace(go.Bar(
        x=valor_diario['Dia_Formatado'],
        y=valor_diario['Valor Venda'],
        text=[f"R$ {v:,.2f}".replace(',', '.') for v in valor_diario['Valor Venda']],
        textposition='outside',
        name="Consumo Diário",
        marker_color=[cores_barras[i % 2] for i in range(len(valor_diario))],  # Cores alternadas
    ))

    # Linha para a média mensal
    fig_valor_diario.add_trace(go.Scatter(
        x=valor_diario['Dia_Formatado'],
        y=[media_mensal] * len(valor_diario),
        mode='lines',
        name="Média do Mês",
        line=dict(color='red', dash='dash')
    ))

    fig_valor_diario.update_layout(
        title="Valor Total de Consumo por Dia com Média do Mês",
        xaxis_title="Data",
        yaxis_title="Valor Total (R$)",
        template="plotly_white",
        title_x=0.5,
        yaxis=dict(range=[0, 2200]),  # Define a escala máxima do eixo Y para 2200
        xaxis=dict(tickfont=dict(size=tamanho_fonte_legenda)),  # Define o tamanho dos rótulos do eixo X
    )

    # Atualização do tamanho da fonte dos valores nas barras
    fig_valor_diario.update_traces(textfont=dict(size=tamanho_fonte_valores))

    # Exibir o gráfico ocupando a largura total da tela
    st.plotly_chart(fig_valor_diario, use_container_width=True)

    # Cálculo do gasto na primeira e segunda quinzena
    primeira_quinzena = data_filtrado[data_filtrado['Data/Hora'].dt.day <= 15]
    segunda_quinzena = data_filtrado[data_filtrado['Data/Hora'].dt.day > 15]
    
    gasto_primeira_quinzena = primeira_quinzena['Valor Venda'].sum()
    gasto_segunda_quinzena = segunda_quinzena['Valor Venda'].sum()
    
    # Cálculo da variação percentual
    if gasto_primeira_quinzena > 0:
        variacao_quinzena = ((gasto_segunda_quinzena - gasto_primeira_quinzena) / gasto_primeira_quinzena) * 100
    else:
        variacao_quinzena = 0

    # Exibir KPIs da primeira e segunda quinzena
    st.write("### Gasto Quinzenal e Variação Percentual")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Gasto 1ª Quinzena", f"R$ {gasto_primeira_quinzena:,.2f}".replace(',', '.'))
    
    with col2:
        st.metric("Gasto 2ª Quinzena", f"R$ {gasto_segunda_quinzena:,.2f}".replace(',', '.'))

    with col3:
        if variacao_quinzena > 0:
            st.metric("Variação Quinzenal", f"Aumento de {variacao_quinzena:.2f}%")
        else:
            st.metric("Variação Quinzenal", f"Redução de {abs(variacao_quinzena):.2f}%")

    # Insights Automáticos
    st.write("### Insights")
    st.write(f"- Veículo com maior consumo: **{data_filtrado.groupby('Placa')['Valor Venda'].sum().idxmax()}** com um total de **R$ {data_filtrado.groupby('Placa')['Valor Venda'].sum().max():,.2f}** no mês.".replace(',', '.'))

def exibir_analise_por_veiculo(data_filtrado):
    st.subheader("Análise por Veículo")
    
    # Expander para mostrar detalhes de um veículo selecionado
    with st.expander("Exibir Detalhes"):
        # Seleção da viatura
        placa_selecionada = st.selectbox("Selecione a Placa do Veículo", data_filtrado['Placa'].unique())
        dados_filtrados = data_filtrado[data_filtrado['Placa'] == placa_selecionada]

        # Cálculo dos KPIs
        gasto_total_mes_placa = dados_filtrados['Valor Venda'].sum()
        kms_rodados_mes = dados_filtrados['Km Rod.'].sum()
        dia_maior_abastecimento = dados_filtrados.groupby('Dia')['Valor Venda'].sum().idxmax()
        valor_maior_abastecimento = dados_filtrados.groupby('Dia')['Valor Venda'].sum().max()

        # Exibição dos KPIs
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Gasto Total no Mês (Placa Selecionada)", f"R$ {gasto_total_mes_placa:,.2f}".replace(',', '.'))
        
        with col2:
            st.metric("KMs Rodados no Mês", f"{kms_rodados_mes:,.0f} km")

        # Exibir dia com maior abastecimento em valor
        st.write(f"**Dia com Maior Abastecimento:** {dia_maior_abastecimento.strftime('%d/%m')} com R$ {valor_maior_abastecimento:,.2f}".replace(',', '.'))

        # Definição dos tamanhos de fonte para os valores nas barras e rótulos do eixo X
        tamanho_fonte_valor = 20  # Tamanho da fonte dos valores nas barras
        tamanho_fonte_rotulos = 20  # Tamanho da fonte dos rótulos do eixo X

        # Dados para o gráfico de abastecimento diário
        abastecimento_diario = dados_filtrados.groupby('Dia')['Valor Venda'].sum().reset_index()
        abastecimento_diario['Dia'] = pd.to_datetime(abastecimento_diario['Dia'])
        abastecimento_diario['Dia_Formatado'] = abastecimento_diario['Dia'].dt.strftime('%d/%m')

        # Definindo cores alternadas para as barras (azul e verde claro)
        cores_barras = ["rgb(31, 119, 180)", "rgb(144, 238, 144)"]  # Azul e verde claro

        # Criação do gráfico de abastecimento diário
        fig_abastecimento_diario = go.Figure(data=go.Bar(
            x=abastecimento_diario['Dia_Formatado'],
            y=abastecimento_diario['Valor Venda'],
            text=[f"R$ {v:,.2f}".replace(',', '.') for v in abastecimento_diario['Valor Venda']],
            textposition='outside',
            name="Consumo Diário",
            marker_color=[cores_barras[i % 2] for i in range(len(abastecimento_diario))]  # Aplica cores alternadas
        ))

        # Configuração do layout do gráfico
        fig_abastecimento_diario.update_layout(
            title="Valor de Abastecimento Diário (Placa Selecionada)",
            xaxis_title="Data",
            yaxis_title="Valor de Abastecimento (R$)",
            template="plotly_white",
            title_x=0.5,
            yaxis=dict(range=[0, 400]),  # Define a escala máxima do eixo Y para 400
            xaxis=dict(tickfont=dict(size=tamanho_fonte_rotulos)),  # Define o tamanho dos rótulos do eixo X
        )

        # Atualização do tamanho da fonte dos valores nas barras
        fig_abastecimento_diario.update_traces(textfont=dict(size=tamanho_fonte_valor))

        # Exibir o gráfico
        st.plotly_chart(fig_abastecimento_diario, use_container_width=True)

# =======================
# Carregamento de Dados e Exibição do Dashboard
# =======================

# Carregar dados
data = carregar_dados("historico_consumo1.csv")

# Exibir gráfico total por mês
exibir_grafico_total_por_mes(data)

# Exibir introdução e filtro de mês
data_filtrado = exibir_introducao_e_filtro(data)

# Exibir visão geral do mês e análise detalhada usando o filtro
exibir_visao_geral_com_tendencias_e_insights(data_filtrado)
exibir_analise_por_veiculo(data_filtrado)
