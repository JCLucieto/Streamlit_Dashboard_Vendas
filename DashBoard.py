#===========================================#
#  PROJETO STREAMLIT - DASHBORAD DE VENDAS  #
#===========================================#

import os
import sys
import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go

# Variáveis Globais

df_vendas = None
df_vendas_por_estados = None
df_vendas_por_mes = None
df_vendas_por_categoria = None
df_vendas_por_vendedor = None

fig_vendas_estados_geo = None
fig_vendas_estados_barra = None
fig_vendas_mes = None
fig_vendas_categoria = None
fig_vendas_vendedor_valor = None
fig_vendas_vendedor_qtde = None

valor_total = None
qtde_total = None
qtde_vendedores = None

estado_selecionado = None
ano_selecionado = None
vendedores_selecionados = None

#-------------------------#
#    Funções Auxiliares   #
#-------------------------#

# Configurar Formato da Tela para o Streamlit
def configura_st():
    st.set_page_config(layout='wide', page_title='Ayit Digital - Dashboard de Vendas')


# Configurar Menu Lateral (Side Bar) com os Filtros
def configura_menu_lateral_filtros():
    global estado_selecionado, ano_selecionado, vendedores_selecionados
    st.sidebar.title('Filtros')
    estados = sorted(df_vendas['Local da compra'].unique())
    novo_estado = 'BR'
    estados_lista = list(estados)
    estados_lista.insert(0, novo_estado)
    estados = pd.DataFrame(estados_lista, columns=['Local da compra'])
    estado_selecionado = st.sidebar.selectbox('Estado', estados)
    todos_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
    if todos_anos:
        ano_selecionado = '9999'
    else:
        ano_selecionado = st.sidebar.slider('Ano', 2020, 2023)
    vendedores_selecionados = st.sidebar.multiselect('Selecione os Vendedores', df_vendas['Vendedor'].unique())


# Formatar Quantidade
# Recebe um Inteiro e Formata Uma String
# separada por pontos de milhar, milhao, bihao
def formata_qtde(qtde):
    if qtde >= 1000000000:
        return f"{qtde:,.0f}".replace(',', '.').replace('.', ',', 1)
    elif qtde >= 1000000:
        return f"{qtde:,.0f}".replace(',', '.')
    elif qtde >= 1000:
        return f"{qtde:,.0f}".replace(',', '.')
    else:
        return str(qtde)

# Formatar Valor Monetario
# Recebe um Float e Formata Uma String R$
# separada por pontos de milhar, milhao, bihao
def formata_valor_monetario(valor):
    valor_formatado = f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return valor_formatado

#-------------------------#
#    Funções Principais   #
#-------------------------#

# Importar a base de Dados (Arquivo vendas.json)
def importar_dados():
    global df_vendas
    try:
        # Se o arquivo existe lê local senão chama API de Leitura na Web
        if os.path.exists('vendas.json'):
            df_vendas = pd.read_json('vendas.json')
        else:
            url = 'https://labdados.com/produtos'
            response = requests.get(url)
            dados_resposta = response.json()
            df_vendas = pd.DataFrame.from_dict(dados_resposta)
            df_vendas.to_json('vendas.json')
        df_vendas['Data da Compra'] = pd.to_datetime(df_vendas['Data da Compra'], format = '%d/%m/%Y')
        # Cria Uma Coluna Ano Para Facilitar Consultas
        df_vendas['Ano'] = df_vendas['Data da Compra'].dt.year        
    except Exception as erro:
        print ('ERRO - Erro Na Obtenção dos Dados !\n')
        print (erro)
        sys.exit(1)

   
# Exibir o Logotipo da Empresa
def exibir_logotipo():
    st.image('logoayit.png')


# Cabecalho da Página
def exibir_cabecalho():
    st.title('DASHBOARD DE VENDAS :shopping_trolley:')
    #st.sidebar.title('Filtros')

