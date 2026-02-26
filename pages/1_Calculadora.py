import streamlit as st
import datetime
import requests
import copy

st.set_page_config(page_title="Calculadora - O Conselho", page_icon="🧮", layout="wide", initial_sidebar_state="collapsed")

# --- CSS INSTITUCIONAL ---
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
        .sim-card {
            background-color: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            height: 100%;
        }
        .sim-title {
            color: #9ca3af;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .sim-val {
            font-size: 1.4em;
            font-weight: bold;
            color: white;
        }
        .badge-taxa {
            background-color: rgba(34, 197, 94, 0.1);
            color: #22c55e;
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            font-weight: bold;
            letter-spacing: 0.5px;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE API ---
def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 65000.0

fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))

# --- CABEÇALHO ---
col_titulo, col_botao = st.columns([8, 2], vertical_alignment="center")
with col_titulo:
    st.title("🧮 Boleta de Operações")
with col_botao:
    st.page_link("pages/2_Portfolio.py", label="Ir para Portfólio", icon="💼")

st.divider()

# --- VERIFICAÇÃO DE MEMÓRIA ---
if 'ordens_abertas' not in st.session_state: st.session_state['ordens_abertas'] = []
if 'historico_fechado' not in st.session_state: st.session_state['historico_fechado'] = []
if 'pilha_desfazer' not in st.session_state: st.session_state['pilha_desfazer'] = []
if 'contador_ordens' not in st.session_state: st.session_state['contador_ordens'] = 1 
if 'val_compra' not in st.session_state: st.session_state['val_compra'] = 100.0
if 'preco_compra' not in st.session_state: st.session_state['preco_compra'] = obter_preco_btc()

# --- LAYOUT PRINCIPAL (50/50) ---
col_boleta, col_espaco, col_simulador = st.columns([10, 1, 10])

