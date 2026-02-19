import streamlit as st

# Configuração da página e ícone da aba do navegador
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
        # Layout elegante para o login
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Identifique-se para acessar o terminal operacional.</p>", unsafe_allow_html=True)
        
        st.text_input("Credencial de Acesso", type="password", on_change=password_guessed, key="password")
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.text_input("Credencial de Acesso", type="password", on_change=password_guessed, key="password")
        st.error("Credencial inválida. O Conselho nega a sua entrada.")
        return False
    
    else:
        return True

# O que aparece DEPOIS que você digita a senha certa
if check_password():
    st.title("🏛️ Quartel General")
    st.markdown("### Bem-vindo de volta, Analista Chefe.")
    st.divider()
    
    # Organizando as informações em blocos visuais elegantes
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("👈 **Navegação do Sistema**\n\nUtilize o menu lateral para acessar as ferramentas do Conselho, registrar operações na **Calculadora** e consultar seu **Portfólio**.")
        
    with col2:
        st.success("📡 **Status do Sistema**\n\nConexão segura. Agentes prontos para compilação de dados e análises de mercado.")
