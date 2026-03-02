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
    st.error(f"Erro de conexão com o Banco de Dados: {e}")
    st.stop()

# --- CSS INSTITUCIONAL ---
st.markdown("""
    <style>
        /* MATAR A BARRA LATERAL PADRÃO */
        [data-testid="collapsedControl"] {display: none !important;}
        [data-testid="stSidebar"] {display: none !important;}
        
        [data-testid="stPageLink-NavLink"] {
            width: 100%;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
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
    </style>
""", unsafe_allow_html=True)

# ==========================================
# O JUIZ DA DISCIPLINA (MOTOR MATEMÁTICO)
# ==========================================
def avaliar_comportamento(preco_compra, preco_venda, alvo, stop):
    if not alvo and not stop:
        return None
        
    lucro_real = preco_venda - preco_compra
    
    if lucro_real >= 0:
        if alvo and alvo > preco_compra:
            alvo_esperado = alvo - preco_compra
            pct_alcancado = lucro_real / alvo_esperado
            
            if pct_alcancado >= 0.90: return "🏆 Sniper"
            elif pct_alcancado > 0.10: return "🥬 Mão de Alface"
            else: return "🛡️ Saída Estratégica"
        else:
            return "⚖️ Ganho Livre"
    else:
        if stop and stop < preco_compra:
            perda_real = preco_compra - preco_venda
            stop_maximo = preco_compra - stop
            pct_perdido = perda_real / stop_maximo
            
            if pct_perdido <= 0.10: return "🛡️ Saída Estratégica"
            elif pct_perdido <= 1.10: return "🛑 Resiliência"
            else: return "💥 Descontrole"
        else:
            return "💥 Perda Livre"

# --- FUNÇÕES DE API E SINCRONIZAÇÃO COM MÁSCARA ---
def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 65000.0

def carregar_dados_nuvem():
    try:
        # MUDANÇA: Filtra apenas as operações do usuário logado
        user_id = st.session_state.get("user_id")
        resposta = supabase.table("operacoes").select("*").eq("user_id", user_id).execute()
        
        dados = resposta.data
        dados_ordenados = sorted(dados, key=lambda x: x['id'])
        
        for indice, d in enumerate(dados_ordenados):
            d['display_id'] = f"{(indice + 1):03d}"
            
        abertas = [d for d in dados_ordenados if d['status'] == 'Aberto']
        fechadas = [d for d in dados_ordenados if d['status'] == 'Fechado']
        return abertas, fechadas
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")
        return [], []

fuso_brasilia = datetime.timezone(datetime.timedelta(hours=-3))

# --- CABEÇALHO E NAVEGAÇÃO ---
col_titulo, col_btn_home, col_btn_port = st.columns([6, 2, 2], vertical_alignment="center")
with col_titulo:
    st.title("🧮 Boleta de Operações")
with col_btn_home:
    st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="🏠")
with col_btn_port:
    st.page_link("pages/2_Portfolio.py", label="Ir para Portfólio", icon="💼")

st.divider()

# --- DADOS E ESTADO ---
abertas_bd, fechadas_bd = carregar_dados_nuvem()

if 'dados_operacao' not in st.session_state:
    st.session_state['dados_operacao'] = {
        'compra': 0.0, 'stop': 0.0, 'alvo': 0.0,
        'taxa_entrada': 0.0, 'investimento': 0.0, 'qtd_btc': 0.0
    }

cotacao_atual = obter_preco_btc()

# --- ABAS PRINCIPAIS ---
aba_calculadora, aba_abertas, aba_historico = st.tabs(["Nova Operação", f"Em Aberto ({len(abertas_bd)})", f"Histórico ({len(fechadas_bd)})"])

