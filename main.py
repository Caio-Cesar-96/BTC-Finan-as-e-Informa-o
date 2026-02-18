import streamlit as st

# 1. Configuração de Segurança Simples
def check_password():
    def password_guessed():
        if st.session_state["password"] == "suasenha123": # Altere sua senha aqui
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Senha de Acesso", type="password", on_change=password_guessed, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Senha de Acesso", type="password", on_change=password_guessed, key="password")
        st.error("Senha incorreta")
        return False
    else:
        return True

if check_password():
    st.title("🛰️ Jornal do BTC - Analista Chefe")
    
    # Menu Lateral
    menu = st.sidebar.selectbox("Navegação", ["Calculadora Rápida", "O Oráculo (Jornal)", "Meu Portfólio"])

    if menu == "Calculadora Rápida":
        st.header("🧮 Calculadora de Margem")
        
        col1, col2 = st.columns(2)
        with col1:
            investimento = st.number_input("Quanto você gastou (USDT)?", min_value=0.0, value=10.0)
            qtd_btc = st.number_input("Quanto BTC você comprou?", min_value=0.0, format="%.8f", value=0.000256)
        
        with col2:
            preco_venda = st.number_input("Preço de venda alvo (USDT)?", min_value=0.0, value=100000.0)
        
        valor_final = qtd_btc * preco_venda
        lucro_bruto = valor_final - investimento
        margem = (lucro_bruto / investimento) * 100

        st.divider()
        st.subheader(f"Resultado Estimado")
        st.write(f"Ao resgatar, você terá: **{valor_final:.2f} USDT**")
        st.metric("Lucro Líquido", f"{lucro_bruto:.2f} USDT", f"{margem:.2f}%")

    elif menu == "O Oráculo (Jornal)":
        st.header("📰 Edições do Jornal")
        st.info("Cole aqui o conteúdo gerado pelo seu Agente Gemini.")
        # Futuramente, automatizaremos para buscar do seu Drive
        edicao = st.text_area("Conteúdo da Edição", height=400)

    elif menu == "Meu Portfólio":
        st.header("💰 Meu Patrimônio")
        st.write("Seus dados protegidos e integrados ao seu Documento Regente.")