with col_boleta:
    aba_compra, aba_venda = st.tabs(["📥 Abrir Ordem", "📤 Fechar Ordem"])
    
    # === ABA DE COMPRA ===
    with aba_compra:
        with st.container(border=True):
            preco_btc_atual = obter_preco_btc()
            
            st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                    <span style="color: #9ca3af; font-size: 0.95em;">Cotação Atual (BTC/USDT)</span>
                    <strong style="font-size: 1.3em; color: #F3BA2F;">&#36;{preco_btc_atual:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                valor_total_usdt = st.number_input("Valor da Operação (USDT)", min_value=0.0, format="%.2f", step=10.0, key="val_compra")
            with c2:
                preco_execucao = st.number_input("Cotação de 1 BTC (Preço Pago)", min_value=0.0, step=100.0, key="preco_compra")
                
            quantidade = 0.0
            if preco_execucao > 0:
                quantidade = valor_total_usdt / preco_execucao
                
            st.markdown(f"""
                <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; margin-bottom: 15px;">
                    <strong>Volume de Compra:</strong> {quantidade:.8f} BTC
                </div>
            """, unsafe_allow_html=True)
            
            # Pílula de Taxa + Toggle Limpo
            st.markdown("<span class='badge-taxa'>TAXA: 0.075%</span>", unsafe_allow_html=True)
            usar_bnb = st.toggle("Pagar em BNB", value=True)

            st.markdown("<br>", unsafe_allow_html=True)
            submit_compra = st.button("Executar Compra", type="primary", use_container_width=True)

            if submit_compra:
                if valor_total_usdt > 0 and preco_execucao > 0:
                    id_operacao = f"{st.session_state['contador_ordens']:03d}"
                    st.session_state['contador_ordens'] += 1
                    agora = datetime.datetime.now(fuso_brasilia)
                    
                    taxa_entrada_usdt = valor_total_usdt * (0.00075 if usar_bnb else 0.001)
                    
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
                    
                    st.session_state['pilha_desfazer'].append({
                        'acao': 'compra',
                        'id_ordem': id_operacao
                    })
                    st.rerun()

    # === ABA DE VENDA ===
    with aba_venda:
        with st.container(border=True):
            if not st.session_state['ordens_abertas']:
                st.info("Nenhuma ordem aberta no momento.")
            else:
                preco_btc_atual_venda = obter_preco_btc()
                
                st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); padding: 12px 15px; border-radius: 8px; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between;">
                        <span style="color: #9ca3af; font-size: 0.95em;">Cotação Atual (BTC/USDT)</span>
                        <strong style="font-size: 1.3em; color: #F3BA2F;">&#36;{preco_btc_atual_venda:,.2f}</strong>
                    </div>
                """, unsafe_allow_html=True)

                opcoes_ordens = {l["id"]: f"Ordem #{l['id']} | Valor: ${l['valor_investido_usdt']:,.2f} | {l['data_abertura_br']}" for l in st.session_state['ordens_abertas']}
                ordem_selecionada = st.selectbox("Selecione a Ordem:", options=list(opcoes_ordens.keys()), format_func=lambda x: opcoes_ordens[x])
                
                preco_venda = st.number_input("Cotação da Venda (USDT)", min_value=0.0, step=100.0, key="preco_venda_input")
                
                # Pílula de Taxa + Toggle Limpo
                st.markdown("<span class='badge-taxa'>TAXA: 0.075%</span>", unsafe_allow_html=True)
                usar_bnb_venda = st.toggle("Pagar em BNB", value=True, key="toggle_venda")
                
                ordem_ativa = next(l for l in st.session_state['ordens_abertas'] if l["id"] == ordem_selecionada)
                valor_bruto_venda = ordem_ativa['quantidade_btc'] * preco_venda
                
                if preco_venda > 0:
                    prev_taxa_saida = valor_bruto_venda * (0.00075 if usar_bnb_venda else 0.0010)
                    prev_total_taxas = ordem_ativa.get('taxa_entrada_usdt', 0.0) + prev_taxa_saida
                    
                    prev_valor_liquido = valor_bruto_venda - prev_taxa_saida
                    prev_lucro_usdt = prev_valor_liquido - ordem_ativa['valor_investido_usdt']
                    prev_lucro_pct = (prev_lucro_usdt / ordem_ativa['valor_investido_usdt']) * 100
                    
                    sinal_prev = "+" if prev_lucro_usdt >= 0 else "-"
                    cor_prev = "#16a34a" if prev_lucro_usdt >= 0 else "#dc2626"
                    
                    st.markdown(f"""
                        <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; margin-bottom: 15px; margin-top: 15px;">
                            <strong>Retorno Final:</strong> &#36;{prev_valor_liquido:,.2f} <span style="margin: 0 8px; color: rgba(255,255,255,0.2);">|</span> <strong style="color: {cor_prev};">{sinal_prev}&#36;{abs(prev_lucro_usdt):,.2f} ({sinal_prev}{abs(prev_lucro_pct):,.2f}%)</strong>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                submit_venda = st.button("Executar Venda e Fechar Ordem", type="primary", use_container_width=True)
                
                if submit_venda and preco_venda > 0:
                    ordem_original = copy.deepcopy(ordem_ativa)
                    taxa_saida_usdt = valor_bruto_venda * (0.00075 if usar_bnb_venda else 0.0010)
                    total_taxas_operacao = ordem_ativa.get('taxa_entrada_usdt', 0.0) + taxa_saida_usdt
                    
                    valor_liquido_recebido = valor_bruto_venda - taxa_saida_usdt
                    lucro_usdt = valor_liquido_recebido - ordem_ativa['valor_investido_usdt']
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
                    
                    st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ordem_ativa['id']]
                    st.session_state['historico_fechado'].append(ordem_ativa)
                    
                    st.session_state['pilha_desfazer'].append({
                        'acao': 'venda',
                        'ordem_restaurada': ordem_original,
                        'id_ordem': ordem_ativa['id']
                    })
                    st.rerun()