# ==================================================
# ABA 1: CALCULADORA (Boleta de Entrada)
# ==================================================
with aba_calculadora:
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.caption("PARAMETROS DE ENTRADA")
        investimento = st.number_input("Investimento (USDT)", min_value=0.0, step=10.0, value=100.0)
        preco_compra = st.number_input("Preço de Entrada (BTC)", min_value=0.0, step=100.0, value=cotacao_atual)
        
        qtd_btc = investimento / preco_compra if preco_compra > 0 else 0.0
        st.metric("Quantidade BTC", f"{qtd_btc:.6f}")
        
    with c2:
        st.caption("GESTÃO DE RISCO")
        preco_stop = st.number_input("Stop Loss (BTC)", min_value=0.0, step=100.0, value=preco_compra * 0.95)
        preco_alvo = st.number_input("Alvo / Take Profit (BTC)", min_value=0.0, step=100.0, value=preco_compra * 1.05)
        
        risco_usd = (preco_compra - preco_stop) * qtd_btc
        retorno_usd = (preco_alvo - preco_compra) * qtd_btc
        ratio = retorno_usd / risco_usd if risco_usd > 0 else 0
        
        st.metric("Risco / Retorno", f"1 : {ratio:.1f}")

    with c3:
        st.caption("TAXAS E CUSTOS")
        taxa_entrada_pct = st.number_input("Taxa Corretora (%)", value=0.1, step=0.01)
        taxa_entrada_usd = investimento * (taxa_entrada_pct / 100)
        
        st.metric("Custo da Entrada", f"${taxa_entrada_usd:.2f}")
        
    st.divider()
    
    # BOTÃO DE SALVAR
    col_btn_salvar, _ = st.columns([1, 2])
    with col_btn_salvar:
        if st.button("Gravar Operação no Banco de Dados", type="primary", use_container_width=True):
            if investimento > 0 and preco_compra > 0:
                agora = datetime.datetime.now(fuso_brasilia)
                
                # MUDANÇA: Inclusão do 'user_id' no payload
                nova_operacao = {
                    "user_id": st.session_state["user_id"], # CARIMBO DO USUÁRIO
                    "data_abertura": str(agora.date()),
                    "hora_abertura": str(agora.strftime("%H:%M")),
                    "texto_data_abertura_br": agora.strftime("%d/%m/%Y"),
                    "valor_investido_usdt": investimento,
                    "preco_compra": preco_compra,
                    "quantidade_btc": qtd_btc,
                    "taxa_entrada_usdt": taxa_entrada_usd,
                    "status": "Aberto",
                    # Campos nulos para preencher no fechamento
                    "preco_venda": None,
                    "valor_recebido_usdt": None,
                    "lucro_usdt": None,
                    "lucro_pct": None,
                    "total_impostos_usdt": None,
                    "texto_status": None # O "Juiz" preenche isso no final
                }
                
                try:
                    supabase.table("operacoes").insert(nova_operacao).execute()
                    st.success("Operação registrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
            else:
                st.warning("Preencha os valores corretamente.")

# ==================================================
# ABA 2: OPERAÇÕES EM ABERTO (Gestão)
# ==================================================
with aba_abertas:
    if not abertas_bd:
        st.info("Nenhuma operação em aberto no momento.")
    else:
        for op in abertas_bd:
            with st.expander(f"🆔 {op['display_id']} | Compra: ${op['preco_compra']:,.2f} ({op['texto_data_abertura_br']})"):
                c1, c2, c3, c4 = st.columns(4)
                
                with c1:
                    st.metric("Investido", f"${op['valor_investido_usdt']:.2f}")
                with c2:
                    st.metric("Qtd BTC", f"{op['quantidade_btc']:.6f}")
                with c3:
                    # Simulação em Tempo Real
                    valor_atual = op['quantidade_btc'] * cotacao_atual
                    pnl_atual = valor_atual - op['valor_investido_usdt']
                    cor_pnl = "normal" if pnl_atual >= 0 else "off" # Streamlit delta color logic
                    st.metric("PnL (Agora)", f"${pnl_atual:.2f}", delta=f"{pnl_atual:.2f}")
                
                st.divider()
                st.write("🔴 **ENCERRAR OPERAÇÃO**")
                
                col_fecha_1, col_fecha_2, col_fecha_3 = st.columns(3)
                
                with col_fecha_1:
                    preco_saida = st.number_input(f"Preço de Venda (BTC) - ID {op['display_id']}", value=cotacao_atual, step=100.0)
                with col_fecha_2:
                    taxa_saida_pct = st.number_input(f"Taxa Saída (%) - ID {op['display_id']}", value=0.1, step=0.01)
                with col_fecha_3:
                    # Parâmetros para o Juiz
                    alvo_definido = st.number_input(f"Alvo Original - ID {op['display_id']}", value=0.0)
                    stop_definido = st.number_input(f"Stop Original - ID {op['display_id']}", value=0.0)

                if st.button(f"Confirmar Fechamento (ID {op['display_id']})", type="primary"):
                    # Cálculos Finais
                    valor_bruto_venda = op['quantidade_btc'] * preco_saida
                    taxa_saida_usd = valor_bruto_venda * (taxa_saida_pct / 100)
                    valor_liquido_recebido = valor_bruto_venda - taxa_saida_usd
                    
                    lucro_final = valor_liquido_recebido - op['valor_investido_usdt']
                    lucro_pct = (lucro_final / op['valor_investido_usdt']) * 100
                    custo_total = op['taxa_entrada_usdt'] + taxa_saida_usd
                    
                    agora_fecha = datetime.datetime.now(fuso_brasilia)
                    
                    # O Veredito do Juiz
                    veredito = avaliar_comportamento(op['preco_compra'], preco_saida, alvo_definido, stop_definido)
                    
                    dados_fechamento = {
                        "status": "Fechado",
                        "data_fechamento": str(agora_fecha.date()),
                        "hora_fechamento": str(agora_fecha.strftime("%H:%M")),
                        "texto_data_fechamento_br": agora_fecha.strftime("%d/%m/%Y"),
                        "preco_venda": preco_saida,
                        "valor_recebido_usdt": valor_liquido_recebido,
                        "lucro_usdt": lucro_final,
                        "lucro_pct": lucro_pct,
                        "total_impostos_usdt": custo_total,
                        "texto_status": veredito # Gravando a sentença
                    }
                    
                    try:
                        # Update seguro usando o ID específico
                        supabase.table("operacoes").update(dados_fechamento).eq("id", op['id']).execute()
                        st.toast(f"Operação {op['display_id']} encerrada com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao fechar: {e}")

# ==================================================
# ABA 3: HISTÓRICO (Diário de Bordo)
# ==================================================
with aba_historico:
    if not fechadas_bd:
        st.info("Nenhuma operação finalizada ainda.")
    else:
        # Exibir da mais recente para a mais antiga
        for op in reversed(fechadas_bd):
            cor_card = "rgba(22, 163, 74, 0.1)" if op['lucro_usdt'] >= 0 else "rgba(220, 38, 38, 0.1)"
            borda = "#16a34a" if op['lucro_usdt'] >= 0 else "#dc2626"
            emoji_juiz = op['texto_status'] if op['texto_status'] else "---"
            
            st.markdown(f"""
                <div style="background-color: {cor_card}; border-left: 5px solid {borda}; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 1.1em;">🆔 {op['display_id']} | {op['texto_data_abertura_br']} ➝ {op['texto_data_fechamento_br']}</span>
                        <span style="font-size: 0.9em; background-color: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 15px;">{emoji_juiz}</span>
                    </div>
                    <div style="margin-top: 10px; display: flex; gap: 20px;">
                        <span>Entrada: <b>${op['preco_compra']:,.2f}</b></span>
                        <span>Saída: <b>${op['preco_venda']:,.2f}</b></span>
                        <span>Resultado: <b style="color: {borda};">${op['lucro_usdt']:.2f} ({op['lucro_pct']:.2f}%)</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
