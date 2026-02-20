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
        /* Estilização para as Abas ficarem bonitas */
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

# --- NOVA ESTRUTURA DE MEMÓRIA (Preparada para os Gráficos Futuros) ---
if 'lotes_abertos' not in st.session_state: st.session_state['lotes_abertos'] = []
if 'historico_fechado' not in st.session_state: st.session_state['historico_fechado'] = []
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
    col_toggle, col_badge = st.columns([3, 2])
    usar_bnb = col_toggle.toggle("Pagar taxas com BNB", value=True)
    
    with col_badge:
        if usar_bnb:
            st.markdown("<div style='background-color: #15803d; color: white; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.075%</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #eab308; color: black; padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: bold; margin-top: 2px; width: fit-content;'>0.100%</div>", unsafe_allow_html=True)
    
    preco_bnb_atual = obter_preco_bnb()
    st.caption(f"📡 Cotação atual BNB/USDT: **{preco_bnb_atual:,.2f} USDT**")
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Limpar Histórico de Testes", use_container_width=True):
        st.session_state['lotes_abertos'] = []
        st.session_state['historico_fechado'] = []
        st.session_state['historico_taxas_bnb'] = []
        st.session_state['saldo_bnb'] = 0.0
        st.session_state['saldo_configurado'] = False
        st.rerun()

with col_boleta:
    # CRIANDO AS ABAS DE NAVEGAÇÃO
    aba_compra, aba_venda = st.tabs(["🛒 Abrir Posição (Compra)", "🎯 Fechar Lote (Venda)"])
    
    # ==========================================
    # ABA 1: ABRIR POSIÇÃO (COMPRA)
    # ==========================================
    with aba_compra:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                valor_total_usdt = st.number_input("Valor da Operação (USDT)", min_value=0.0, format="%.2f", step=10.0, key="val_compra")
                data_hora = st.date_input("Data da Compra", datetime.date.today(), format="DD/MM/YYYY")
                
            with c2:
                preco_execucao = st.number_input("Cotação de 1 BTC (Preço de Execução)", min_value=0.0, step=100.0, key="preco_compra")
                hora_minuto = st.time_input("Hora da Compra", datetime.datetime.now().time())
                
            quantidade = 0.0
            if preco_execucao > 0:
                quantidade = valor_total_usdt / preco_execucao
                
            st.info(f"**Quantidade Bruta Estimada:** {quantidade:.8f} BTC")
            
            if usar_bnb and not st.session_state['saldo_configurado']:
                st.warning("⚠️ **Atenção:** O desconto BNB está ativo, mas você ainda não configurou a Tesouraria.")

            submit_compra = st.button("Executar Compra e Abrir Lote", type="primary", use_container_width=True)

            if submit_compra:
                if usar_bnb and not st.session_state['saldo_configurado']:
                    st.error("🛑 Operação Bloqueada: Aplique saldo na Tesouraria ou desative o desconto.")
                elif valor_total_usdt > 0 and preco_execucao > 0:
                    id_operacao = str(uuid.uuid4())[:8].upper()
                    
                    # Deduzir taxa BNB se ativo
                    if usar_bnb:
                        taxa_usdt = valor_total_usdt * 0.00075
                        custo_bnb = taxa_usdt / preco_bnb_atual
                        if st.session_state['saldo_bnb'] >= custo_bnb:
                            st.session_state['saldo_bnb'] -= custo_bnb 
                            st.session_state['historico_taxas_bnb'].append({"id_transacao": id_operacao, "qtd_bnb": custo_bnb})
                        else:
                            usar_bnb = False # Falha silenciosa de saldo vai pra taxa cheia
                    
                    # Estrutura de dados perfeita para o futuro Gráfico
                    novo_lote = {
                        "id": id_operacao,
                        "data_abertura": data_hora.strftime("%Y-%m-%d"), # Formato YYYY-MM-DD é o melhor para gráficos
                        "hora_abertura": hora_minuto.strftime("%H:%M"),
                        "data_abertura_br": data_hora.strftime("%d/%m/%Y"), # Para exibir bonito na tela
                        "valor_investido_usdt": valor_total_usdt,
                        "quantidade_btc": quantidade if usar_bnb else quantidade - (quantidade * 0.001), # Desconta se não usou BNB
                        "preco_compra": preco_execucao,
                        "status": "Aberto"
                    }
                    st.session_state['lotes_abertos'].append(novo_lote)
                    st.rerun()

    # ==========================================
    # ABA 2: FECHAR LOTE (VENDA)
    # ==========================================
    with aba_venda:
        with st.container(border=True):
            if not st.session_state['lotes_abertos']:
                st.info("Nenhum lote aberto no momento para realizar fechamento.")
            else:
                # Cria a lista suspensa com os lotes abertos para você escolher
                opcoes_lotes = {l["id"]: f"Lote #{l['id']} | Adquirido em {l['data_abertura_br']} | {l['quantidade_btc']:.8f} BTC" for l in st.session_state['lotes_abertos']}
                lote_selecionado = st.selectbox("Selecione o Lote para Venda:", options=list(opcoes_lotes.keys()), format_func=lambda x: opcoes_lotes[x])
                
                c3, c4 = st.columns(2)
                with c3:
                    preco_venda = st.number_input("Cotação da Venda (USDT)", min_value=0.0, step=100.0, key="preco_venda")
                with c4:
                    data_venda = st.date_input("Data da Venda", datetime.date.today(), format="DD/MM/YYYY")
                    hora_venda = st.time_input("Hora da Venda", datetime.datetime.now().time())
                
                # Resgatando os dados do lote escolhido
                lote_ativo = next(l for l in st.session_state['lotes_abertos'] if l["id"] == lote_selecionado)
                valor_bruto_venda = lote_ativo['quantidade_btc'] * preco_venda
                
                if preco_venda > 0:
                    st.info(f"💵 **Valor Bruto da Venda:** {valor_bruto_venda:,.2f} USDT")
                
                submit_venda = st.button("Executar Venda e Fechar Lote", type="primary", use_container_width=True)
                
                if submit_venda:
                    if usar_bnb and not st.session_state['saldo_configurado']:
                        st.error("🛑 Operação Bloqueada: Aplique saldo na Tesouraria.")
                    elif preco_venda > 0:
                        # Calculo de taxas
                        valor_liquido_recebido = valor_bruto_venda
                        if usar_bnb:
                            taxa_usdt = valor_bruto_venda * 0.00075
                            custo_bnb = taxa_usdt / preco_bnb_atual
                            if st.session_state['saldo_bnb'] >= custo_bnb:
                                st.session_state['saldo_bnb'] -= custo_bnb 
                                st.session_state['historico_taxas_bnb'].append({"id_transacao": f"VENDA-{lote_ativo['id']}", "qtd_bnb": custo_bnb})
                            else:
                                valor_liquido_recebido = valor_bruto_venda - (valor_bruto_venda * 0.0010)
                        else:
                            valor_liquido_recebido = valor_bruto_venda - (valor_bruto_venda * 0.0010)
                        
                        # Calculando o Lucro (PnL)
                        lucro_usdt = valor_liquido_recebido - lote_ativo['valor_investido_usdt']
                        lucro_pct = (lucro_usdt / lote_ativo['valor_investido_usdt']) * 100
                        
                        # Completando o Dicionário para ir para o Histórico de Gráficos
                        lote_ativo['status'] = "Fechado"
                        lote_ativo['data_fechamento'] = data_venda.strftime("%Y-%m-%d")
                        lote_ativo['hora_fechamento'] = hora_venda.strftime("%H:%M")
                        lote_ativo['preco_venda'] = preco_venda
                        lote_ativo['valor_recebido_usdt'] = valor_liquido_recebido
                        lote_ativo['lucro_usdt'] = lucro_usdt
                        lote_ativo['lucro_pct'] = lucro_pct
                        
                        # Move da gaveta de Abertos para o Histórico Fechado
                        st.session_state['lotes_abertos'].remove(lote_ativo)
                        st.session_state['historico_fechado'].append(lote_ativo)
                        st.rerun()