# Totalizar Vendas
def totalizar_vendas():
    global df_vendas, valor_total, qtde_total, estado_selecionado, ano_selecionado
    if estado_selecionado == 'BR':
        if ano_selecionado == '9999':
            valor_total = formata_valor_monetario(float(round(df_vendas['Preço'].sum(),2)))
            qtde_total = formata_qtde(df_vendas.shape[0])
        else:
            df_filtrado = df_vendas[df_vendas['Ano'] == ano_selecionado]
            valor_total = formata_valor_monetario(float(round(df_filtrado['Preço'].sum(),2)))
            qtde_total = formata_qtde(df_filtrado.shape[0])
    else:
        if ano_selecionado == '9999':
            df_filtrado = df_vendas[df_vendas['Local da compra'] == estado_selecionado]
            valor_total = formata_valor_monetario(float(round(df_filtrado['Preço'].sum(), 2)))
            qtde_total = formata_qtde(df_filtrado.shape[0])
        else:
            df_filtrado = df_vendas[ (df_vendas['Local da compra'] == estado_selecionado) &
                                     (df_vendas['Ano'] == ano_selecionado)]
            valor_total = formata_valor_monetario(float(round(df_filtrado['Preço'].sum(), 2)))
            qtde_total = formata_qtde(df_filtrado.shape[0])


# Construir Gráfico de Vendas
def montar_informacao_vendas_por_estados():
    global df_vendas, df_vendas_por_estados, ano_selecionado, estado_selecionado
    df_vendas_por_estados = df_vendas.groupby('Local da compra')[['Preço']].sum()
    df_vendas_por_estados = (
        df_vendas
        .drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']]
        .merge(df_vendas_por_estados, left_on='Local da compra', right_index=True)
        .sort_values('Preço', ascending=False)
    )
        
        
    # 1. df_vendas.drop_duplicates(subset='Local da compra')
    #    Remove linhas duplicadas em df_vendas, considerando apenas a coluna 'Local da compra'.
    #    O resultado é um DataFrame que contém apenas entradas únicas para cada local de compra.
    # 2. [['Local da compra', 'lat', 'lon']]:
    #    Após remover as linhas duplicada, essa parte seleciona apenas três colunas do DataFrame resultante:
    #    'Local da compra', 'lat' (latitude) e 'lon' (longitude).
    #    O resultado é um DataFrame reduzido com informações de localização.
    # 3. .merge(df_vendas_por_estados, left_on='Local da compra', right_index=True)
    #    Aqui, o DataFrame reduzido é mesclado com o DataFrame `df_vendas_por_estados`.
    #    A mesclagem é feita com base na coluna 'Local da compra' do DataFrame à esquerda (o reduzido)
    #    e no índice do DataFrame à direita (`df_vendas_por_estados`).
    #    Isso significa que as informações do DataFrame `df_vendas_por_estados` serão associadas a cada local de compra.
    # 4. .sort_values('Preço', ascending=False)
    #    Por fim, essa linha ordena o DataFrame resultante da mesclagem pela coluna `'Preço'` em ordem decrescente.
    #    Isso significa que os locais de compra com o maior preço aparecerão primeiro.
    #    Em resumo, o comando completo cria um DataFrame que lista locais de compra únicos com suas 
    #    respectivas coordenadas geográficas e associa essas informações a dados de receita, organizando 
    #    o resultado pelos preços de forma decrescente.

    # print('RECEITA POR ESTADO\n')
    # print(df_vendas_por_estados)


# Montar o Grafico (Mapa Geografico) de Vendas por Estado
def montar_grafico_geo_vendas_por_estado():
    global df_vendas_por_estados, fig_vendas_estados_geo
    try:
        fig_vendas_estados_geo = px.scatter_geo(df_vendas_por_estados, 
                                                lat = 'lat',
                                                lon = 'lon',
                                                scope = 'south america',
                                                size = 'Preço',
                                                template = 'seaborn',
                                                hover_name = 'Local da compra',
                                                hover_data = {'lat':False,'lon':False},
                                                title = 'Vendas Por Estado')
        fig_vendas_estados_geo.update_layout(width=1000, height=600)
        assert isinstance(fig_vendas_estados_geo, go.Figure)
    except Exception as e:
        print(f"ERRO : Na Criação do Gráfico de Vendas Por Estados! \n {e}")
        exit(1)

