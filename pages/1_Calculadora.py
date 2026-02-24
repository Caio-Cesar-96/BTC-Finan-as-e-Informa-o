import streamlit as st
import datetime
import uuid
import requests
import copy

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
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px 5px 0px 0px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-bottom: 2px solid #F3BA2F !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE API ---
def obter_preco_bnb():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BNBUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 600.0 

def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 65000.0

# --- FUSO HORÁRIO (BRASÍLIA) ---
fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))

st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="⬅️")

st.title("🧮 Boleta de Operações")
st.divider()

if 'ordens_abertas' not in st.session_state: st.session_state['ordens_abertas'] = []
if 'historico_fechado' not in st.session_state: st.session_state['historico_fechado'] = []
if 'saldo_bnb' not in st.session_state: st.session_state['saldo_bnb'] = 0.0 
if 'saldo_configurado' not in st.session_state: st.session_state['saldo_configurado'] = False
if 'historico_taxas_bnb' not in st.session_state: st.session_state['historico_taxas_bnb'] = []
if 'pilha_desfazer' not in st.session_state: st.session_state['pilha_desfazer'] = [] # O cérebro do botão Desfazer

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
    col_toggle, col_badge = st.columns([3, 2])
    usar_bnb = col_toggle.toggle("Pagar taxas com BNB", value=True)
    
    with col_badge:
        if usar_bnb:
            st.markdown("<div style='background-color: #15803d; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.075%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #eab308; color: black; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.100%</div>", unsafe_allow_html=True)
    
    preco_bnb_atual = obter_preco_bnb()
    st.caption(f"📡 Cotação atual BNB/USDT: **\${preco_bnb_atual:,.2f}**")

