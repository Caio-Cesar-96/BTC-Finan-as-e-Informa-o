import streamlit as st
import datetime
import uuid

# Configuração da página
st.set_page_config(page_title="Calculadora - O Conselho", page_icon="🧮", layout="centered", initial_sidebar_state="collapsed")

# CSS para esconder o menu lateral também nesta página
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Estilo para o botão de voltar não ficar gigante */
        [data-testid="stPageLink-NavLink"] {
            width: fit-content;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Botão para voltar à tela inicial livremente
st.page_link("main.py", label="Voltar ao Terminal", icon="⬅️")

st.title("🧮 Boleta de Operações")
st.markdown("Registre suas ordens. O Conselho fará a custódia e o cálculo de margem no seu Portfólio.")
st.divider()

# Criando a "memória" do aplicativo para guardar as transações
if 'transacoes_abertas' not in st.session_state:
    st.session_state['transacoes_abertas'] = []

# Formulário de Inserção de Dados
with st.form(key="form_boleta"):
    st.subheader("Nova Ordem")
    
    col1, col2 = st.columns(2)
    with col1:
        # Ajuste 1: Somente Compra e Venda
        tipo_operacao = st.selectbox("Tipo de Ordem", ["Compra", "Venda"])
        quantidade = st.number_input("Quantidade de BTC", min_value=0.00000000, format="%.8f", step=0.001)
        
    with col2:
        preco_execucao = st.number_input("Preço de Execução (USDT)", min_value=0.0, step=100.0)
        # Ajuste 2: Formato de data PT-BR (DD/MM/YYYY)
        data_hora = st.date_input("Data da Operação", datetime.date.today(), format="DD/MM/YYYY")
        
    st.markdown("---")
    st.markdown("### Configuração de Taxas (Binance)")
    # Toggle para a taxa da Binance
    usar_bnb = st.toggle("Deduzir taxas usando BNB (Desconto de 25%)", value=True)
    
    # Botão para enviar o formulário
    submit = st.form_submit_button("Executar Ordem e Gerar Canhoto")

# Lógica de Processamento e Taxas
if submit:
    if quantidade > 0 and preco_execucao > 0:
        # A taxa padrão da Binance spot é 0.100%. Com BNB cai para 0.075%
        taxa_percentual = 0.075 if usar_bnb else 0.100
        
        valor_total_usdt = quantidade * preco_execucao
        custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
        
        # Criando o canhoto/recibo provisório
        nova_transacao = {
            "id": str(uuid.uuid4())[:8].upper(), # Gera um código único (ex: 4F9A2B1C)
            "tipo": tipo_operacao,
            "data": data_hora.strftime("%d/%m/%Y"),
            "quantidade_btc": quantidade,
            "preco_usdt": preco_execucao,
            "valor_total": valor_total_usdt,
            "taxa_percentual": taxa_percentual,
            "taxa_paga_usdt": custo_taxa_usdt,
            "status": "Aguardando Fechamento"
        }
        
        # Salvando na memória
        st.session_state['transacoes_abertas'].append(nova_transacao)
        st.success(f"✅ Ordem registrada com sucesso! (ID da Boleta: {nova_transacao['id']})")
    else:
        st.error("Atenção: A quantidade e o preço de execução devem ser maiores que zero.")

st.divider()

# Visualização Rápida do que está no cache da sessão
st.subheader("Ordens em Aberto (Cache de Sessão)")
if st.session_state['transacoes_abertas']:
    for t in st.session_state['transacoes_abertas']:
        cor = "🟢" if "Compra" == t['tipo'] else "🔴"
        st.info(f"{cor} **{t['tipo']}** | Data: {t['data']} | {t['quantidade_btc']} BTC a ${t['preco_usdt']:,.2f} | Taxa Paga: ${t['taxa_paga_usdt']:.2f}")
else:
    st.write("Nenhuma ordem aguardando consolidação.")