# Monta informações de Vendas Por Mês
def montar_informacao_vendas_por_mes():
    global df_vendas, df_vendas_por_mes
    df_vendas_por_mes = df_vendas.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
    df_vendas_por_mes['Ano'] = df_vendas_por_mes['Data da Compra'].dt.year
    df_vendas_por_mes['Mês'] = df_vendas_por_mes['Data da Compra'].dt.month_name()

# Monta Grafico de Vendas Por Mes
def montar_grafico_vendas_por_mes():
    global df_vendas_por_mes, fig_vendas_mes
    try:
        fig_vendas_mes = px.line(
            df_vendas_por_mes,
            x='Mês',
            y='Preço',
            markers=True,
            range_y=(0, df_vendas_por_mes['Preço'].max()),
            color='Ano',
            line_dash='Ano',
            title='Vendas Por Mês'
        )
        fig_vendas_mes.update_layout(yaxis_title='Receita')
        assert isinstance(fig_vendas_mes, go.Figure)
    except Exception as e:
        print(f"ERRO : Na Criação do Gráfico de Vendas Por Mês ! \n {e}")
        exit(1)


# Monta Informação Vendas Por Categoria
def montar_informacao_vendas_por_categoria():
    global df_vendas, df_vendas_por_categoria
    df_vendas_por_categoria = df_vendas.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False).reset_index()


# Montar o Grafico (Barras) de Vendas por Estado
def montar_grafico_barras_vendas_por_estado():
    global df_vendas_por_estados, fig_vendas_estados_barra
    try:
        fig_vendas_estados_barra = px.bar(
                                        # df_vendas_por_estados,
                                        df_vendas_por_estados.head(),
                                        x='Local da compra',
                                        y = 'Preço',
                                        #title = 'Vendas Por Estado',
                                        title = 'Vendas Por Estados (Os 5 Primeiros - Top Five)')
        assert isinstance(fig_vendas_estados_barra, go.Figure)
    except Exception as e:
        print(f"ERRO : Na Criação do Gráfico de Barras - Vendas Por Estados ! \n {e}")
        exit(1)


# Montar o Grafico (Barras) de Vendas por Categoria
def montar_grafico_vendas_por_categoria():
    global df_vendas_por_categoria, fig_vendas_categoria
    try:
        fig_vendas_categoria = px.bar(df_vendas_por_categoria,
                                      x='Categoria do Produto',
                                      y = 'Preço',
                                      title = 'Vendas Por Categoria')
        assert isinstance(fig_vendas_categoria, go.Figure)
    except Exception as e:
        print(f"ERRO : Na Criação do Gráfico de Barras - Vendas Por Categoria ! \n {e}")
        exit(1)


# Monta Informação Vendas (Valor e Qtde - sum e count
def montar_informacao_vendas_por_vendedor():
    global df_vendas, df_vendas_por_vendedor
    df_vendas_por_vendedor = pd.DataFrame(df_vendas.groupby('Vendedor')['Preço'].agg(['sum', 'count']))

   
# Montar o Grafico (Barras) de Vendas por Vendedor - VALORES
def montar_grafico_vendas_por_vendedor_valor():
    global df_vendas_por_vendedor, fig_vendas_vendedor_valor, qtde_vendedores
    fig_vendas_vendedor_valor = px.bar(
        df_vendas_por_vendedor[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores),
        x='sum',
        y=df_vendas_por_vendedor[['sum']].sort_values(['sum'], ascending=False).head(qtde_vendedores).index,
        text_auto=True,
        title=f'Top {qtde_vendedores} Vendedores (Valores Vendidos)'
)


