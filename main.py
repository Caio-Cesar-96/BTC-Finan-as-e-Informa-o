import streamlit as st
from supabase import create_client, Client

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Login - O Conselho", page_icon="🔒", layout="centered", initial_sidebar_state="collapsed")

# Esconder menu lateral se não estiver autenticado
if not st.session_state.get("autenticado", False):
    st.markdown("""
        <style>
            [data-testid="collapsedControl"] {display: none;}
            [data-testid="stSidebar"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def iniciar_conexao():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = iniciar_conexao()
except Exception as e:
    st.error("⚠️ Erro ao conectar com o Banco de Dados. Verifique os Secrets.")
    st.stop()

# --- FLUXO DA TELA ---
if not st.session_state.get("autenticado", False):
    _, col_main, _ = st.columns([1, 2, 1])
    
    with col_main:
        st.markdown("<h1 style='text-align: center;'>🏛️ O Conselho</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: gray;'>Terminal de Operações Restrito</p>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
        # ABA 1: LOGIN
        with aba_login:
            email_login = st.text_input("E-mail", key="email_log")
            senha_login = st.text_input("Senha", type="password", key="senha_log")
            btn_login = st.button("Acessar Terminal", type="primary", use_container_width=True)
            
            if btn_login:
                if email_login and senha_login:
                    try:
                        # Autenticação oficial no Supabase
                        resposta = supabase.auth.sign_in_with_password({"email": email_login, "password": senha_login})
                        st.session_state["autenticado"] = True
                        st.session_state["user_id"] = resposta.user.id # SALVANDO A IDENTIDADE DO USUÁRIO
                        st.rerun()
                    except Exception as e:
                        st.error("❌ E-mail ou senha incorretos.")
                else:
                    st.warning("Preencha todos os campos.")
        
        # ABA 2: CADASTRO COM CHAVE MESTRA
        with aba_cadastro:
            email_cad = st.text_input("Novo E-mail", key="email_cad")
            senha_cad = st.text_input("Criar Senha", type="password", key="senha_cad")
            senha_conf = st.text_input("Repita a Senha", type="password", key="senha_conf")
            chave_mestra = st.text_input("Chave de Convite (Master Key)", type="password", key="chave_cad")
            btn_cadastrar = st.button("Criar Credencial", type="primary", use_container_width=True)
            
            if btn_cadastrar:
                chave_correta = st.secrets.get("CHAVE_MESTRE", "CCSS-5454")
                
                if chave_mestra != chave_correta:
                    st.error("❌ Chave de convite inválida.")
                elif senha_cad != senha_conf:
                    st.error("❌ As senhas não coincidem.")
                elif len(senha_cad) < 6:
                    st.error("❌ A senha deve ter pelo menos 6 caracteres.")
                elif email_cad and senha_cad:
                    try:
                        # Criação oficial de usuário no Supabase
                        resposta = supabase.auth.sign_up({"email": email_cad, "password": senha_cad})
                        st.success("✅ Conta criada com sucesso! Você já pode fazer o login na aba ao lado.")
                    except Exception as e:
                        st.error(f"❌ Erro detalhado do Supabase: {e}")
                else:
                    st.warning("Preencha todos os campos.")

# SE JÁ ESTIVER LOGADO
else:
    _, col_login, _ = st.columns([1, 2, 1])
    with col_login:
        st.success("✅ Acesso Liberado.")
        st.write("Conexão estabelecida e criptografada.")
        
        if st.button("Entrar no Terminal", type="primary", use_container_width=True):
            st.switch_page("pages/0_Terminal.py")
            
        if st.button("Sair (Logout)", type="secondary", use_container_width=True):
            supabase.auth.sign_out()
            st.session_state["autenticado"] = False
            st.session_state["user_id"] = None
            st.rerun()
