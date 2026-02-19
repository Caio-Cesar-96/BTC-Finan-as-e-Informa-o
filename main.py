import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="O Conselho BTC", page_icon="🏛️", layout="centered", initial_sidebar_state="collapsed")

# Truque em CSS para esconder o menu e refinar os botões
st.markdown("""
    <style>
        /* Esconder o menu lateral na tela inicial */
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Estilizar os links para ficarem menores e mais elegantes */
        [data-testid="stPageLink-NavLink"] {
            background-color: rgba(128, 128, 128, 0.05); /* Mais transparente */
            border: 1px solid rgba(128, 128, 128, 0.2); /* Borda bem fina */
            border-radius: 6px; 
            padding: 8px 12px; /* Tamanho reduzido para não ficar desproporcional */
            margin-bottom: 8px;
            transition: all 0.3s ease; 
        }
        
        /* Efeito Hover */
        [data-testid="stPageLink-NavLink"]:hover {
            background-color: rgba(128, 128, 128, 0.15);
            border: 1px solid rgba(128, 128, 128, 0.5);
        }
    </style>
""", unsafe_allow_html=True)

# Sistema de Segurança
def check_password():
    def password_guessed():
        if st.session_state["password"] == "123": # Senha provisória de testes
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Insira sua chave de acesso à mesa de operações.</p>", unsafe_allow_html=True)
        
        st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
        st.error("Chave inválida. Acesso negado à tesouraria.")
        return False
    
    else:
        return True

# Função Blindada para buscar o preço do BTC
def obter_preco_btc():
    # Tentativa 1: API da Binance US (não bloqueia servidores americanos do Streamlit)
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3) # Timeout de 3 seg para não travar o site
        dados = resposta.json()
        return float(dados["price"])
    except:
        # Tentativa 2: Fallback para a API da CoinGecko caso a Binance caia
        try:
            url_reserva = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            resposta_reserva = requests.get(url_reserva, timeout=3)
            dados_reserva = resposta_reserva.json()
            return float(dados_reserva["bitcoin"]["usd"])
        except:
            return None

# O que aparece DEPOIS do login
if check_password():
    st.title("📊 Terminal de Operações")
    st.divider()
    
    st.markdown("<p style='text-align: center;'>Selecione um dos módulos abaixo para iniciar suas alocações e análises de mercado:</p>", unsafe_allow_html=True)
    
    # Criando colunas para "espremer" os botões no centro, deixando-os menores e mais chiques
    col_vazia1, col_botoes, col_vazia2 = st.columns([1, 2, 1])
    
    with col_botoes:
        st.page_link("pages/1_Calculadora.py", label="Calculadora de Margem", icon="🧮")
        st.page_link("pages/2_Portfolio.py", label="Portfólio e Custódia", icon="💼")
        st.page_link("pages/3_Conselho.py", label="Conselho e Inteligência", icon="🏛️")
    
    st.divider()
    
    # Secção da Cotação ao Vivo
    preco_btc = obter_preco_btc()
    
    if preco_btc:
        st.markdown("<h4 style='text-align: center;'>📡 Cotação Atualizada (BTC/USDT)</h4>", unsafe_allow_html=True)
        
        # Centralizando o valor do mercado
        _, col_preco, _ = st.columns([1, 2, 1])
        with col_preco:
            st.metric(label="Mercado Spot", value=f"${preco_btc:,.2f}")
    else:
        st.error("Sem conexão com o feed de dados do mercado no momento.")