# Montar o Grafico (Barras) de Vendas por Vendedor - QUANTIDADES
def montar_grafico_vendas_por_vendedor_qtde():
    global df_vendas_por_vendedor, fig_vendas_vendedor_qtde, qtde_vendedores
    fig_vendas_vendedor_qtde = px.bar(
        df_vendas_por_vendedor[['count']].sort_values('count', ascending=False).head(qtde_vendedores),
        x = 'count',
        y = df_vendas_por_vendedor[['count']].sort_values(['count'], ascending=False).head(qtde_vendedores).index,
        text_auto=True,
        title=f'Top {qtde_vendedores} Vendedores (Volume de Vendas)'
    )


# Exibir as Informações (Abas)
def exibir_informacoes():
    global df_vendas

    global valor_total, qtde_total, qtde_vendedores, ano_selecionado  
    
    global fig_vendas_estados_barra, fig_vendas_categoria
    global fig_vendas_estados_geo, fig_vendas_mes
    global fig_vendas_vendedor_valor, fig_vendas_vendedor_qtde

    aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs(['Resumo de Vendas', 'Vendas Mensais', 'Categorias', 'Estados', 'Vendedores', 'Detalhes'])

    with aba1: # Resumo de Vendas
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            if ano_selecionado == '9999':
                st.metric('Valor Total de Vendas', valor_total)
            else:
                st.metric(f'Valor Total de Vendas no Ano de {ano_selecionado}', valor_total)
        with coluna2:
            if ano_selecionado == '9999':
                st.metric('Quantidade Total de Vendas', qtde_total)
            else:
                 st.metric(f'Quantidade Total de Vendas no Ano de {ano_selecionado}', qtde_total)

    with aba2: # Vendas Mensais
        st.plotly_chart(fig_vendas_mes, use_container_width = True)

    with aba3: # Categorias
        st.plotly_chart(fig_vendas_categoria, use_container_width = True)

    with aba4: # Estados
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.plotly_chart(fig_vendas_estados_geo, use_container_width = True)
        with coluna2:
            st.plotly_chart(fig_vendas_estados_barra, use_container_width = True)

    with aba5: # Vendedores
        qtde_vendedores = st.number_input('Quantidade de Vendedores', 2, 10, 5)
        coluna1, coluna2 = st.columns(2)
        with coluna1:
            st.metric('Valor Total de Vendas', valor_total)
        with coluna2:
            st.metric('Quantidade Total de Vendas', qtde_total)
        montar_grafico_vendas_por_vendedor_valor()
        montar_grafico_vendas_por_vendedor_qtde()
        with coluna1:
            st.plotly_chart(fig_vendas_vendedor_valor, use_container_width = True)
        with coluna2:
            st.plotly_chart(fig_vendas_vendedor_qtde, use_container_width = True)

    with aba6: # Detalhes (Lista Completa de Vendas)
        st.dataframe(df_vendas)


  
#=====================================#
#        Programa Principal           #
#=====================================#

def main():

    importar_dados()

    configura_st()

    configura_menu_lateral_filtros()

    exibir_logotipo()
    
    exibir_cabecalho()

    totalizar_vendas()

    montar_informacao_vendas_por_estados()
    montar_grafico_geo_vendas_por_estado()
    montar_grafico_barras_vendas_por_estado()

    montar_informacao_vendas_por_mes()
    montar_grafico_vendas_por_mes()
    
    montar_informacao_vendas_por_categoria()
    montar_grafico_vendas_por_categoria()

    montar_informacao_vendas_por_vendedor()
    montar_grafico_vendas_por_vendedor_valor()
    montar_grafico_vendas_por_vendedor_qtde()

    # Exibir todas as Abas e Informações
    
    exibir_informacoes()
    
        
if __name__ == "__main__":
    main()
    