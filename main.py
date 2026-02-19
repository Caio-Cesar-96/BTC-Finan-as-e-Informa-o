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
        
        /* Estilizar os links: efeito de vidro exato no tamanho do texto */
        [data-testid="stPageLink-NavLink"] {
            background-color: rgba(255, 255, 255, 0.03); /* Fundo de vidro bem sutil */
            border: 1px solid rgba(255, 255, 255, 0.1); /* Borda fininha */
            border-radius: 10px; 
            padding: 10px 20px; 
            margin: 0 auto 12px auto !important; /* Centraliza perfeitamente */
            width: fit-content !important; /* Faz o botão abraçar apenas o texto */
            transition: all 0.3s ease; 
        }
        
        /* Efeito Hover quando passa o mouse */
        [data-testid="stPageLink-NavLink"]:hover {
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            transform: translateY(-2px); /* Leve levantadinha 3D */
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

# O que aparece DEPOIS do login
if check_password():
    st.title("📊 Terminal de Operações")
    st.divider()
    
    st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Selecione um dos módulos abaixo para iniciar suas alocações e análises de mercado:</p>", unsafe_allow_html=True)
    
    # Removidas as colunas: O CSS agora garante que eles fiquem no centro e no tamanho perfeito
    st.page_link("pages/1_Calculadora.py", label="Calculadora de Margem", icon="🧮")
    st.page_link("pages/2_Portfolio.py", label="Portfólio e Custódia", icon="💼")
    st.page_link("pages/3_Conselho.py", label="Conselho e Inteligência", icon="🏛️")
    
    st.divider()
    
    # Secção da Cotação ao Vivo (Sem o rótulo extra)
    preco_btc = obter_preco_btc()
    
    if preco_btc:
        st.markdown("<p style='text-align: center; color: gray; margin-bottom: -15px;'>📡 Cotação Atualizada (BTC/USDT)</p>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-size: 3.5rem;'>${preco_btc:,.2f}</h1>", unsafe_allow_html=True)
    else:
        st.error("Sem conexão com o feed de dados do mercado no momento.")
