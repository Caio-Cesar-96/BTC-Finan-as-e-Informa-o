import streamlit as st
import requests

# 1. CONFIGURAÇÃO (Deve ser obrigatoriamente o 1º comando Streamlit)
st.set_page_config(page_title="O Conselho BTC", page_icon="🏛️", layout="wide", initial_sidebar_state="collapsed")

# 2. CADEADO DE SEGURANÇA: Verifica a nova variável da v2.3.0
if not st.session_state.get("autenticado", False):
    st.switch_page("main.py")

# O CSS com o design dos seus botões
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stPageLink"] {
            display: flex;
            justify-content: center;
            margin-bottom: 5px;
        }
        [data-testid="stPageLink-NavLink"] {
            background-color: rgba(255, 255, 255, 0.05) !important; 
            border: 1px solid rgba(255, 255, 255, 0.15) !important; 
            border-radius: 1px !important; 
            padding: 1px 4px !important; 
            width: 250px !important; 
            display: flex !important;
            justify-content: center !important; 
            transition: all 0.3s ease !important; 
        }
        [data-testid="stPageLink-NavLink"]:hover {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border: 1px solid rgba(255, 255, 255, 0.4) !important;
            transform: scale(1.02) !important; 
        }
    </style>
""", unsafe_allow_html=True)

def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3) 
        dados = resposta.json()
        return float(dados["price"])
    except:
        try:
            url_reserva = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
            resposta_reserva = requests.get(url_reserva, timeout=3)
            dados_reserva = resposta_reserva.json()
            return float(dados_reserva["bitcoin"]["usd"])
        except:
            return None

col_titulo, col_sair = st.columns([8, 2], vertical_alignment="center")
with col_titulo:
    st.title("📊 Terminal de Operações")
with col_sair:
    if st.button("🚪 Sair", use_container_width=True):
        st.session_state.clear() # Limpa a memória
        st.switch_page("main.py")
st.divider()

st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Selecione um dos módulos abaixo para iniciar suas alocações e análises de mercado:</p>", unsafe_allow_html=True)

st.page_link("pages/1_Calculadora.py", label="Calculadora de Margem", icon="🧮")
st.page_link("pages/2_Portfolio.py", label="Portfólio e Custódia", icon="💼")
st.page_link("pages/3_Conselho.py", label="Conselho e Inteligência", icon="🏛️")

st.divider()

preco_btc = obter_preco_btc()

if preco_btc:
    st.markdown("<p style='text-align: center; color: gray; margin-bottom: -15px;'>📡 Cotação Atualizada (BTC/USDT)</p>", unsafe_allow_html=True)
    st.markdown(f"<h1 style='text-align: center; font-size: 3.5rem;'>${preco_btc:,.2f}</h1>", unsafe_allow_html=True)
else:
    st.error("Sem conexão com o feed de dados do mercado no momento.")
