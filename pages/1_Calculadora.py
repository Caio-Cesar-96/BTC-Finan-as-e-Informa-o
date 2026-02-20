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

# --- GERENCIAMENTO DE MEMÓRIA ---
if 'transacoes_abertas' not in st.session_state: st.session_state['transacoes_abertas'] = []
if 'saldo_bnb' not in st.session_state: st.session_state['saldo_bnb'] = 0.0 
if 'saldo_configurado' not in st.session_state: st.session_state['saldo_configurado'] = False
if 'historico_taxas_bnb' not in st.session_state: st.session_state['historico_taxas_bnb'] = []

col_boleta, col_espaco, col_tesouraria = st.columns([5, 1, 3])

# ==========================================
# COLUNA DA DIREITA: TESOURARIA (BNB)
# ==========================================
with col_tesouraria:
    st.subheader("🔶 Tesouraria (BNB)")
    
    # Sistema Novo: Trava de Saldo com Botão "Aplicar"
    if not st.session_state['saldo_configurado']:
        st.markdown("Defina o seu saldo inicial reservado para taxas:")
        # Digite aqui o equivalente aos 5 USDT em BNB (ex: 0.008 BNB)
        saldo_input = st.number_input("Inserir Saldo (BNB)", min_value=0.0, step=0.001, format="%.8f")
        
        if st.button("Aplicar Saldo", type="primary", use_container_width=True):
            st.session_state['saldo_bnb'] = saldo_input
            st.session_state['saldo_configurado'] = True
            st.rerun()
    else:
        # Mostra o saldo de forma destacada, subtraindo centavinhos a cada transação
        st.metric(label="Saldo Atual Disponível", value=f"{st.session_state['saldo_bnb']:.8f} BNB")
        if st.button("⚙️ Reajustar Saldo Inicial", use_container_width=True):
            st.session_state['saldo_configurado'] = False
            st.rerun()
            
    usar_bnb = st.toggle("Pagar taxas com BNB (-25%)", value=True)
    
    preco_bnb_atual = obter_preco_bnb()
    st.caption(f"📡 Cotação atual BNB/USDT: **${preco_bnb_atual:,.2f}**")
    
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

# ==========================================
# COLUNA DA ESQUERDA: FORMULÁRIO DE ORDEM
# ==========================================
with col_boleta:
    with st.form(key="form_boleta"):
        st.subheader("Nova Ordem")
        
        c1, c2 = st.columns(2)
        with c1:
            tipo_operacao = st.selectbox("Tipo de Ordem", ["Compra", "Venda"])
            quantidade = st.number_input("Quantidade de BTC", min_value=0.00000000, format="%.8f", step=0.001)
            
        with c2:
            preco_execucao = st.number_input("Preço de Execução (USDT)", min_value=0.0, step=100.0)
            data_hora = st.date_input("Data da Operação", datetime.date.today(), format="DD/MM/YYYY")
            
        submit = st.form_submit_button("Executar Ordem e Gerar Canhoto")

# --- LÓGICA DE PROCESSAMENTO ---
if submit:
    if quantidade > 0 and preco_execucao > 0:
        valor_total_usdt = quantidade * preco_execucao
        id_operacao = str(uuid.uuid4())[:8].upper()
        
        taxa_percentual = 0.100 
        custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
        custo_taxa_bnb = 0.0
        
        if usar_bnb:
            taxa_percentual = 0.075
            custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
            
            custo_taxa_bnb = custo_taxa_usdt / preco_bnb_atual
            
            # Bloqueio de segurança: Só debita se o saldo existir na memória
            if st.session_state['saldo_bnb'] >= custo_taxa_bnb:
                st.session_state['saldo_bnb'] -= custo_taxa_bnb 
                
                st.session_state['historico_taxas_bnb'].append({
                    "id_transacao": id_operacao,
                    "qtd_bnb": custo_taxa_bnb
                })
                st.success(f"✅ Ordem registrada! Taxa de {custo_taxa_bnb:.8f} BNB debitada da Tesouraria.")
            else:
                st.warning("⚠️ Saldo de BNB insuficiente para a taxa. A ordem foi registrada cobrando a taxa cheia em USDT.")
                taxa_percentual = 0.100
                custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
                custo_taxa_bnb = 0.0
        else:
            st.success("✅ Ordem registrada com taxa cheia em USDT.")

        nova_transacao = {
            "id": id_operacao,
            "tipo": tipo_operacao,
            "data": data_hora.strftime("%d/%m/%Y"),
            "quantidade_btc": quantidade,
            "preco_usdt": preco_execucao,
            "valor_total": valor_total_usdt,
            "taxa_percentual": taxa_percentual,
            "taxa_paga_usdt": custo_taxa_usdt,
            "taxa_paga_bnb": custo_taxa_bnb,
            "status": "Aguardando Fechamento"
        }
        st.session_state['transacoes_abertas'].append(nova_transacao)
        
        st.rerun() 
        
    else:
        st.error("Atenção: A quantidade e o preço devem ser maiores que zero.")

st.divider()

# --- ÁREA INFERIOR: CANHOTOS ---
st.subheader("Ordens em Aberto (Cache de Sessão)")
if st.session_state['transacoes_abertas']:
    for t in st.session_state['transacoes_abertas']:
        cor = "🟢" if "Compra" == t['tipo'] else "🔴"
        
        # Ajuste: Removida a informação da taxa do canhoto, deixando-o mais limpo
        st.info(f"{cor} **{t['tipo']}** | Data: {t['data']} | {t['quantidade_btc']} BTC a ${t['preco_usdt']:,.2f} | Ref: {t['id']}")
else:
    st.write("Nenhuma ordem aguardando consolidação no momento.")
