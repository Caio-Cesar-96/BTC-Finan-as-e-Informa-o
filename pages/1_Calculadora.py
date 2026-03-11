import streamlit as st
import datetime
import requests
import copy
from supabase import create_client, Client

st.set_page_config(page_title="Calculadora - O Conselho", page_icon="🧮", layout="wide", initial_sidebar_state="collapsed")

# --- CADEADO DE SEGURANÇA ---
if not st.session_state.get("autenticado", False):
    st.switch_page("main.py")

# --- CONEXÃO COM O BANCO DE DADOS (SUPABASE) ---
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

# --- CONFIGURAÇÃO DE ATIVOS (IMAGENS OFICIAIS CDN) ---
ASSETS_CONFIG = {
    "BTC": {"nome": "Bitcoin", "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png", "cor": "#F3BA2F"},
    "ETH": {"nome": "Ethereum", "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png", "cor": "#627EEA"},
    "SOL": {"nome": "Solana", "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png", "cor": "#14F195"},
    "BNB": {"nome": "Binance Coin", "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/1839.png", "cor": "#F3BA2F"},
    "PAXG": {"nome": "PAX Gold", "image": "https://s2.coinmarketcap.com/static/img/coins/64x64/4705.png", "cor": "#D4AF37"}
}

# --- CSS INSTITUCIONAL ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none !important;}
        [data-testid="stSidebar"] {display: none !important;}
        
        [data-testid="stPageLink-NavLink"] {
            width: 100%; padding: 5px 15px; border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
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
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] {
            height: 50px; white-space: pre-wrap;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 5px 5px 0px 0px;
            padding-top: 10px; padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-bottom: 2px solid #F3BA2F !important;
        }
        .sim-card {
            background-color: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
            padding: 15px; text-align: center; height: 100%;
        }
        .sim-title { color: #9ca3af; font-size: 0.85em; text-transform: uppercase; margin-bottom: 5px; }
        .sim-val { font-size: 1.4em; font-weight: bold; color: white; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# MOTOR MATEMÁTICO (JUIZ) - RESTAURADO ORIGINAL
# ==========================================
def avaliar_comportamento(preco_compra, preco_venda, alvo, stop):
    if not alvo and not stop: return None
    lucro_real = preco_venda - preco_compra
    if lucro_real >= 0:
        if alvo and alvo > preco_compra:
            alvo_esperado = alvo - preco_compra
            pct_alcancado = lucro_real / alvo_esperado
            if pct_alcancado >= 0.90: return "🏆 Sniper"
            elif pct_alcancado > 0.10: return "🥬 Mão de Alface"
            else: return "🛡️ Saída Estratégica"
        else: return "⚖️ Ganho Livre"
    else:
        if stop and stop < preco_compra:
            perda_real = preco_compra - preco_venda
            stop_maximo = preco_compra - stop
            pct_perdido = perda_real / stop_maximo
            if pct_perdido <= 0.10: return "🛡️ Saída Estratégica"
            elif pct_perdido <= 1.10: return "🛑 Resiliência"
            else: return "💥 Descontrole"
        else: return "💥 Perda Livre"

# --- FUNÇÕES AUXILIARES ---
def obter_cotacao(simbolo):
    if not simbolo: return 0.0
    try:
        par = f"{simbolo}USDT"
        url = f"https://api.binance.us/api/v3/ticker/price?symbol={par}"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except: return 0.0

def carregar_dados_nuvem():
    try:
        user_id = st.session_state.get("user_id") 
        resposta = supabase.table("operacoes").select("*").eq("user_id", user_id).execute()
        dados = resposta.data
        dados_ordenados = sorted(dados, key=lambda x: x['id'])
        for indice, d in enumerate(dados_ordenados):
            d['display_id'] = f"{(indice + 1):03d}"
            if 'simbolo' not in d or not d['simbolo']: d['simbolo'] = 'BTC'
        abertas = [d for d in dados_ordenados if d['status'] == 'Aberto']
        fechadas = [d for d in dados_ordenados if d['status'] == 'Fechado']
        return abertas, fechadas
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return [], []

fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))

# --- CABEÇALHO ---
col_titulo, col_btn_home, col_btn_port = st.columns([6, 2, 2], vertical_alignment="center")
with col_titulo: st.title("🧮 Boleta de Operações")
with col_btn_home: st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="🏠")
with col_btn_port: st.page_link("pages/2_Portfolio.py", label="Ir para Portfólio", icon="💼")
st.divider()

