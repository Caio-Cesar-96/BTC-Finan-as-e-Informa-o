import streamlit as st
import datetime
import uuid
import requests

# Layout "wide" mantido
st.set_page_config(page_title="Calculadora - O Conselho", page_icon="🧮", layout="wide", initial_sidebar_state="collapsed")

# CSS para esconder o menu lateral e estilizar o botão
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

# Função para buscar o preço do BNB
def obter_preco_bnb():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BNBUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 600.0 # Valor reserva caso a API falhe

# Botão agora aponta para o novo Terminal
st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="⬅️")

st.title("🧮 Boleta de Operações")
st.divider()

# --- GERENCIAMENTO DE MEMÓRIA ---
if 'transacoes_abertas' not in st.session_state: st.session_state['transacoes_abertas'] = []
if 'saldo_bnb' not in st.session_state: st.session_state['saldo_bnb'] = 5.0 
if 'historico_taxas_bnb' not in st.session_state: st.session_state['historico_taxas_bnb'] = []

# --- DIVISÃO DA TELA ---
col_boleta, col_espaco, col_tesouraria = st.columns([5, 1, 3])

# ==========================================
# COLUNA DA DIREITA: TESOURARIA (BNB)
# ==========================================
with col_tesouraria:
    # Ajuste visual: Losango para simular a logo da BNB
    st.subheader("🔶 Tesouraria (BNB)")
    
    # Ajuste Matemático: Formatado para 8 casas decimais (padrão cripto)
    novo_saldo = st.number_input("Saldo Disponível (BNB)", min_value=0.0, value=float(st.session_state['saldo_bnb']), step=0.01, format="%.8f")
    if novo_saldo != st.session_state['saldo_bnb']:
        st.session_state['saldo_bnb'] = novo_saldo 
        
    usar_bnb = st.toggle("Pagar taxas com BNB (-25%)", value=True)
    
    preco_bnb_atual = obter_preco_bnb()
    st.caption(f"📡 Cotação atual BNB/USDT: **${preco_bnb_atual:,.2f}**")
    
    st.markdown("---")
    st.markdown("**📋 Últimos Débitos de Taxa**")
    if st.session_state['historico_taxas_bnb']:
        for h in reversed(st.session_state['historico_taxas_bnb'][-5:]):
            # Histórico também forçado a exibir 8 casas decimais
            st.caption(f"🔻 -{h['qtd_bnb']:.8f} BNB (Ref: {h['id_transacao']})")
    else:
        st.caption("Nenhuma taxa deduzida ainda.")

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
        
        if usar_bnb:
            taxa_percentual = 0.075
            custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
            
            # Conversão
            custo_taxa_bnb = custo_taxa_usdt / preco_bnb_atual
            
            if st.session_state['saldo_bnb'] >= custo_taxa_bnb:
                st.session_state['saldo_bnb'] -= custo_taxa_bnb 
                
                st.session_state['historico_taxas_bnb'].append({
                    "id_transacao": id_operacao,
                    "qtd_bnb": custo_taxa_bnb
                })
                st.success(f"✅ Ordem registrada! Taxa de {custo_taxa_bnb:.8f} BNB debitada do saldo.")
            else:
                st.warning(f"⚠️ Saldo de BNB insuficiente para a taxa. A ordem foi registrada cobrando a taxa cheia em USDT.")
                taxa_percentual = 0.100
                custo_taxa_usdt = valor_total_usdt * (taxa_percentual / 100)
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
        st.info(f"{cor} **{t['tipo']}** | Data: {t['data']} | {t['quantidade_btc']} BTC a ${t['preco_usdt']:,.2f} | Ref: {t['id']}")
else:
    st.write("Nenhuma ordem aguardando consolidação no momento.")
