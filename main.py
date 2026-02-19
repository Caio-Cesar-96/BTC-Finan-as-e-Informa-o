import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="O Conselho BTC", page_icon="🏛️", layout="centered", initial_sidebar_state="collapsed")

# Truque em CSS para esconder o menu e estilizar os botões
st.markdown("""
    <style>
        /* Esconder o menu lateral */
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Estilizar os links de página para parecerem botões elegantes e semitransparentes */
        [data-testid="stPageLink-NavLink"] {
            background-color: rgba(128, 128, 128, 0.08); /* Fundo leve e transparente */
            border: 1px solid rgba(128, 128, 128, 0.2); /* Borda muito subtil */
            border-radius: 8px; /* Cantos arredondados */
            padding: 12px 15px;
            margin-bottom: 10px;
            transition: all 0.3s ease; /* Transição suave */
        }
        
        /* Efeito quando o rato passa por cima (Hover) */
        [data-testid="stPageLink-NavLink"]:hover {
            background-color: rgba(128, 128, 128, 0.15);
            border: 1px solid rgba(128, 128, 128, 0.4);
        }
    </style>
""", unsafe_allow_html=True)

# Sistema de Segurança
def check_password():
    def password_guessed():
        if st.session_state["password"] == "123": # Senha de testes rápida
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

# Função para ir buscar o preço do BTC na Binance
def obter_preco_btc():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url)
        dados = resposta.json()
        return float(dados["price"])
    except:
        return None

# O que aparece DEPOIS do login
if check_password():
    st.title("📊 Terminal de Operações")
    st.divider()
    
    st.markdown("Selecione um dos módulos abaixo para iniciar suas alocações e análises de mercado:")
    
    # Botões de navegação
    st.page_link("pages/1_Calculadora.py", label="Calculadora de Margem", icon="🧮")
    st.page_link("pages/2_Portfolio.py", label="Portfólio e Custódia", icon="💼")
    st.page_link("pages/3_Conselho.py", label="Conselho e Inteligência de Mercado", icon="🏛️")
    
    st.divider()
    
    # Secção da Cotação ao Vivo
    preco_btc = obter_preco_btc()
    
    if preco_btc:
        st.markdown("<h4 style='text-align: center;'>📡 Cotação em Tempo Real (Binance)</h4>", unsafe_allow_html=True)
        # Usar colunas para centralizar o bloco de preço
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.metric(label="Bitcoin (BTC/USDT)", value=f"${preco_btc:,.2f}")
    else:
        st.warning("Aguardando conexão com a API da Binance...")