# ==========================================
# SIMULADOR DE RISCO E RETORNO
# ==========================================
with col_simulador:
    st.subheader("Projeção de Risco e Retorno")
    st.markdown("<div style='color: gray; font-size: 0.9em; margin-bottom: 15px;'>Calcule os cenários antes de abrir a ordem na corretora.</div>", unsafe_allow_html=True)
    
    val_sim = st.session_state.get('val_compra', 0.0)
    preco_sim = st.session_state.get('preco_compra', 0.0)
    
    # Inputs com números inteiros (step=1)
    col_alvo, col_stop = st.columns(2)
    with col_alvo:
        alvo_pct = st.number_input("🎯 Alvo Desejado (%)", min_value=1, value=5, step=1)
    with col_stop:
        stop_pct = st.number_input("🛑 Limite de Perda (%)", min_value=1, value=2, step=1)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MATEMÁTICA ---
    preco_alvo = preco_sim * (1 + (alvo_pct / 100)) if preco_sim > 0 else 0.0
    preco_stop = preco_sim * (1 - (stop_pct / 100)) if preco_sim > 0 else 0.0
    
    lucro_potencial = val_sim * (alvo_pct / 100)
    risco_potencial = val_sim * (stop_pct / 100)
    
    relacao_rr = (lucro_potencial / risco_potencial) if risco_potencial > 0 else 0.0

    # --- DESENHANDO OS CARDS (3 Cards Limpos) ---
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(f"""
            <div class="sim-card" style="border-top: 3px solid #16a34a;">
                <div class="sim-title">Lucro Alvo</div>
                <div class="sim-val" style="color: #22c55e;">+${lucro_potencial:.2f}</div>
                <div style="font-size: 0.8em; color: gray; margin-top: 5px;">Vender a ${preco_alvo:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
            <div class="sim-card" style="border-top: 3px solid #dc2626;">
                <div class="sim-title">Risco Máximo</div>
                <div class="sim-val" style="color: #ef4444;">-${risco_potencial:.2f}</div>
                <div style="font-size: 0.8em; color: gray; margin-top: 5px;">Stop em ${preco_stop:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    cor_rr = "#22c55e" if relacao_rr >= 2.0 else "#eab308" if relacao_rr >= 1.0 else "#ef4444"
    st.markdown(f"""
        <div class="sim-card" style="border-left: 4px solid {cor_rr}; text-align: left; padding: 20px;">
            <div class="sim-title">Relação Risco / Retorno</div>
            <div class="sim-val" style="color: {cor_rr}; font-size: 1.8em;">1 : {relacao_rr:.1f}</div>
            <div style="font-size: 0.85em; color: gray; margin-top: 5px;">Para cada dólar em risco, você projeta um retorno de ${relacao_rr:.2f}.</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# ==========================================
# PAINEL INFERIOR
# ==========================================
col_abertos, col_fechados = st.columns(2)

with col_abertos:
    st.subheader("🟢 Ordens Abertas")
    if st.session_state['ordens_abertas']:
        for t in st.session_state['ordens_abertas']:
            st.info(f"**Ordem #{t['id']}** | {t['quantidade_btc']:.8f} BTC\n\nCusto Original: \${t['valor_investido_usdt']:,.2f} | Preço Pago: \${t['preco_compra']:,.2f}")
    else:
        st.write("Sua carteira está vazia.")

with col_fechados:
    st.subheader("🧾 Últimas Liquidações")
    if st.session_state['historico_fechado']:
        for t in reversed(st.session_state['historico_fechado'][-3:]):
            cor_lucro = "#16a34a" if t['lucro_usdt'] >= 0 else "#dc2626"
            sinal = "+" if t['lucro_usdt'] >= 0 else ""
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid {cor_lucro}; margin-bottom: 8px;">
                <strong>Ordem #{t['id']}</strong> <span style="color: gray; font-size: 0.9em;">fechada em {t['data_fechamento_br']}</span><br>
                Resultado Líquido: <strong style="color: {cor_lucro};">{sinal}&#36;{t['lucro_usdt']:.2f} ({sinal}{t['lucro_pct']:.2f}%)</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nenhuma venda realizada ainda.")

if st.session_state['pilha_desfazer']:
    st.markdown("<br>", unsafe_allow_html=True)
    c_empty, c_undo = st.columns([8, 2])
    with c_undo:
        if st.button("↩️ Desfazer Última Ação", use_container_width=True):
            ultima_acao = st.session_state['pilha_desfazer'].pop()
            if ultima_acao['acao'] == 'compra':
                st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ultima_acao['id_ordem']]
                st.session_state['contador_ordens'] = max(1, st.session_state['contador_ordens'] - 1) 
            elif ultima_acao['acao'] == 'venda':
                st.session_state['historico_fechado'] = [o for o in st.session_state['historico_fechado'] if o['id'] != ultima_acao['id_ordem']]
                st.session_state['ordens_abertas'].append(ultima_acao['ordem_restaurada'])
            st.rerun()
