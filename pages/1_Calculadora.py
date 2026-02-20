import streamlit as st
import datetime
import uuid
import requests

st.set_page_config(page_title="Calculadora - O Conselho", page_icon="🧮", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stPageLink-NavLink"] {
            width: fit-content;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        button[kind="primary"] {
            background-color: #F3BA2F !important;
            color: #000000 !important;
            border: none !important;
            font-weight: bold !important;
            transition: all 0.3s ease !important;
        }
        button[kind="primary"]:hover {
            background-color: #DDA221 !important;
            transform: scale(1.02) !important;
        }
    </style>
""", unsafe_allow_html=True)

def obter_preco_bnb():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BNBUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 600.0 

st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="⬅️")

st.title("🧮 Boleta de Operações")
st.divider()

if 'transacoes_abertas' not in st.session_state: st.session_state['transacoes_abertas'] = []
if 'saldo_bnb' not in st.session_state: st.session_state['saldo_bnb'] = 0.0 
if 'saldo_configurado' not in st.session_state: st.session_state['saldo_configurado'] = False
if 'historico_taxas_bnb' not in st.session_state: st.session_state['historico_taxas_bnb'] = []

col_boleta, col_espaco, col_tesouraria = st.columns([5, 1, 3])

with col_tesouraria:
    st.subheader("🔶 Tesouraria (BNB)")
    
    if not st.session_state['saldo_configurado']:
        st.markdown("Defina o seu saldo inicial reservado para taxas:")
        saldo_input = st.number_input("Inserir Saldo (BNB)", min_value=0.0, step=0.001, format="%.8f")
        
        if st.button("Aplicar Saldo", type="primary", use_container_width=True):
            st.session_state['saldo_bnb'] = saldo_input
            st.session_state['saldo_configurado'] = True
            st.rerun()
    else:
        st.metric(label="Saldo Atual Disponível", value=f"{st.session_state['saldo_bnb']:.8f} BNB")
        if st.button("⚙️ Reajustar Saldo Inicial", use_container_width=True):
            st.session_state['saldo_configurado'] = False
            st.rerun()
    
    st.markdown("---")
    
    # Criando duas colunas para colocar a etiqueta colorida ao lado do botão
    col_toggle, col_badge = st.columns([3, 2])
    
    # O botão agora tem o texto limpo
    usar_bnb = col_toggle.toggle("Pagar taxas com BNB", value=True)
    
    # A etiqueta colorida muda instantaneamente baseada no botão
    with col_badge:
        if usar_bnb:
            st.markdown("<div style='background-color: #15803d; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.075%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #eab308; color: black; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.100%</div>", unsafe_allow_html=True)
    
    preco_bnb_atual = obter_preco_bnb()
    st.caption(f"📡 Cotação atual BNB/USDT: **{preco_bnb_atual:,.2f} USDT**")
    
    st.markdown("---")
    st.markdown("**📋 Últimos Débitos de Taxa**")
    if st.session_state['historico_taxas_bnb']:
        for h in reversed(st.session_state['historico_taxas_bnb'][-5:]):
            st.caption(f"🔻 -{h['qtd_bnb']:.8f} BNB (Ref: {h['id_transacao']})")
    else:
        st.caption("Nenhuma taxa deduzida ainda.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Histórico de Testes", use_container_width=True):
        st.session_state['transacoes_abertas'] = []
        st.session_state['historico_taxas_bnb'] = []
        st.session_state['saldo_bnb'] = 0.0
        st.session_state['saldo_configurado'] = False
        st.rerun()

with col_boleta:
    with st.container(border=True):
        st.subheader("Nova Ordem")
        
        c1, c2 = st.columns(2)
        with c1:
            tipo_operacao = st.selectbox("Tipo de Ordem", ["Compra", "Venda"])
            quantidade = st.number_input("Quantidade Bruta de BTC", min_value=0.00000000, format="%.8f", step=0.001)
            
        with c2:
            preco_execucao = st.number_input("Cotação de 1 BTC (Preço de Execução)", min_value=0.0, step=100.0)
            data_hora = st.date_input("Data da Operação", datetime.date.today(), format="DD/MM/YYYY")
            
        valor_total_usdt = quantidade * preco_execucao
        st.info(f"💵 **Valor Total da Operação:** {valor_total_usdt:,.2f} USDT")
        
        if usar_bnb and not st.session_state['saldo_configurado']:
            st.warning("⚠️ **Atenção:** O desconto BNB está ativo, mas você ainda não configurou a Tesouraria.")

        submit = st.button("Executar Ordem e Gerar Canhoto", type="primary", use_container_width=True)

if submit:
    if usar_bnb and not st.session_state['saldo_configurado']:
        st.error("🛑 **Operação Bloqueada:** Você ativou o pagamento em BNB, mas esqueceu de aplicar o saldo na Tesouraria. Por favor, insira o saldo ao lado e clique em 'Aplicar', ou desative a opção de desconto.")
    
    elif quantidade > 0 and preco_execucao > 0:
        id_operacao = str(uuid.uuid4())[:8].upper()
        
        taxa_percentual = 0.100 
        custo_taxa_bnb = 0.0
        recebido_liquido = 0.0
        moeda_recebida = "BTC" if tipo_operacao == "Compra" else "USDT"
        info_taxa = ""
        
        if usar_bnb:
            taxa_percentual = 0.075
            custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
            custo_taxa_bnb = custo_taxa_usdt / preco_bnb_atual
            
            if st.session_state['saldo_bnb'] >= custo_taxa_bnb:
                st.session_state['saldo_bnb'] -= custo_taxa_bnb 
                st.session_state['historico_taxas_bnb'].append({
                    "id_transacao": id_operacao,
                    "qtd_bnb": custo_taxa_bnb
                })
                st.success(f"✅ Ordem registrada! Taxa debitada da Tesouraria.")
                
                recebido_liquido = quantidade if tipo_operacao == "Compra" else valor_total_usdt
                info_taxa = "Taxa paga em BNB"
            else:
                st.warning("⚠️ Saldo de BNB insuficiente. Taxa cheia cobrada na moeda recebida.")
                taxa_percentual = 0.100
                usar_bnb = False 
                
        if not usar_bnb:
            st.success("✅ Ordem registrada com taxa cheia na moeda recebida.")
            if tipo_operacao == "Compra":
                taxa_na_moeda = quantidade * (taxa_percentual / 100)
                recebido_liquido = quantidade - taxa_na_moeda 
                info_taxa = f"Taxa de {taxa_na_moeda:.8f} BTC descontada"
            else:
                taxa_na_moeda = valor_total_usdt * (taxa_percentual / 100)
                recebido_liquido = valor_total_usdt - taxa_na_moeda 
                info_taxa = f"Taxa de {taxa_na_moeda:.2f} USDT descontada"

        nova_transacao = {
            "id": id_operacao,
            "tipo": tipo_operacao,
            "data": data_hora.strftime("%d/%m/%Y"),
            "quantidade_bruta_btc": quantidade,
            "preco_usdt": preco_execucao,
            "recebido_liquido": recebido_liquido,
            "moeda_recebida": moeda_recebida,
            "info_taxa": info_taxa,
            "status": "Aguardando Fechamento"
        }
        st.session_state['transacoes_abertas'].append(nova_transacao)
        st.rerun() 
        
    else:
        st.error("Atenção: A quantidade e a cotação devem ser maiores que zero.")

st.divider()

st.subheader("Ordens em Aberto (Cache de Sessão)")
if st.session_state['transacoes_abertas']:
    for t in st.session_state['transacoes_abertas']:
        cor = "🟢" if "Compra" == t['tipo'] else "🔴"
        
        st.info(f"{cor} **{t['tipo']}** de {t['quantidade_bruta_btc']} BTC a {t['preco_usdt']:,.2f} USDT | **Entrou na Carteira: {t['recebido_liquido']:.8f} {t['moeda_recebida']}** | *{t['info_taxa']}* | Ref: {t['id']}")
else:
    st.write("Nenhuma ordem aguardando consolidação no momento.")
