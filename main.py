import streamlit as st

# Configuração da página de Login
st.set_page_config(page_title="Login - O Conselho", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

# Esconder o menu lateral se não estiver logado
if not st.session_state.get("autenticado", False):
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

def password_guessed():
    # Busca a chave nos Secrets ou usa a fallback temporária
    chave_correta = st.secrets.get("CHAVE_MESTRE", "CCSS-5454")
    
    if st.session_state["password"] == chave_correta:
        st.session_state["autenticado"] = True
        st.session_state["password_correct"] = True # Variável de legado para não quebrar o 0_Terminal.py antigo
        del st.session_state["password"]
    else:
        st.session_state["autenticado"] = False

# --- FLUXO DA TELA ---
if not st.session_state.get("autenticado", False):
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Insira sua chave de acesso à mesa de operações.</p>", unsafe_allow_html=True)
        
        st.text_input("Chave de Acesso", type="password", on_change=password_guessed, key="password")
        
        if "autenticado" in st.session_state and not st.session_state["autenticado"]:
            st.error("❌ Chave inválida. Acesso negado à tesouraria.")
else:
    # Quebra do Loop: Tela estática de sucesso aguardando ação manual do usuário
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.success("✅ Acesso Liberado.")
        st.write("Conexão estabelecida com a base de dados.")
        
        if st.button("Entrar no Terminal", type="primary", use_container_width=True):
            st.switch_page("pages/0_Terminal.py")