with col_boleta:
    aba_compra, aba_venda = st.tabs(["🛒 Abrir Ordem", "🎯 Fechar Ordem"])
    
    # ==========================================
    # ABA 1: ABRIR ORDEM (COMPRA)
    # ==========================================
    with aba_compra:
        with st.container(border=True):
            preco_btc_atual = obter_preco_btc()
            
            st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #9ca3af; font-size: 0.95em;">Cotação Atual do Bitcoin (BTC/USDT)</span>
                    <strong style="font-size: 1.3em; color: #F3BA2F;">&#36;{preco_btc_atual:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                valor_total_usdt = st.number_input("Valor da Operação (USDT)", min_value=0.0, format="%.2f", step=10.0, key="val_compra")
            with c2:
                preco_execucao = st.number_input("Cotação de 1 BTC (Preço de Execução)", min_value=0.0, step=100.0, key="preco_compra")
                
            quantidade = 0.0
            if preco_execucao > 0:
                quantidade = valor_total_usdt / preco_execucao
                
            st.info(f"**Quantidade Bruta Estimada:** {quantidade:.8f} BTC")
            
            if usar_bnb and not st.session_state['saldo_configurado']:
                st.warning("⚠️ **Atenção:** O desconto BNB está ativo, mas você ainda não configurou a Tesouraria.")

            submit_compra = st.button("Executar Compra e Abrir Ordem", type="primary", use_container_width=True)

            if submit_compra:
                if usar_bnb and not st.session_state['saldo_configurado']:
                    st.error("🛑 Operação Bloqueada: Aplique saldo na Tesouraria ou desative o desconto.")
                elif valor_total_usdt > 0 and preco_execucao > 0:
                    id_operacao = str(uuid.uuid4())[:8].upper()
                    agora = datetime.datetime.now(fuso_brasilia)
                    
                    taxa_entrada_usdt = valor_total_usdt * (0.00075 if usar_bnb else 0.001)
                    usou_bnb_real = False
                    custo_bnb = 0.0
                    
                    if usar_bnb:
                        custo_bnb = taxa_entrada_usdt / preco_bnb_atual
                        if st.session_state['saldo_bnb'] >= custo_bnb:
                            st.session_state['saldo_bnb'] -= custo_bnb 
                            st.session_state['historico_taxas_bnb'].append({"id_transacao": id_operacao, "qtd_bnb": custo_bnb})
                            usou_bnb_real = True
                        else:
                            usar_bnb = False
                            taxa_entrada_usdt = valor_total_usdt * 0.001
                    
                    nova_ordem = {
                        "id": id_operacao,
                        "data_abertura": agora.strftime("%Y-%m-%d"),
                        "hora_abertura": agora.strftime("%H:%M"),
                        "data_abertura_br": agora.strftime("%d/%m/%Y"), 
                        "valor_investido_usdt": valor_total_usdt,
                        "quantidade_btc": quantidade if usar_bnb else quantidade - (quantidade * 0.001), 
                        "preco_compra": preco_execucao,
                        "taxa_entrada_usdt": taxa_entrada_usdt,
                        "status": "Aberto"
                    }
                    st.session_state['ordens_abertas'].append(nova_ordem)
                    
                    # Salvando na Pilha de Desfazer
                    st.session_state['pilha_desfazer'].append({
                        'acao': 'compra',
                        'id_ordem': id_operacao,
                        'usou_bnb': usou_bnb_real,
                        'custo_bnb': custo_bnb
                    })
                    st.rerun()

    # ==========================================
    # ABA 2: FECHAR ORDEM (VENDA)
    # ==========================================
    with aba_venda:
        with st.container(border=True):
            if not st.session_state['ordens_abertas']:
                st.info("Nenhuma ordem aberta no momento para realizar fechamento.")
            else:
                preco_btc_atual_venda = obter_preco_btc()
                
                st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="color: #9ca3af; font-size: 0.95em;">Cotação Atual do Bitcoin (BTC/USDT)</span>
                        <strong style="font-size: 1.3em; color: #F3BA2F;">&#36;{preco_btc_atual_venda:,.2f}</strong>
                    </div>
                """, unsafe_allow_html=True)

                opcoes_ordens = {l["id"]: f"Valor: ${l['valor_investido_usdt']:,.2f} / Data {l['data_abertura_br']} - {l['hora_abertura']}" for l in st.session_state['ordens_abertas']}
                ordem_selecionada = st.selectbox("Selecione a Ordem para Venda:", options=list(opcoes_ordens.keys()), format_func=lambda x: opcoes_ordens[x])
                
                c3, c4 = st.columns(2)
                with c3:
                    preco_venda = st.number_input("Cotação da Venda (USDT)", min_value=0.0, step=100.0, key="preco_venda")
                with c4:
                    pass 
                
                ordem_ativa = next(l for l in st.session_state['ordens_abertas'] if l["id"] == ordem_selecionada)
                valor_bruto_venda = ordem_ativa['quantidade_btc'] * preco_venda
                
                if preco_venda > 0:
                    st.info(f"💵 **Valor Bruto da Venda:** \${valor_bruto_venda:,.2f}")
                
                submit_venda = st.button("Executar Venda e Fechar Ordem", type="primary", use_container_width=True)
                
                if submit_venda:
                    if usar_bnb and not st.session_state['saldo_configurado']:
                        st.error("🛑 Operação Bloqueada: Aplique saldo na Tesouraria.")
                    elif preco_venda > 0:
                        # Backup perfeito da ordem antes de ser modificada para caso o usuário clique em Desfazer
                        ordem_original = copy.deepcopy(ordem_ativa)
                        
                        taxa_saida_usdt = valor_bruto_venda * (0.00075 if usar_bnb else 0.0010)
                        total_taxas_operacao = ordem_ativa.get('taxa_entrada_usdt', 0.0) + taxa_saida_usdt
                        
                        valor_liquido_recebido = valor_bruto_venda
                        usou_bnb_real_venda = False
                        custo_bnb_venda = 0.0
                        
                        if usar_bnb:
                            custo_bnb_venda = taxa_saida_usdt / preco_bnb_atual
                            if st.session_state['saldo_bnb'] >= custo_bnb_venda:
                                st.session_state['saldo_bnb'] -= custo_bnb_venda 
                                st.session_state['historico_taxas_bnb'].append({"id_transacao": f"VENDA-{ordem_ativa['id']}", "qtd_bnb": custo_bnb_venda})
                                usou_bnb_real_venda = True
                            else:
                                valor_liquido_recebido = valor_bruto_venda - taxa_saida_usdt
                        else:
                            valor_liquido_recebido = valor_bruto_venda - taxa_saida_usdt
                        
                        lucro_usdt = valor_liquido_recebido - ordem_ativa['valor_investido_usdt']
                        if usar_bnb:
                            lucro_usdt -= total_taxas_operacao
                            
                        lucro_pct = (lucro_usdt / ordem_ativa['valor_investido_usdt']) * 100
                        agora_venda = datetime.datetime.now(fuso_brasilia)
                        
                        ordem_ativa['status'] = "Fechado"
                        ordem_ativa['data_fechamento'] = agora_venda.strftime("%Y-%m-%d")
                        ordem_ativa['data_fechamento_br'] = agora_venda.strftime("%d/%m/%Y") 
                        ordem_ativa['hora_fechamento'] = agora_venda.strftime("%H:%M")
                        ordem_ativa['preco_venda'] = preco_venda
                        ordem_ativa['valor_recebido_usdt'] = valor_liquido_recebido
                        ordem_ativa['lucro_usdt'] = lucro_usdt
                        ordem_ativa['lucro_pct'] = lucro_pct
                        ordem_ativa['total_taxas_usdt'] = total_taxas_operacao
                        
                        # Remove a antiga aberta e coloca na lista de fechadas
                        st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ordem_ativa['id']]
                        st.session_state['historico_fechado'].append(ordem_ativa)
                        
                        # Salvando na Pilha de Desfazer
                        st.session_state['pilha_desfazer'].append({
                            'acao': 'venda',
                            'ordem_restaurada': ordem_original,
                            'usou_bnb': usou_bnb_real_venda,
                            'custo_bnb': custo_bnb_venda,
                            'id_ordem': ordem_ativa['id']
                        })
                        st.rerun()

st.divider()

col_abertos, col_fechados = st.columns(2)

with col_abertos:
    st.subheader("🟢 Ordens Abertas")
    if st.session_state['ordens_abertas']:
        for t in st.session_state['ordens_abertas']:
            st.info(f"**Ordem #{t['id']}** | {t['data_abertura_br']} às {t['hora_abertura']}\n\n{t['quantidade_btc']:.8f} BTC | Custo Total: \${t['valor_investido_usdt']:,.2f} | Preço Pago: \${t['preco_compra']:,.2f} | Taxa: \${t['taxa_entrada_usdt']:.4f}")
    else:
        st.write("Nenhuma ordem aberta no momento.")

with col_fechados:
    st.subheader("🎯 Últimas Ordens Fechadas")
    if st.session_state['historico_fechado']:
        for t in reversed(st.session_state['historico_fechado'][-5:]):
            cor_lucro = "#16a34a" if t['lucro_usdt'] >= 0 else "#dc2626"
            sinal = "+" if t['lucro_usdt'] >= 0 else ""
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 5px solid {cor_lucro}; margin-bottom: 10px;">
                <strong>Ordem #{t['id']}</strong> concluída<br>
                <span style="color: gray; font-size: 0.85em;">
                    Aberta em {t['data_abertura_br']} às {t['hora_abertura']} Hs<br>
                    Fechada em {t['data_fechamento_br']} às {t['hora_fechamento']} Hs
                </span><br>
                Resultado Líquido: <strong style="color: {cor_lucro};">{sinal}&#36;{t['lucro_usdt']:.2f} ({sinal}{t['lucro_pct']:.2f}%)</strong><br>
                <span style="color: #9ca3af; font-size: 0.85em;">Total gasto em Taxas: &#36;{t['total_taxas_usdt']:.4f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nenhuma venda realizada ainda.")

# ==========================================
# BOTÃO DE DESFAZER AÇÃO (NO RODAPÉ)
# ==========================================
if st.session_state['pilha_desfazer']:
    st.markdown("<br>", unsafe_allow_html=True)
    c_empty, c_undo = st.columns([8, 2])
    with c_undo:
        if st.button("↩️ Desfazer Última Ação", use_container_width=True):
            ultima_acao = st.session_state['pilha_desfazer'].pop()
            
            if ultima_acao['acao'] == 'compra':
                st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ultima_acao['id_ordem']]
                if ultima_acao['usou_bnb']:
                    st.session_state['saldo_bnb'] += ultima_acao['custo_bnb']
                    st.session_state['historico_taxas_bnb'] = [t for t in st.session_state['historico_taxas_bnb'] if t['id_transacao'] != ultima_acao['id_ordem']]
                    
            elif ultima_acao['acao'] == 'venda':
                st.session_state['historico_fechado'] = [o for o in st.session_state['historico_fechado'] if o['id'] != ultima_acao['id_ordem']]
                st.session_state['ordens_abertas'].append(ultima_acao['ordem_restaurada'])
                if ultima_acao['usou_bnb']:
                    st.session_state['saldo_bnb'] += ultima_acao['custo_bnb']
                    st.session_state['historico_taxas_bnb'] = [t for t in st.session_state['historico_taxas_bnb'] if t['id_transacao'] != f"VENDA-{ultima_acao['id_ordem']}"]
            
            st.rerun()
