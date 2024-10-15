#===========================================#
#  PROJETO STREAMLIT - PAGINA DADOS BRUTOS  #
#===========================================#

import os
import sys
import time
import requests
import pandas as pd
import streamlit as st


# Variáveis Globais

df_vendas = None
nome_arquivo = None

#-----------------------------------------------------#
#    Funções Auxiliares                               #
#-----------------------------------------------------#

# Configurar Formato da Tela para o Streamlit
def configura_st():
    st.set_page_config(layout='wide', page_title='Ayit Digital - Dashboard de Vendas')

# Converte o DataFrame para Arquivo CSV
@st.cache_data
def converte_csv(df):
    global nome_arquivo
    return df.to_csv(index = False).encode('utf-8')


# Mensagem de Sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo Baixado Com Sucesso!', icon = "✅")
    time.sleep(5)
    sucesso.empty()


#-----------------------------------------------------#
#    Funções Principais                               #
#-----------------------------------------------------#

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
        # Criando Uma Coluna Ano Para Facilitar Consultas
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
    st.title('DADOS BRUTOS')
    #st.sidebar.title('Filtros')


# Exibir Informações da Página
def exibir_informacoes():

    global df_vendas, nome_arquivo

    with st.expander('Colunas'):
        colunas = st.multiselect('Selecione as Colunas', list(df_vendas.columns), list(df_vendas.columns))

    st.sidebar.title('Filtros')

    with st.sidebar.expander('Categoria do Produto'):
        categoria = st.multiselect('Selecione as Categorias', sorted(df_vendas['Categoria do Produto'].unique()), sorted(df_vendas['Categoria do Produto'].unique()))

    with st.sidebar.expander('Nome do Produto'):
        produtos = st.multiselect('Selecione os Produtos', sorted(df_vendas['Produto'].unique()), sorted(df_vendas['Produto'].unique()))

    with st.sidebar.expander('Preço do Produto'):
        preco = st.slider('Selecione o Preço', 0, 5000, (0,5000))

    with st.sidebar.expander('Frete da Venda'):
        frete = st.slider('Frete', 0,250, (0,250))

    with st.sidebar.expander('Data da Compra'):
        data_compra = st.date_input('Selecione a Data', (df_vendas['Data da Compra'].min(), df_vendas['Data da Compra'].max()))

    with st.sidebar.expander('Vendedor'):
        vendedores = st.multiselect('Selecione os Vendedores', sorted(df_vendas['Vendedor'].unique()), sorted(df_vendas['Vendedor'].unique()))

    with st.sidebar.expander('Local da Compra'):
        local_compra = st.multiselect('Selecione o Local da Compra', sorted(df_vendas['Local da compra'].unique()), sorted(df_vendas['Local da compra'].unique()))

    with st.sidebar.expander('Avaliação da Compra'):
        avaliacao = st.slider('Selecione a Avaliação da Compra',1,5, value = (1,5))

    with st.sidebar.expander('Tipo de Pagamento'):
        tipo_pagamento = st.multiselect('Selecione o Tipo de Pagamento', sorted(df_vendas['Tipo de pagamento'].unique()), sorted(df_vendas['Tipo de pagamento'].unique()))

    with st.sidebar.expander('Quantidade de Parcelas'):
        qtde_parcelas = st.slider('Selecione a Quantidade de Parcelas', 1, 24, (1,24))


    # Monta uma ùnica Query do Pandas ara Fazer Todas as Condições de Filtragem
    
    query = '''
        Produto in @produtos and \
        `Categoria do Produto` in @categoria and \
        @preco[0] <= Preço <= @preco[1] and \
        @frete[0] <= Frete <= @frete[1] and \
        @data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
        Vendedor in @vendedores and \
        `Local da compra` in @local_compra and \
        @avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
        `Tipo de pagamento`in @tipo_pagamento and \
        @qtde_parcelas[0] <= `Quantidade de parcelas` <= @qtde_parcelas[1]
    '''
    # Aplica o Filtro das Seleções Laterais
    dados_filtrados = df_vendas.query(query)
    # Aplica o Filtro de Colunas do Incio da Página
    dados_filtrados = dados_filtrados[colunas]

    st.dataframe(dados_filtrados)

    st.markdown(f'A tabela possui  :red[{dados_filtrados.shape[0]}] linhas e  :red[{dados_filtrados.shape[1]}] colunas')

    st.markdown('Escreva um nome para o arquivo')

    coluna1, coluna2 = st.columns(2)
    with coluna1:
        nome_arquivo = st.text_input('', label_visibility = 'collapsed', value = 'dados')
        nome_arquivo += '.csv'
    with coluna2:
        st.download_button('Download da Tabela em Formato CSV', data = converte_csv(dados_filtrados), file_name = nome_arquivo, mime = 'text/csv', on_click = mensagem_sucesso)

#=====================================#
#        Programa Principal           #
#=====================================#

def main():

    importar_dados()

    configura_st()

    exibir_logotipo()
    
    exibir_cabecalho()
 
    exibir_informacoes()
    
        
if __name__ == "__main__":
    main()