if 'dados_sincronizados' not in st.session_state:
    with st.spinner("Sincronizando..."):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.session_state['dados_sincronizados'] = True

if 'val_compra' not in st.session_state: st.session_state['val_compra'] = 0.0
if 'preco_compra' not in st.session_state: st.session_state['preco_compra'] = 0.0

# --- LAYOUT PRINCIPAL ---
col_boleta, col_espaco, col_simulador = st.columns([10, 1, 10])

with col_boleta:
    aba_compra, aba_venda = st.tabs(["Abrir Ordem", "Fechar Ordem"])
    
    with aba_compra:
        with st.container(border=True):
            
            # --- 1. SELETOR PADRÃO (Sem Bugs) ---
            ativo_selecionado = st.selectbox(
                "Escolha o Ativo", 
                options=list(ASSETS_CONFIG.keys()),
                index=0, 
                format_func=lambda x: f"{ASSETS_CONFIG[x]['nome']} ({x})"
            )
            
            # Dados
            cotacao_atual = obter_cotacao(ativo_selecionado)
            img_ativo = ASSETS_CONFIG[ativo_selecionado]['image']
            nome_ativo = ASSETS_CONFIG[ativo_selecionado]['nome']

            # --- 2. CARD PREMIUM (HTML Puro e Seguro) ---
            st.markdown(f"""
<div style="display: flex; align-items: center; background: linear-gradient(90deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%); border: 1px solid rgba(255,255,255,0.08); padding: 20px; border-radius: 12px; margin-bottom: 25px; margin-top: 5px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
    <div style="position: relative;">
        <img src="{img_ativo}" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid rgba(255,255,255,0.1);">
    </div>
    <div style="margin-left: 20px; flex-grow: 1;">
        <div style="font-size: 0.8em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Operando Agora</div>
        <div style="font-size: 1.6em; font-weight: 800; color: white; line-height: 1.1;">{nome_ativo} <span style="font-size: 0.5em; color: #F3BA2F; vertical-align: middle; background: rgba(243, 186, 47, 0.1); padding: 2px 6px; border-radius: 4px;">{ativo_selecionado}</span></div>
    </div>
    <div style="text-align: right;">
        <div style="font-size: 0.8em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Preço de Mercado</div>
        <div style="font-size: 1.6em; font-weight: bold; color: #F3BA2F;">${cotacao_atual:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)

            # --- 3. INPUTS ORIGINAIS ---
            c1, c2 = st.columns(2)
            with c1: valor_total_usdt = st.number_input("Valor da Operação (USDT)", min_value=0.0, format="%.2f", step=10.0, key="val_compra")
            with c2: preco_execucao = st.number_input(f"Preço Pago ({ativo_selecionado})", min_value=0.0, value=cotacao_atual, step=0.01, format="%.2f", key="preco_compra")
            
            quantidade = 0.0
            if preco_execucao > 0: quantidade = valor_total_usdt / preco_execucao
            
            st.markdown(f"""<div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; margin-bottom: 15px;"><strong>Volume de Compra:</strong> {quantidade:.6f} {ativo_selecionado}</div>""", unsafe_allow_html=True)
            
            col_tog1, col_tog2 = st.columns(2)
            with col_tog1:
                usar_bnb = st.toggle("Pagar Taxa em BNB", value=True, key="toggle_compra_bnb")
                if usar_bnb: st.markdown("<div style='margin-bottom: 10px;'><span style='background-color: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold;'>TAXA: 0.075%</span></div>", unsafe_allow_html=True)
                else: st.markdown("<div style='margin-bottom: 10px;'><span style='background-color: rgba(156, 163, 175, 0.1); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.3); padding: 3px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold;'>TAXA: 0.100%</span></div>", unsafe_allow_html=True)
            
            with col_tog2:
                vincular_projecao = st.toggle("Vincular Projeção", value=False, key="toggle_vincular")
                alvo_input = st.session_state.get('alvo_simulador', 0)
                stop_input = st.session_state.get('stop_simulador', 0)
                if vincular_projecao:
                    if alvo_input == 0 and stop_input == 0: st.markdown("<div style='margin-bottom: 10px; text-align: right;'><span style='color: #eab308; font-size: 0.80em;'>⚠️ Simulador zerado. Ordem ficará livre.</span></div>", unsafe_allow_html=True)
                    else: st.markdown(f"<div style='margin-bottom: 10px; text-align: right;'><span style='color: #22c55e; font-size: 0.80em;'>✅ Vinculado: Alvo {alvo_input}% | Stop {stop_input}%</span></div>", unsafe_allow_html=True)
                else: st.markdown("<div style='margin-bottom: 10px; height: 18px;'></div>", unsafe_allow_html=True)

            submit_compra = st.button("Executar Compra", type="primary", use_container_width=True)

            # Lógica Original de Inserção
            if submit_compra:
                if valor_total_usdt > 0 and preco_execucao > 0:
                    id_operacao = f"ORD-{int(datetime.datetime.now().timestamp())}"
                    agora = datetime.datetime.now(fuso_brasilia)
                    taxa_entrada_usdt = valor_total_usdt * (0.00075 if usar_bnb else 0.001)
                    quantidade_final = quantidade if usar_bnb else quantidade - (quantidade * 0.001)
                    teve_projecao = vincular_projecao and (alvo_input > 0 or stop_input > 0)
                    preco_alvo = float(preco_execucao * (1 + (alvo_input / 100))) if alvo_input > 0 else None
                    preco_stop = float(preco_execucao * (1 - (stop_input / 100))) if stop_input > 0 else None
                    
                    nova_ordem = {
                        "id": id_operacao, "user_id": st.session_state.get("user_id"),
                        "simbolo": ativo_selecionado, "data_abertura": agora.strftime("%Y-%m-%d"),
                        "hora_abertura": agora.strftime("%H:%M"), "data_abertura_br": agora.strftime("%d/%m/%Y"), 
                        "valor_investido_usdt": float(valor_total_usdt), "quantidade_btc": float(quantidade_final), 
                        "preco_compra": float(preco_execucao), "taxa_entrada_usdt": float(taxa_entrada_usdt),
                        "status": "Aberto", "teve_projecao": teve_projecao,
                        "alvo_planejado": preco_alvo if teve_projecao else None, "stop_planejado": preco_stop if teve_projecao else None,
                        "comportamento_final": None
                    }
                    try:
                        supabase.table("operacoes").insert(nova_ordem).execute()
                        total_existentes = len(st.session_state['ordens_abertas']) + len(st.session_state['historico_fechado'])
                        nova_ordem['display_id'] = f"{(total_existentes + 1):03d}"
                        st.session_state['ordens_abertas'].append(nova_ordem)
                        st.success(f"✅ Ordem de {ativo_selecionado} registrada!")
                        st.rerun()
                    except Exception as e: st.error(f"Erro ao salvar: {e}")

    with aba_venda:
        with st.container(border=True):
            if not st.session_state['ordens_abertas']:
                st.info("Nenhuma ordem aberta no banco de dados.")
            else:
                opcoes_ordens = {l["id"]: f"Ordem #{l.get('display_id', '???')} | {l.get('simbolo', 'BTC')} | Investido: ${l['valor_investido_usdt']:,.2f} | Pago: ${l['preco_compra']:,.2f}" for l in st.session_state['ordens_abertas']}
                ordem_selecionada = st.selectbox("Selecione a Ordem:", options=list(opcoes_ordens.keys()), format_func=lambda x: opcoes_ordens[x])
                
                ordem_ativa = next(l for l in st.session_state['ordens_abertas'] if l["id"] == ordem_selecionada)
                simbolo_ativo = ordem_ativa.get('simbolo', 'BTC')
                preco_atual_venda = obter_cotacao(simbolo_ativo)
                img_ativo_venda = ASSETS_CONFIG.get(simbolo_ativo, ASSETS_CONFIG['BTC'])['image']

                # CARD VISUAL NA VENDA (Visual Seguro)
                st.markdown(f"""
<div style="display: flex; align-items: center; background-color: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <img src="{img_ativo_venda}" style="width: 40px; height: 40px; border-radius: 50%; margin-right: 15px;">
    <div>
        <div style="font-size: 0.8em; color: #9ca3af; text-transform: uppercase;">Mercado Atual</div>
        <div style="font-size: 1.4em; font-weight: bold; color: #F3BA2F;">${preco_atual_venda:,.2f}</div>
    </div>
</div>
""", unsafe_allow_html=True)
                
                preco_venda = st.number_input(f"Cotação da Venda ({simbolo_ativo})", min_value=0.0, step=0.01, format="%.2f", key="preco_venda_input")
                usar_bnb_venda = st.toggle("Pagar em BNB", value=True, key="toggle_venda_bnb")
                if usar_bnb_venda: st.markdown("<div style='margin-bottom: 5px;'><span style='background-color: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); padding: 3px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold;'>TAXA: 0.075%</span></div>", unsafe_allow_html=True)
                else: st.markdown("<div style='margin-bottom: 5px;'><span style='background-color: rgba(156, 163, 175, 0.1); color: #9ca3af; border: 1px solid rgba(156, 163, 175, 0.3); padding: 3px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold;'>TAXA: 0.100%</span></div>", unsafe_allow_html=True)
                
                valor_bruto_venda = float(ordem_ativa['quantidade_btc']) * preco_venda
                
                # Inicialização das variáveis para evitar o NameError
                prev_valor_liquido = 0.0
                prev_lucro_usdt = 0.0
                prev_lucro_pct = 0.0
                sinal_prev = ""
                cor_prev = "gray"
                html_veredito = ""
                
                if preco_venda > 0:
                    taxa_saida_prev = valor_bruto_venda * (0.00075 if usar_bnb_venda else 0.0010)
                    prev_valor_liquido = valor_bruto_venda - taxa_saida_prev
                    prev_lucro_usdt = prev_valor_liquido - float(ordem_ativa['valor_investido_usdt'])
                    prev_lucro_pct = (prev_lucro_usdt / float(ordem_ativa['valor_investido_usdt'])) * 100
                    sinal_prev = "+" if prev_lucro_usdt >= 0 else "-"
                    cor_prev = "#16a34a" if prev_lucro_usdt >= 0 else "#dc2626"
                    
                    comportamento_prev = None
                    if ordem_ativa.get('teve_projecao'):
                        comportamento_prev = avaliar_comportamento(float(ordem_ativa['preco_compra']), preco_venda, float(ordem_ativa.get('alvo_planejado')) if ordem_ativa.get('alvo_planejado') else None, float(ordem_ativa.get('stop_planejado')) if ordem_ativa.get('stop_planejado') else None)

                    if comportamento_prev:
                        cor_ver = "#22c55e" if "Sniper" in comportamento_prev else "#eab308" if "Alface" in comportamento_prev else "#ef4444" if "Descontrole" in comportamento_prev else "gray"
                        html_veredito = f"""
                        <div style="margin-top: 10px; border-top: 1px dashed rgba(255,255,255,0.1); padding-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                            <span style="color: #9ca3af; font-size: 0.85em; text-transform: uppercase;">Projeção de Disciplina:</span>
                            <strong style="color: {cor_ver}; background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 4px; font-size: 0.9em;">{comportamento_prev}</strong>
                        </div>
                        """
                    
                st.markdown(f"""
                    <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px 15px; border-radius: 4px; margin-bottom: 15px; margin-top: 15px;">
                        <strong>Retorno Final:</strong> &#36;{prev_valor_liquido:,.2f} <span style="margin: 0 8px; color: rgba(255,255,255,0.2);">|</span> <strong style="color: {cor_prev};">{sinal_prev}&#36;{abs(prev_lucro_usdt):,.2f} ({sinal_prev}{abs(prev_lucro_pct):,.2f}%)</strong>
                        {html_veredito}
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Executar Venda e Fechar Ordem", type="primary", use_container_width=True):
                    if preco_venda > 0:
                        taxa_saida = valor_bruto_venda * (0.00075 if usar_bnb_venda else 0.0010)
                        total_taxas = float(ordem_ativa.get('taxa_entrada_usdt', 0)) + taxa_saida
                        val_liq = valor_bruto_venda - taxa_saida
                        lucro = val_liq - float(ordem_ativa['valor_investido_usdt'])
                        pct = (lucro / float(ordem_ativa['valor_investido_usdt'])) * 100
                        agora_v = datetime.datetime.now(fuso_brasilia)
                        
                        comp_final = None
                        if ordem_ativa.get('teve_projecao'):
                            comp_final = avaliar_comportamento(float(ordem_ativa['preco_compra']), preco_venda, float(ordem_ativa.get('alvo_planejado')) if ordem_ativa.get('alvo_planejado') else None, float(ordem_ativa.get('stop_planejado')) if ordem_ativa.get('stop_planejado') else None)

                        update_data = {
                            'status': "Fechado", 'data_fechamento': agora_v.strftime("%Y-%m-%d"), 'data_fechamento_br': agora_v.strftime("%d/%m/%Y"),
                            'hora_fechamento': agora_v.strftime("%H:%M"), 'preco_venda': float(preco_venda), 'valor_recebido_usdt': float(val_liq),
                            'lucro_usdt': float(lucro), 'lucro_pct': float(pct), 'total_taxas_usdt': float(total_taxas), 'comportamento_final': comp_final
                        }
                        try:
                            supabase.table("operacoes").update(update_data).eq("id", ordem_ativa['id']).execute()
                            st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ordem_ativa['id']]
                            st.session_state['historico_fechado'].append(ordem_ativa)
                            st.success("✅ Ordem liquidada!")
                            st.rerun()
                        except Exception as e: st.error(f"Erro: {e}")

with col_simulador:
    st.subheader("Projeção de Risco e Retorno")
    st.markdown("<div style='color: gray; font-size: 0.9em; margin-bottom: 15px;'>Calcule os cenários antes de abrir a ordem.</div>", unsafe_allow_html=True)
    val_sim = st.session_state.get('val_compra', 0.0)
    preco_sim = st.session_state.get('preco_compra', 0.0)
    col_alvo, col_stop = st.columns(2)
    with col_alvo: alvo_pct = st.number_input("🎯 Alvo Desejado (%)", min_value=0, value=0, step=1, key="alvo_simulador")
    with col_stop: stop_pct = st.number_input("🛑 Limite de Perda (%)", min_value=0, value=0, step=1, key="stop_simulador")

    st.markdown("<br>", unsafe_allow_html=True)
    preco_alvo = preco_sim * (1 + (alvo_pct / 100)) if preco_sim > 0 else 0.0
    preco_stop = preco_sim * (1 - (stop_pct / 100)) if preco_sim > 0 else 0.0
    lucro_potencial = val_sim * (alvo_pct / 100)
    risco_potencial = val_sim * (stop_pct / 100)
    relacao_rr = (lucro_potencial / risco_potencial) if risco_potencial > 0 else 0.0

    s1, s2 = st.columns(2)
    with s1: st.markdown(f"""<div class="sim-card" style="border-top: 3px solid #16a34a;"><div class="sim-title">Lucro Alvo</div><div class="sim-val" style="color: #22c55e;">+${lucro_potencial:.2f}</div><div style="font-size: 0.8em; color: gray; margin-top: 5px;">Vender a ${preco_alvo:,.2f}</div></div>""", unsafe_allow_html=True)
    with s2: st.markdown(f"""<div class="sim-card" style="border-top: 3px solid #dc2626;"><div class="sim-title">Risco Máximo</div><div class="sim-val" style="color: #ef4444;">-${risco_potencial:.2f}</div><div style="font-size: 0.8em; color: gray; margin-top: 5px;">Stop em ${preco_stop:,.2f}</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    cor_rr = "#22c55e" if relacao_rr >= 2.0 else "#eab308" if relacao_rr >= 1.0 else "#ef4444"
    st.markdown(f"""<div class="sim-card" style="border-left: 4px solid {cor_rr}; text-align: left; padding: 20px;"><div class="sim-title">Relação Risco / Retorno</div><div class="sim-val" style="color: {cor_rr}; font-size: 1.8em;">1 : {relacao_rr:.1f}</div><div style="font-size: 0.85em; color: gray; margin-top: 5px;">Para cada dólar em risco, retorno de ${relacao_rr:.2f}.</div></div>""", unsafe_allow_html=True)

st.divider()

# ==========================================
# PAINEL INFERIOR (LISTAGEM RESTAURADA + ÍCONES)
# ==========================================
col_abertos, col_fechados = st.columns(2)

with col_abertos:
    st.subheader("🟢 Ordens Abertas")
    if st.session_state['ordens_abertas']:
        for t in reversed(st.session_state['ordens_abertas']):
            simb = t.get('simbolo', 'BTC')
            img = ASSETS_CONFIG.get(simb, ASSETS_CONFIG["BTC"])["image"]
            
            # --- CARD COM LOGO EM VEZ DO NOME ---
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 15px; border-radius: 8px 8px 0 0; margin-bottom: 0px; border-left: 4px solid #3b82f6;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center;">
                        <strong style="color: white; font-size: 1.1em;">Ordem #{t.get('display_id', '???')}</strong>
                        <img src="{img}" style="width: 24px; height: 24px; border-radius: 50%; vertical-align: middle; margin-left: 10px;" title="{simb}">
                    </div>
                    <span style="color: #F3BA2F; font-weight: bold;">{t['quantidade_btc']:.6f} {simb}</span>
                </div>
                <div style="color: #9ca3af; font-size: 0.9em; margin-bottom: 4px;">Custo: <strong style="color: white;">${t['valor_investido_usdt']:,.2f}</strong></div>
                <div style="color: #9ca3af; font-size: 0.9em;">Preço Pago: <strong style="color: white;">${t['preco_compra']:,.2f}</strong></div>
            </div>
            """, unsafe_allow_html=True)
            
            if t.get('teve_projecao'):
                alvo_str = f"🎯 Alvo: ${t['alvo_planejado']:,.2f}" if t.get('alvo_planejado') else "🎯 Alvo: ---"
                stop_str = f"🛑 Stop: ${t['stop_planejado']:,.2f}" if t.get('stop_planejado') else "🛑 Stop: ---"
                st.markdown(f"""
                <div style="background-color: rgba(255,255,255,0.05); padding: 10px 15px; border-radius: 0 0 8px 8px; margin-bottom: 10px; border-left: 4px solid #3b82f6; border-top: 1px dashed rgba(255,255,255,0.1);">
                     <div style="display: flex; justify-content: space-between; font-size: 0.85em;">
                        <span style="color: #22c55e;">{alvo_str}</span>
                        <span style="color: #ef4444;">{stop_str}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)
    else:
        st.write("Sua carteira está vazia.")

