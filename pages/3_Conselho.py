import streamlit as st
import datetime
import requests
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

# ==============================================================================
# BLOCO 1: CONFIGURAÇÃO DA PÁGINA E SEGURANÇA
# ==============================================================================
st.set_page_config(page_title="Portfólio - O Conselho", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

if not st.session_state.get("autenticado", False):
    st.switch_page("main.py")

# ==============================================================================
# BLOCO 2: CONEXÃO E CONFIGURAÇÕES DE ATIVOS
# ==============================================================================
@st.cache_resource
def iniciar_conexao():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase: Client = iniciar_conexao()
except Exception as e:
    st.error("⚠️ Erro no Banco de Dados.")
    st.stop()

ASSETS_CONFIG = {
    "BTC": {"nome": "Bitcoin", "icon": "🟠", "cor": "#F3BA2F"},
    "ETH": {"nome": "Ethereum", "icon": "💠", "cor": "#627EEA"},
    "SOL": {"nome": "Solana", "icon": "🟣", "cor": "#14F195"},
    "BNB": {"nome": "Binance Coin", "icon": "🟡", "cor": "#F3BA2F"},
    "PAXG": {"nome": "PAX Gold", "icon": "🏆", "cor": "#D4AF37"}
}

# ==============================================================================
# BLOCO 3: ESTILIZAÇÃO CSS (O CORAÇÃO DO VISUAL)
# ==============================================================================
st.markdown("""
<style>
    [data-testid="collapsedControl"], [data-testid="stSidebar"] {display: none !important;}
    
    /* Menu de Navegação */
    [data-testid="stPageLink-NavLink"] {
        width: 100%; padding: 5px 15px; border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    
    /* Cards de Métricas Gerais (Topo) */
    .metric-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 8px;
        display: flex; flex-direction: column; justify-content: center; height: 100%;
        transition: transform 0.2s ease;
    }
    .card-capital { border-top: 3px solid #F3BA2F; }
    .card-pnl { border-top: 3px solid #3b82f6; }
    .card-realizado { border-top: 3px solid #10b981; }
    .card-winrate { border-top: 3px solid #8b5cf6; }

    /* Mini Cards de Destaque (Herói/Vilão) */
    .highlight-card {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(255, 255, 255, 0.05); padding: 12px; border-radius: 8px;
        text-align: center;
    }

    /* Cards Largos do Cofre */
    .asset-row {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8)) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-top: 3px solid #F3BA2F !important; border-radius: 8px !important;
        padding: 15px 25px !important; margin-bottom: 15px !important;
        display: flex !important; align-items: center !important; justify-content: space-between !important;
    }
    .asset-identity { display: flex !important; align-items: center !important; gap: 15px !important; width: 20% !important; }
    .asset-stats-container { display: flex !important; justify-content: space-between !important; flex-grow: 1 !important; align-items: center; }
    .asset-label { font-size: 0.7em !important; color: #9ca3af !important; text-transform: uppercase; margin-bottom: 4px; }
    .asset-value { font-size: 1.1em !important; font-weight: bold !important; color: white; }
    .vertical-divider { width: 1px !important; height: 30px !important; background-color: rgba(255, 255, 255, 0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# BLOCO 4: PROCESSAMENTO DE DADOS (LÓGICA)
# ==============================================================================
def carregar_dados():
    user_id = st.session_state.get("user_id")
    res = supabase.table("operacoes").select("*").eq("user_id", user_id).execute().data
    for i, d in enumerate(sorted(res, key=lambda x: x['id'])):
        d['display_id'] = f"{(i + 1):03d}"
        if 'simbolo' not in d or not d['simbolo']: d['simbolo'] = 'BTC'
    return [d for d in res if d['status'] == 'Aberto'], [d for d in res if d['status'] == 'Fechado']

ordens_abertas, historico_fechado = carregar_dados()

# Preços em tempo real
simbolos = list(set([o['simbolo'] for o in ordens_abertas]))
precos = {}
for s in simbolos:
    try: precos[s] = float(requests.get(f"https://api.binance.us/api/v3/ticker/price?symbol={s}USDT").json()["price"])
    except: precos[s] = 0.0

# ==============================================================================
# BLOCO 5: CABEÇALHO E NAVEGAÇÃO
# ==============================================================================
c_t, c_h, c_c = st.columns([6, 2, 2], vertical_alignment="center")
c_t.title("💼 Cockpit de Performance")
c_h.page_link("pages/0_Terminal.py", label="Início", icon="🏠")
c_c.page_link("pages/1_Calculadora.py", label="Calculadora", icon="🧮")
st.divider()

# ==============================================================================
# BLOCO 6: MÉTRICAS GERAIS (TOPO)
# ==============================================================================
total_inv = sum(float(o['valor_investido_usdt']) for o in ordens_abertas)
val_mercado = sum(float(o['quantidade_btc']) * precos.get(o['simbolo'], 0) for o in ordens_abertas)
pnl_f = val_mercado - total_inv
pnl_p = (pnl_f / total_inv * 100) if total_inv > 0 else 0
lucro_r = sum(float(o.get('lucro_usdt', 0)) for o in historico_fechado)
taxa_a = (sum(1 for o in historico_fechado if float(o.get('lucro_usdt',0)) > 0) / len(historico_fechado) * 100) if historico_fechado else 0

col1, col2, col3, col4 = st.columns(4)
with col1: st.markdown(f'<div class="metric-card card-capital"><div class="metric-title">Capital Alocado</div><div class="metric-value">${total_inv:,.2f}</div></div>', unsafe_allow_html=True)
with col2: st.markdown(f'<div class="metric-card card-pnl"><div class="metric-title">PnL Flutuante</div><div class="metric-value">{" " if pnl_f >= 0 else "-"}${abs(pnl_f):,.2f}</div><div class="metric-sub">{pnl_p:+.2f}%</div></div>', unsafe_allow_html=True)
with col3: st.markdown(f'<div class="metric-card card-realizado"><div class="metric-title">Lucro Realizado</div><div class="metric-value">{" " if lucro_r >= 0 else "-"}${abs(lucro_r):,.2f}</div></div>', unsafe_allow_html=True)
with col4: st.markdown(f'<div class="metric-card card-winrate"><div class="metric-title">Taxa de Acerto</div><div class="metric-value">{taxa_a:.1f}%</div></div>', unsafe_allow_html=True)

# ==============================================================================
# BLOCO 7: SEÇÃO DE ANÁLISE VISUAL (GRÁFICOS)
# ==============================================================================
st.markdown("<br>", unsafe_allow_html=True)
col_rel, col_per = st.columns([1.1, 0.9], gap="large")

with col_rel:
    st.subheader("📋 Relatórios")
    # Aqui entrariam as tabelas do Pandas (removidas para brevidade, mas mantendo o espaço)

with col_per:
    st.subheader("📊 Raio-X")
    # Gráfico de Curva de Capital (Plotly)

# ==============================================================================
# BLOCO 8: SEÇÃO COFRE DOS ATIVOS (A ÁREA DO PROBLEMA)
# ==============================================================================
st.markdown("<br><br><div style='width: 100%; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(243, 186, 47, 0.5), rgba(255,255,255,0.05)); margin-bottom: 30px;'></div>", unsafe_allow_html=True)
st.subheader("🏦 Cofre dos Ativos")

# Processamento consolidado
stats_ativos = {}
for o in (historico_fechado + ordens_abertas):
    s = o['simbolo']
    if s not in stats_ativos: stats_ativos[s] = {'lucro_r': 0.0, 'inv_a': 0.0, 'qtd_a': 0.0, 'trades': 0, 'wins': 0}
    if o['status'] == 'Fechado':
        stats_ativos[s]['lucro_r'] += float(o['lucro_usdt'])
        stats_ativos[s]['trades'] += 1
        if float(o['lucro_usdt']) > 0: stats_ativos[s]['wins'] += 1
    else:
        stats_ativos[s]['inv_a'] += float(o['valor_investido_usdt'])
        stats_ativos[s]['qtd_a'] += float(o['quantidade_btc'])

# --- SUB-BLOCO: DESTAQUES ---
col_gr, col_ds = st.columns([1.2, 2], gap="large")

with col_ds:
    st.markdown("##### 🏆 Destaques")
    d1, d2, d3 = st.columns(3)
    melhor = max(stats_ativos.items(), key=lambda x: x[1]['lucro_r'], default=(None, None))
    pior = min(stats_ativos.items(), key=lambda x: x[1]['lucro_r'], default=(None, None))
    maior_e = max(stats_ativos.items(), key=lambda x: x[1]['inv_a'], default=(None, None))

    def draw_highlight(col, title, ativo, val, color):
        if ativo:
            ic = ASSETS_CONFIG.get(ativo, {}).get("icon", "")
            col.markdown(f'<div class="highlight-card" style="border-top: 3px solid {color};"><div style="font-size:0.65em; color:gray;">{title}</div><div style="font-weight:bold;">{ic} {ativo}</div><div style="color:{color};">${abs(val):,.2f}</div></div>', unsafe_allow_html=True)

    draw_highlight(d1, "MAIOR LUCRO", melhor[0], melhor[1]['lucro_r'], "#22c55e")
    draw_highlight(d2, "MAIOR PREJUÍZO", pior[0], pior[1]['lucro_r'], "#ef4444")
    draw_highlight(d3, "MAIOR EXPOSIÇÃO", maior_e[0], maior_e[1]['inv_a'], "#eab308")

with col_gr:
    # Gráfico de Rosca Corrigido
    labels = [s for s, d in stats_ativos.items() if d['inv_a'] > 0]
    values = [d['inv_a'] for s, d in stats_ativos.items() if d['inv_a'] > 0]
    if values:
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, textinfo='percent', textposition='outside', marker=dict(colors=[ASSETS_CONFIG.get(s, {}).get("cor", "#888") for s in labels]))])
        fig.update_layout(margin=dict(l=30, r=30, t=30, b=80), height=320, paper_bgcolor='rgba(0,0,0,0)', showlegend=False,
                          annotations=[dict(text=f"Total<br>${total_inv:,.0f}", x=0.5, y=0.5, font_size=14, showarrow=False, font_color="white")])
        st.plotly_chart(fig, use_container_width=True)

# --- SUB-BLOCO: CARDS DETALHADOS ---
st.markdown("<br>##### 📜 Detalhes", unsafe_allow_html=True)
for s in sorted(stats_ativos.keys()):
    d = stats_ativos[s]
    ic = ASSETS_CONFIG.get(s, {}).get("icon", "🪙")
    # Lógica do Status (PM)
    if d['qtd_a'] > 0:
        pm = d['inv_a'] / d['qtd_a']
        cot = precos.get(s, 0)
        status_html = f'<div class="asset-stat-box"><div class="asset-label">Status</div><div class="asset-value" style="color:{"#22c55e" if cot >= pm else "#ef4444"};">${cot:,.2f}</div></div>'
    else: status_html = '<div class="asset-stat-box"><div class="asset-label">Status</div><div class="asset-value" style="color:gray;">Zerado</div></div>'

    # CARD HTML SEM INDENTAÇÃO INTERNA (PARA EVITAR BUG)
    html_card = f"""
<div class="asset-row">
<div class="asset-identity"><div class="asset-icon-large">{ic}</div><div class="asset-name-large">{s}</div></div>
<div class="asset-stats-container">
{status_html}
<div class="vertical-divider"></div>
<div class="asset-stat-box"><div class="asset-label">Lucro Realizado</div><div class="asset-value" style="color:{"#22c55e" if d['lucro_r'] >=0 else "#ef4444"};">${d['lucro_r']:,.2f}</div></div>
<div class="vertical-divider"></div>
<div class="asset-stat-box"><div class="asset-label">Acertos</div><div class="asset-value">{(d['wins']/d['trades']*100 if d['trades']>0 else 0):.0f}%</div></div>
<div class="vertical-divider"></div>
<div class="asset-stat-box"><div class="asset-label">Trades</div><div class="asset-value">{d['trades']}</div></div>
</div>
</div>
"""
    st.markdown(html_card, unsafe_allow_html=True)
