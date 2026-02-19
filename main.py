import streamlit as st

# Configuração da página
st.set_page_config(page_title="O Conselho BTC", page_icon="🏛️", layout="centered")

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

# O que aparece DEPOIS do login
if check_password():
    st.title("📊 Terminal de Operações")
    st.markdown("### Bem-vindo de volta, Gestor.")
    st.divider()
    
    st.markdown("Selecione um dos módulos abaixo para iniciar suas alocações e análises de mercado:")
    
    # Botões de navegação grandes e visíveis
    st.page_link("pages/1_Calculadora.py", label="Calculadora de Margem (Boleta)", icon="🧮")
    st.page_link("pages/2_Portfolio.py", label="Portfólio e Custódia", icon="💼")
    st.page_link("pages/3_Conselho.py", label="O Conselho (Inteligência de Mercado)", icon="🏛️")
    
    st.divider()
    
    # Status do mercado
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("📈 **Mercado Ativo**\n\nMonitoramento de liquidez e rastreamento de ativos habilitado.")
        
    with col2:
        st.success("🔒 **Segurança**\n\nConexão estabelecida. Patrimônio protegido.")