with col_fechados:
    st.subheader("🎯 Ordens Finalizadas")
    if st.session_state['historico_fechado']:
        for t in reversed(st.session_state['historico_fechado'][-3:]):
            cor_lucro = "#16a34a" if t.get('lucro_usdt', 0) >= 0 else "#dc2626"
            sinal = "+" if t.get('lucro_usdt', 0) >= 0 else ""
            simbolo_display = t.get('simbolo', 'BTC')
            img = ASSETS_CONFIG.get(simbolo_display, ASSETS_CONFIG["BTC"])["image"]
            
            html_comportamento = ""
            comp = t.get('comportamento_final')
            if comp:
                html_comportamento = f"""<div style="margin-top: 8px; font-size: 0.8em; display: inline-block; padding: 2px 8px; background-color: rgba(255,255,255,0.1); border-radius: 4px; color: #e2e8f0;">{comp}</div>"""
            
            # --- CARD COM LOGO EM VEZ DO NOME (Restaurada info de taxas e lucro) ---
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; border-left: 4px solid {cor_lucro}; margin-bottom: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center;">
                        <strong>Ordem #{t.get('display_id', '???')}</strong>
                        <img src="{img}" style="width: 24px; height: 24px; border-radius: 50%; vertical-align: middle; margin-left: 10px;" title="{simbolo_display}">
                    </div>
                </div>
                Resultado Líquido: <strong style="color: {cor_lucro};">{sinal}&#36;{t.get('lucro_usdt', 0):.2f} ({sinal}{t.get('lucro_pct', 0):.2f}%)</strong><br>
                <span style="color: gray; font-size: 0.85em;">Taxas: &#36;{t.get('total_taxas_usdt', 0):.4f}</span><br>
                {html_comportamento}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.write("Nenhuma venda realizada ainda.")