st.divider()

# --- ÁREA INFERIOR: VISUALIZAÇÃO DOS LOTES ---
col_abertos, col_fechados = st.columns(2)

with col_abertos:
    st.subheader("🟢 Lotes Abertos (Em Custódia)")
    if st.session_state['lotes_abertos']:
        for t in st.session_state['lotes_abertos']:
            st.info(f"**Lote #{t['id']}** | Compra: {t['data_abertura_br']} às {t['hora_abertura']}\n\n{t['quantidade_btc']:.8f} BTC | Custo Total: {t['valor_investido_usdt']:,.2f} USDT | Preço Pago: ${t['preco_compra']:,.2f}")
    else:
        st.write("Nenhum lote aberto no momento.")

with col_fechados:
    st.subheader("🎯 Últimos Lotes Fechados")
    if st.session_state['historico_fechado']:
        for t in reversed(st.session_state['historico_fechado'][-5:]): # Mostra os 5 últimos
            cor_lucro = "green" if t['lucro_usdt'] >= 0 else "red"
            sinal = "+" if t['lucro_usdt'] >= 0 else ""
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; border-left: 5px solid {cor_lucro}; margin-bottom: 10px;">
                <strong>Lote #{t['id']}</strong> concluído<br>
                <span style="color: gray; font-size: 0.9em;">Aberto em {t['data_abertura_br']} | Fechado em {t['data_fechamento']}</span><br>
                Resultado Liquido: <strong style="color: {cor_lucro};">{sinal}{t['lucro_usdt']:.2f} USDT ({sinal}{t['lucro_pct']:.2f}%)</strong>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nenhuma venda realizada ainda.")
