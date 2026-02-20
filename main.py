import streamlit as st

# Configuração da página de Login
st.set_page_config(page_title="Login - O Conselho", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

# Esconder o menu lateral na tela de login
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

def check_password():
    def password_guessed():
        if st.session_state["password"] == "123": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        _, col_login, _ = st.columns([1, 2, 1])
        with col_login:
            st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Insira sua chave de acesso à mesa de operações.</p>", unsafe_allow_html=True)
            st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        _, col_login, _ = st.columns([1, 2, 1])
        with col_login:
            st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
            st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
            st.error("Chave inválida. Acesso negado à tesouraria.")
        return False
    
    else:
        return True

# Se a senha estiver correta, TELETRANSPORTA para o Terminal
if check_password():
    st.switch_page("pages/0_Terminal.py")