# === ZONA DE PERIGO ===
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🗑️ Zona de Perigo: Apagar Ordens do Banco de Dados"):
    todas_ordens = st.session_state['ordens_abertas'] + st.session_state['historico_fechado']
    if not todas_ordens:
        st.write("Nenhuma ordem encontrada no banco de dados.")
    else:
        opcoes_del = {o['id']: f"Ordem #{o.get('display_id', '???')} ({o['status']}) | {o.get('simbolo', 'BTC')} | ${o['valor_investido_usdt']:,.2f}" for o in todas_ordens}
        ordem_del_id = st.selectbox("Selecione a ordem para excluir permanentemente:", options=list(opcoes_del.keys()), format_func=lambda x: opcoes_del[x])
        
        if st.button("🚨 Apagar Ordem Selecionada", type="primary"):
            try:
                user_id = st.session_state.get("user_id")
                supabase.table("operacoes").delete().eq("id", ordem_del_id).eq("user_id", user_id).execute()
                
                st.session_state['ordens_abertas'] = [o for o in st.session_state['ordens_abertas'] if o['id'] != ordem_del_id]
                st.session_state['historico_fechado'] = [o for o in st.session_state['historico_fechado'] if o['id'] != ordem_del_id]
                
                todas_restantes = sorted(st.session_state['ordens_abertas'] + st.session_state['historico_fechado'], key=lambda x: x['id'])
                for indice, d in enumerate(todas_restantes):
                    d['display_id'] = f"{(indice + 1):03d}"
                    
                st.success("Ordem apagada com sucesso e numeração reorganizada!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao apagar ordem no banco: {e}")
