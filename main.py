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
        # Busca a chave nos Secrets. Se o arquivo não estiver configurado, usa a fallback provisória.
        chave_correta = st.secrets.get("CHAVE_MESTRE", "CCSS-5454")
        
        if st.session_state["password"] == chave_correta:
            st.session_state["autenticado"] = True
            del st.session_state["password"]  # Limpa a senha da memória por segurança
        else:
            st.session_state["autenticado"] = False

    # Se a variável 'autenticado' não existir ou for False, exibe a tela de login
    if not st.session_state.get("autenticado", False):
        _, col_login, _ = st.columns([1, 2, 1])
        with col_login:
            st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Insira sua chave de acesso à mesa de operações.</p>", unsafe_allow_html=True)
            
            # O input aciona a função password_guessed ao apertar Enter
            st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
            
            # Se a tentativa de senha foi feita e registrada como False, exibe o erro
            if "autenticado" in st.session_state and not st.session_state["autenticado"]:
                st.error("❌ Chave inválida. Acesso negado à tesouraria.")
        return False
    else:
        return True

# Execução do fluxo principal
if check_password():
    # Redireciona para o Terminal após a autenticação
    st.switch_page("pages/0_Terminal.py")
