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

# Cadeado de Segurança
if not st.session_state.get("autenticado", False):
    st.switch_page("main.py")

# ==============================================================================
# BLOCO 2: CONEXÃO COM BANCO DE DADOS
# ==============================================================================
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

# Configuração de Ativos (Cores e Ícones)
ASSETS_CONFIG = {
    "BTC": {"nome": "Bitcoin", "icon": "🟠", "cor": "#F3BA2F"},
    "ETH": {"nome": "Ethereum", "icon": "💠", "cor": "#627EEA"},
    "SOL": {"nome": "Solana", "icon": "🟣", "cor": "#14F195"},
    "BNB": {"nome": "Binance Coin", "icon": "🟡", "cor": "#F3BA2F"},
    "PAXG": {"nome": "PAX Gold", "icon": "🏆", "cor": "#D4AF37"}
}

# ==============================================================================
# BLOCO 3: ESTILIZAÇÃO (CSS)
# ==============================================================================
st.markdown("""
    <style>
        /* Remove elementos padrões do Streamlit */
        [data-testid="collapsedControl"] {display: none !important;}
        [data-testid="stSidebar"] {display: none !important;}
        
        /* Botões de Navegação */
        [data-testid="stPageLink-NavLink"] {
            width: 100%;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            text-align: center;
        }
        
        /* CARDS DO TOPO (Métricas Gerais) */
        .metric-card {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
        }
        .card-capital { border-top: 3px solid #F3BA2F; }
        .card-pnl { border-top: 3px solid #3b82f6; }
        .card-realizado { border-top: 3px solid #10b981; }
        .card-winrate { border-top: 3px solid #8b5cf6; }

        .metric-title {
            color: #9ca3af;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: white;
        }
        .metric-sub {
            font-size: 0.9em;
            margin-top: 5px;
        }
        .text-green { color: #16a34a; }
        .text-red { color: #dc2626; }
        .text-gray { color: #6b7280; }
        .text-gold { color: #F3BA2F; }
        
        /* CARDS PEQUENOS (Mini Metrics) */
        .mini-metric {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8));
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 15px 5px;
            text-align: center;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .mini-metric:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        }
        .mini-label {
            font-size: 0.8em;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 10px;
            display: block;
        }

        /* CARDS LARGOS DO COFRE (Asset Rows) */
        .asset-row {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8)) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-top: 3px solid #F3BA2F !important;
            border-radius: 8px !important;
            padding: 15px 25px !important;
            margin-bottom: 15px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        .asset-row:hover {
            transform: translateX(5px) !important;
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4) !important;
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9)) !important;
        }
        .asset-identity {
            display: flex !important;
            align-items: center !important;
            gap: 15px !important;
            width: 20% !important;
        }
        .asset-icon-large { font-size: 2em !important; }
        .asset-name-large { font-size: 1.2em !important; font-weight: bold !important; color: white !important; letter-spacing: 1px !important; }
        
        .asset-stats-container {
            display: flex !important;
            justify-content: space-between !important;
            flex-grow: 1 !important;
            align-items: center !important;
            margin-left: 20px !important;
        }
        .asset-stat-box { text-align: center !important; min-width: 80px !important; }
        .asset-label { font-size: 0.7em !important; color: #9ca3af !important; text-transform: uppercase !important; letter-spacing: 0.5px !important; margin-bottom: 4px !important; font-family: sans-serif !important; }
        .asset-value { font-size: 1.1em !important; font-weight: bold !important; font-family: sans-serif !important; }
        
        .vertical-divider {
            width: 1px !important;
            height: 30px !important;
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# BLOCO 4: FUNÇÕES AUXILIARES (API & DADOS)
# ==============================================================================
def obter_dicionario_precos(lista_simbolos):
    precos = {}
    if not lista_simbolos: return precos
    lista_limpa = list(set([s for s in lista_simbolos if s]))
    for simb in lista_limpa:
        try:
            par = f"{simb}USDT"
            url = f"https://api.binance.us/api/v3/ticker/price?symbol={par}"
            resposta = requests.get(url, timeout=2)
            if resposta.status_code == 200:
                precos[simb] = float(resposta.json()["price"])
            else:
                precos[simb] = 0.0
        except:
            precos[simb] = 0.0
    return precos

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

# ==============================================================================
# BLOCO 5: EXECUÇÃO PRINCIPAL & MENU
# ==============================================================================
col_titulo, col_btn_home, col_btn_calc = st.columns([6, 2, 2], vertical_alignment="center")
with col_titulo:
    st.title("💼 Cockpit de Performance")
with col_btn_home:
    st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="🏠")
with col_btn_calc:
    st.page_link("pages/1_Calculadora.py", label="Ir para Calculadora", icon="🧮")

st.divider()

if 'dados_sincronizados' not in st.session_state:
    with st.spinner("Sincronizando Portfólio..."):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.session_state['dados_sincronizados'] = True

# Botão Invisível de Refresh (para debug)
col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Atualizar Dados"):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.rerun()

ordens_abertas = st.session_state.get('ordens_abertas', [])
historico_fechado = st.session_state.get('historico_fechado', [])

# ==============================================================================
# BLOCO 6: MOTOR DE CÁLCULO (MATEMÁTICA)
# ==============================================================================
simbolos_em_aberto = list(set([o['simbolo'] for o in ordens_abertas]))
cotacoes_atuais = obter_dicionario_precos(simbolos_em_aberto)

total_investido_aberto = sum(float(o['valor_investido_usdt']) for o in ordens_abertas)

valor_mercado_atual_total = 0.0
for o in ordens_abertas:
    simb = o.get('simbolo', 'BTC')
    preco_atual = cotacoes_atuais.get(simb, 0.0)
    qtd = float(o['quantidade_btc']) 
    valor_mercado_atual_total += qtd * preco_atual

pnl_flutuante = valor_mercado_atual_total - total_investido_aberto
pnl_flutuante_pct = (pnl_flutuante / total_investido_aberto * 100) if total_investido_aberto > 0 else 0.0

lucro_realizado_total = sum(float(o.get('lucro_usdt', 0)) for o in historico_fechado)
total_taxas_pagas = sum(float(o.get('total_taxas_usdt', 0)) for o in historico_fechado) + sum(float(o.get('taxa_entrada_usdt', 0)) for o in ordens_abertas)

ordens_vencedoras = sum(1 for o in historico_fechado if float(o.get('lucro_usdt', 0)) > 0)
total_ordens_fechadas = len(historico_fechado)
win_rate = (ordens_vencedoras / total_ordens_fechadas * 100) if total_ordens_fechadas > 0 else 0.0

# Cálculos de Streak e Médias
media_gain = 0.0
media_loss = 0.0
streak_count = 0
streak_tipo = "Nenhum"
icone_streak = "➖"

if historico_fechado:
    gains = [float(o['lucro_usdt']) for o in historico_fechado if float(o.get('lucro_usdt', 0)) > 0]
    losses = [float(o['lucro_usdt']) for o in historico_fechado if float(o.get('lucro_usdt', 0)) < 0]
    if gains: media_gain = sum(gains) / len(gains)
    if losses: media_loss = sum(losses) / len(losses)
    
    historico_cronologico = sorted(historico_fechado, key=lambda x: f"{x['data_fechamento']} {x['hora_fechamento']}")
    ordens_reversas = list(reversed(historico_cronologico))
    ultimo_resultado_positivo = float(ordens_reversas[0].get('lucro_usdt', 0)) > 0
    streak_tipo = "Lucro" if ultimo_resultado_positivo else "Prejuízo"
    icone_streak = "🔥" if ultimo_resultado_positivo else "🧊"
    for o in ordens_reversas:
        l_usdt = float(o.get('lucro_usdt', 0))
        if (l_usdt > 0 and ultimo_resultado_positivo) or (l_usdt < 0 and not ultimo_resultado_positivo):
            streak_count += 1
        elif l_usdt == 0: continue
        else: break

# Tempo Médio
tempos_operacao = []
tempo_medio_str = "0m"
for o in historico_fechado:
    try:
        dt_abertura = datetime.datetime.strptime(f"{o['data_abertura']} {o['hora_abertura']}", "%Y-%m-%d %H:%M")
        dt_fechamento = datetime.datetime.strptime(f"{o['data_fechamento']} {o['hora_fechamento']}", "%Y-%m-%d %H:%M")
        tempos_operacao.append((dt_fechamento - dt_abertura).total_seconds())
    except: pass
if tempos_operacao:
    media_seg = sum(tempos_operacao) / len(tempos_operacao)
    horas = int(media_seg // 3600)
    minutos = int((media_seg % 3600) // 60)
    tempo_medio_str = f"{horas}h {minutos}m" if horas > 0 else f"{minutos}m"

# ==============================================================================
# BLOCO 7: VISUALIZAÇÃO - CARDS TOPO
# ==============================================================================
st.subheader("Visão Geral do Portfólio")
col1, col2, col3, col4 = st.columns(4)

cor_flutuante = "text-green" if pnl_flutuante >= 0 else "text-red"
sinal_flutuante = "+" if pnl_flutuante >= 0 else "-"
cor_realizado = "text-green" if lucro_realizado_total >= 0 else "text-red"
sinal_realizado = "+" if lucro_realizado_total >= 0 else "-"
cor_winrate = "text-green" if win_rate >= 50 else ("text-red" if total_ordens_fechadas > 0 else "text-gray")

with col1:
    st.markdown(f"""<div class="metric-card card-capital"><div class="metric-title">Capital Alocado (Risco)</div><div class="metric-value">&#36;{total_investido_aberto:,.2f}</div><div class="metric-sub text-gold">Multi-Ativos</div></div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-card card-pnl"><div class="metric-title">PnL Flutuante (Abertas)</div><div class="metric-value {cor_flutuante}">{sinal_flutuante}&#36;{abs(pnl_flutuante):,.2f}</div><div class="metric-sub {cor_flutuante}">{sinal_flutuante}{abs(pnl_flutuante_pct):,.2f}% sobre o investido</div></div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class="metric-card card-realizado"><div class="metric-title">Lucro Líquido Realizado</div><div class="metric-value {cor_realizado}">{sinal_realizado}&#36;{abs(lucro_realizado_total):,.2f}</div><div class="metric-sub text-gray">De {total_ordens_fechadas} ordens fechadas</div></div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class="metric-card card-winrate"><div class="metric-title">Taxa de Acerto</div><div class="metric-value {cor_winrate}">{win_rate:.1f}%</div><div class="metric-sub text-gray">Ordens Positivas: {ordens_vencedoras}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# BLOCO 8: VISUALIZAÇÃO - LISTAS E TABELAS
# ==============================================================================
col_tabelas, col_lateral = st.columns([1.1, 0.9], gap="large")

with col_tabelas:
    st.subheader("📋 Relatórios de Custódia")
    aba_abertas, aba_fechadas = st.tabs(["🟢 Ordens em aberto", "🎯 Ordens finalizadas"])

    def pintar_tabela(val):
        if isinstance(val, (int, float)):
            if val > 0: return 'color: #16a34a; font-weight: bold;'
            elif val < 0: return 'color: #dc2626; font-weight: bold;'
        return 'color: gray;'

    with aba_abertas:
        if not ordens_abertas:
            st.info("Sua carteira está vazia. Nenhuma ordem aberta no momento.")
        else:
            dados_abertas = []
            for o in ordens_abertas:
                simb = o.get('simbolo', 'BTC')
                preco_atual_ativo = cotacoes_atuais.get(simb, 0.0)
                valor_atual_ordem = float(o['quantidade_btc']) * preco_atual_ativo
                pnl_dolar = valor_atual_ordem - float(o['valor_investido_usdt'])
                pnl_pct = (pnl_dolar / float(o['valor_investido_usdt'])) * 100
                icone = ASSETS_CONFIG.get(simb, {}).get("icon", "🪙")
                dados_abertas.append({
                    'Ativo': f"{icone} {simb}",
                    'Investido': float(o['valor_investido_usdt']),
                    'Volume': float(o['quantidade_btc']),
                    'PnL Atual ($)': pnl_dolar,
                    'Rentabilidade (%)': pnl_pct,
                    'ID': f"#{o.get('display_id', '???')}"
                })
            df_abertas = pd.DataFrame(dados_abertas)
            st.dataframe(df_abertas.style.map(pintar_tabela, subset=['PnL Atual ($)', 'Rentabilidade (%)']).format({'Investido': '${:,.2f}','Volume': '{:.6f}','PnL Atual ($)': '${:,.2f}','Rentabilidade (%)': '{:+.2f}%'}), use_container_width=True, hide_index=True)

    with aba_fechadas:
        if not historico_fechado:
            st.info("Nenhuma ordem foi liquidada ainda.")
        else:
            dados_fechadas = []
            for o in historico_fechado:
                simb = o.get('simbolo', 'BTC')
                icone = ASSETS_CONFIG.get(simb, {}).get("icon", "🪙")
                dados_fechadas.append({
                    'Ativo': f"{icone} {simb}",
                    'Retorno Final': float(o.get('valor_recebido_usdt', 0)),
                    'Lucro Líquido ($)': float(o.get('lucro_usdt', 0)),
                    'Rentabilidade (%)': float(o.get('lucro_pct', 0)),
                    'Disciplina': o.get('comportamento_final', "---"),
                    'ID': f"#{o.get('display_id', '???')}"
                })
            df_fechadas = pd.DataFrame(dados_fechadas)
            st.dataframe(df_fechadas.style.map(pintar_tabela, subset=['Lucro Líquido ($)', 'Rentabilidade (%)']).format({'Retorno Final': '${:,.2f}','Lucro Líquido ($)': '${:,.2f}','Rentabilidade (%)': '{:+.2f}%'}), use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div style="background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(255, 255, 255, 0.05); padding: 8px 15px; border-radius: 6px; display: inline-block; font-size: 0.85em;"><span style="color: #9ca3af;">Custo Operacional Acumulado:</span> <strong style="color: #e2e8f0; margin-left: 5px;">&#36;{total_taxas_pagas:.4f}</strong></div>""", unsafe_allow_html=True)

# ==============================================================================
# BLOCO 9: VISUALIZAÇÃO - ANÁLISE LATERAL E GRÁFICOS
# ==============================================================================
with col_lateral:
    st.subheader("📊 Raio-X de Performance")
    loss_rate = 100.0 - win_rate if total_ordens_fechadas > 0 else 0.0
    
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-family: sans-serif;">
                <span style="color: #22c55e; font-weight: 600; font-size: 0.95em; text-shadow: 0 0 5px rgba(34,197,94,0.3);">🟢 Acertos {win_rate:.0f}%</span>
                <span style="color: #ef4444; font-weight: 600; font-size: 0.95em; text-shadow: 0 0 5px rgba(239,68,68,0.3);">Erros {loss_rate:.0f}% 🔴</span>
            </div>
            <div style="width: 100%; height: 12px; background-color: rgba(239,68,68,0.2); border-radius: 6px; overflow: hidden; display: flex; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);">
                <div style="width: {win_rate}%; background: linear-gradient(90deg, #16a34a, #22c55e); height: 100%; box-shadow: 0 0 10px rgba(34,197,94,0.4);"></div>
                <div style="width: {loss_rate}%; background: linear-gradient(90deg, #dc2626, #ef4444); height: 100%; box-shadow: 0 0 10px rgba(239,68,68,0.4);"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_payoff, col_streak, col_tempo = st.columns(3)
    cor_streak = "#22c55e" if streak_tipo == "Lucro" else "#ef4444" if streak_tipo == "Prejuízo" else "gray"
    
    with col_payoff:
        st.markdown(f"""<div class="mini-metric"><div class="mini-label">Média (L/P)</div><div style="font-size: 1.1em; font-weight: bold;"><span style="color: #22c55e;">+${media_gain:.2f}</span> <span style="color: rgba(255,255,255,0.2);">|</span> <span style="color: #ef4444;">-${abs(media_loss):.2f}</span></div></div>""", unsafe_allow_html=True)
    with col_streak:
        st.markdown(f"""<div class="mini-metric"><div class="mini-label">Sequência</div><div style="font-size: 1.2em; font-weight: bold; color: {cor_streak};">{icone_streak} {streak_count} {streak_tipo}s</div></div>""", unsafe_allow_html=True)
    with col_tempo:
        st.markdown(f"""<div class="mini-metric"><div class="mini-label">Tempo Médio</div><div style="font-size: 1.2em; font-weight: bold; color: white;">⏱️ {tempo_medio_str}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.9em; color: #9ca3af; margin-bottom: 10px; margin-top: 15px;'>Curva de Capital (Acumulado)</div>", unsafe_allow_html=True)
    if not historico_fechado:
        st.info("O gráfico aparecerá após sua primeira venda.")
    else:
        df_hist = pd.DataFrame(historico_fechado)
        df_hist['Datahora'] = pd.to_datetime(df_hist['data_fechamento'] + ' ' + df_hist['hora_fechamento'])
        df_hist = df_hist.sort_values('Datahora').reset_index(drop=True)
        
        lucro_acumulado = 0.0
        eixo_x, eixo_y, labels_x = [], [], []
        for i, row in df_hist.iterrows():
            lucro_acumulado += float(row.get('lucro_usdt', 0))
            eixo_x.append(i + 1)
            eixo_y.append(lucro_acumulado)
            labels_x.append(f"#{row.get('display_id', '???')}")
            
        cor_grafico = "#22c55e" if eixo_y and eixo_y[-1] >= 0 else "#ef4444"
        cor_fundo = "rgba(34, 197, 94, 0.1)" if eixo_y and eixo_y[-1] >= 0 else "rgba(239, 68, 68, 0.1)"
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=eixo_x, y=eixo_y, mode='lines+markers', name='Lucro Acum.', line=dict(color=cor_grafico, width=3, shape='spline'), marker=dict(size=8, color=cor_grafico, line=dict(color='white', width=1)), fill='tozeroy', fillcolor=cor_fundo, customdata=labels_x, hovertemplate="<b>Ordem %{customdata}</b><br>Acumulado: $%{y:.2f}<extra></extra>"))
        fig.update_layout(height=320, margin=dict(l=0, r=0, t=30, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False, zeroline=False, showticklabels=False), yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=True, zerolinecolor="rgba(255,255,255,0.2)"), hovermode="x unified", hoverlabel=dict(bgcolor="rgba(30, 41, 59, 0.95)"))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# DNA Operacional
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""<div style="width: 100%; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(243, 186, 47, 0.5), rgba(255,255,255,0.05)); margin-bottom: 30px;"></div>""", unsafe_allow_html=True)
st.subheader("🧬 DNA Operacional", help="Análise de disciplina.")

contagem = {"🏆 Sniper": 0, "🥬 Mão de Alface": 0, "🛡️ Saída Estratégica": 0, "🛑 Resiliência": 0, "💥 Descontrole": 0}
total_dna = 0
for o in historico_fechado:
    c = o.get('comportamento_final')
    if c in contagem: 
        contagem[c] += 1
        total_dna += 1

if total_dna > 0:
    dados_grafico = {k: v for k, v in contagem.items() if v > 0}
    c_dna1, c_dna2 = st.columns([1, 2], gap="large")
    cores_map = {"🏆 Sniper": "#10b981", "🥬 Mão de Alface": "#F3BA2F", "🛡️ Saída Estratégica": "#64748b", "🛑 Resiliência": "#f97316", "💥 Descontrole": "#ef4444"}
    
    with c_dna1:
        labels = list(dados_grafico.keys())
        colors = [cores_map.get(l, "gray") for l in labels]
        fig_dna = go.Figure(data=[go.Pie(labels=labels, values=list(dados_grafico.values()), hole=.6, marker=dict(colors=colors, line=dict(color='#0f172a', width=3)), textinfo='percent', textposition='outside', showlegend=False)])
        fig_dna.update_layout(margin=dict(l=10, r=10, t=10, b=50), height=250, paper_bgcolor='rgba(0,0,0,0)', annotations=[dict(text=f"{total_dna}", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="white")])
        st.plotly_chart(fig_dna, use_container_width=True)
    with c_dna2:
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        for item, qtd in dados_grafico.items():
            pct = (qtd / total_dna) * 100
            cor = cores_map.get(item, "gray")
            st.markdown(f"""<div style="margin-bottom: 12px;"><div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span style="color: #e2e8f0; font-size: 0.9em; font-weight: 500;">{item}</span></div><div style="width: 100%; background-color: rgba(255,255,255,0.05); height: 8px; border-radius: 4px;"><div style="width: {pct}%; background-color: {cor}; height: 100%; border-radius: 4px;"></div></div></div>""", unsafe_allow_html=True)
else:
    st.info("Aguardando operações com Alvo/Stop para gerar DNA.")

# Comparação Comportamental
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""<div style="border-top: 1px dashed rgba(255,255,255,0.1); margin: 20px 0;"></div>""", unsafe_allow_html=True)
st.subheader("⚖️ Comparação Comportamental")

ops_est = [o for o in historico_fechado if o.get('teve_projecao')]
ops_liv = [o for o in historico_fechado if not o.get('teve_projecao')]

lucro_est = sum(o['lucro_usdt'] for o in ops_est)
lucro_liv = sum(o['lucro_usdt'] for o in ops_liv)
wr_est = (sum(1 for o in ops_est if o['lucro_usdt'] > 0) / len(ops_est) * 100) if ops_est else 0.0
wr_liv = (sum(1 for o in ops_liv if o['lucro_usdt'] > 0) / len(ops_liv) * 100) if ops_liv else 0.0
media_est = (lucro_est / len(ops_est)) if ops_est else 0.0
media_liv = (lucro_liv / len(ops_liv)) if ops_liv else 0.0

cc1, cc2, cc3 = st.columns(3)
with cc1: st.markdown(f"""<div class="mini-metric"><span class="mini-label">LUCRO LÍQUIDO</span><div style="display: flex; justify-content: space-around;"><div style="text-align: center;"><div style="color: #3b82f6; font-size: 1.5em; font-weight: bold;">${lucro_est:.2f}</div><div style="font-size: 0.7em; color: #3b82f6;">planejado</div></div><div style="border-left: 1px solid rgba(255,255,255,0.1);"></div><div style="text-align: center;"><div style="color: #F3BA2F; font-size: 1.5em; font-weight: bold;">${lucro_liv:.2f}</div><div style="font-size: 0.7em; color: #F3BA2F;">livre</div></div></div></div>""", unsafe_allow_html=True)
with cc2: st.markdown(f"""<div class="mini-metric"><span class="mini-label">TAXA DE ACERTO</span><div style="display: flex; justify-content: space-around;"><div style="text-align: center;"><div style="color: #3b82f6; font-size: 1.5em; font-weight: bold;">{wr_est:.0f}%</div><div style="font-size: 0.7em; color: #3b82f6;">planejado</div></div><div style="border-left: 1px solid rgba(255,255,255,0.1);"></div><div style="text-align: center;"><div style="color: #F3BA2F; font-size: 1.5em; font-weight: bold;">{wr_liv:.0f}%</div><div style="font-size: 0.7em; color: #F3BA2F;">livre</div></div></div></div>""", unsafe_allow_html=True)
with cc3: st.markdown(f"""<div class="mini-metric"><span class="mini-label">RETORNO MÉDIO</span><div style="display: flex; justify-content: space-around;"><div style="text-align: center;"><div style="color: #3b82f6; font-size: 1.5em; font-weight: bold;">${media_est:.2f}</div><div style="font-size: 0.7em; color: #3b82f6;">planejado</div></div><div style="border-left: 1px solid rgba(255,255,255,0.1);"></div><div style="text-align: center;"><div style="color: #F3BA2F; font-size: 1.5em; font-weight: bold;">${media_liv:.2f}</div><div style="font-size: 0.7em; color: #F3BA2F;">livre</div></div></div></div>""", unsafe_allow_html=True)

# ==============================================================================
# BLOCO 10: COFRE DOS ATIVOS (A SEÇÃO COMPLEXA)
# ==============================================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""<div style="width: 100%; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(243, 186, 47, 0.5), rgba(255,255,255,0.05)); margin-bottom: 30px;"></div>""", unsafe_allow_html=True)
st.subheader("🏦 Cofre dos Ativos", help="Análise de exposição (risco) e performance detalhada por ativo.")

dados_ativos = {}
# Processa dados para o cofre (Histórico + Aberto)
if historico_fechado:
    for o in historico_fechado:
        simb = o.get('simbolo', 'BTC')
        if simb not in dados_ativos: dados_ativos[simb] = {'investido_aberto': 0.0, 'qtd_aberta': 0.0, 'lucro_realizado': 0.0, 'wins': 0, 'trades': 0}
        dados_ativos[simb]['lucro_realizado'] += float(o.get('lucro_usdt', 0))
        dados_ativos[simb]['trades'] += 1
        if float(o.get('lucro_usdt', 0)) > 0: dados_ativos[simb]['wins'] += 1
if ordens_abertas:
    for o in ordens_abertas:
        simb = o.get('simbolo', 'BTC')
        if simb not in dados_ativos: dados_ativos[simb] = {'investido_aberto': 0.0, 'qtd_aberta': 0.0, 'lucro_realizado': 0.0, 'wins': 0, 'trades': 0}
        dados_ativos[simb]['investido_aberto'] += float(o.get('valor_investido_usdt', 0))
        dados_ativos[simb]['qtd_aberta'] += float(o.get('quantidade_btc', 0))

if not dados_ativos:
    st.info("Nenhuma operação registrada para análise de ativos.")
else:
    # --- PARTE A: O DONUT + DESTAQUES (Lado a Lado) ---
    col_grafico, col_destaques = st.columns([1.2, 2], gap="large")
    
    with col_grafico:
        total_investido_geral = sum(d['investido_aberto'] for d in dados_ativos.values())
        if total_investido_geral > 0:
            labels, values, colors = [], [], []
            for s, d in dados_ativos.items():
                if d['investido_aberto'] > 0:
                    labels.append(s)
                    values.append(d['investido_aberto'])
                    colors.append(ASSETS_CONFIG.get(s, {}).get("cor", "#888"))
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.6, marker=dict(colors=colors, line=dict(color='#0e1117', width=3)), textinfo='label+percent', textposition='outside', textfont=dict(size=14, color='white', weight='bold'), showlegend=False)])
            fig.update_layout(margin=dict(l=20, r=20, t=20, b=60), height=320, paper_bgcolor='rgba(0,0,0,0)', annotations=[dict(text=f"<span style='font-size:0.8em; color:gray'>Total em Risco</span><br><span style='font-size:1.4em; color:white; font-weight:bold'>${total_investido_geral:,.0f}</span>", x=0.5, y=0.5, font_size=12, showarrow=False)])
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Carteira 100% Líquida.")

    with col_destaques:
        melhor = max(dados_ativos.items(), key=lambda x: x[1]['lucro_realizado'], default=(None, None))
        pior = min(dados_ativos.items(), key=lambda x: x[1]['lucro_realizado'], default=(None, None))
        maior_risco = max(dados_ativos.items(), key=lambda x: x[1]['investido_aberto'], default=(None, None))
        
        st.markdown("##### 🏆 Destaques do Portfólio")
        st.markdown("<br>", unsafe_allow_html=True)
        
        c_d1, c_d2, c_d3 = st.columns(3)
        style_base = "background: linear-gradient(145deg, rgba(30, 41, 59, 0.5), rgba(15, 23, 42, 0.8)); border: 1px solid rgba(255, 255, 255, 0.05); padding: 10px; border-radius: 8px; text-align: center;"
        
        with c_d1:
            if melhor[0] and melhor[1]['lucro_realizado'] > 0:
                ic = ASSETS_CONFIG.get(melhor[0], {}).get("icon", "")
                st.markdown(f"""<div style="{style_base} border-top: 3px solid #22c55e;"><div style="font-size: 0.65em; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px;">Maior Lucro</div><div style="font-size: 1.1em; font-weight: bold; color: white;">{ic} {melhor[0]}</div><div style="color: #22c55e; font-weight: bold; font-size: 0.95em;">+${melhor[1]['lucro_realizado']:.2f}</div></div>""", unsafe_allow_html=True)
            else: st.markdown(f"<div style='{style_base} border-top: 3px solid gray; color: gray; font-size: 0.7em;'>Sem lucros</div>", unsafe_allow_html=True)
        
        with c_d2:
            if pior[0] and pior[1]['lucro_realizado'] < 0:
                ic = ASSETS_CONFIG.get(pior[0], {}).get("icon", "")
                st.markdown(f"""<div style="{style_base} border-top: 3px solid #ef4444;"><div style="font-size: 0.65em; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px;">Maior Prejuízo</div><div style="font-size: 1.1em; font-weight: bold; color: white;">{ic} {pior[0]}</div><div style="color: #ef4444; font-weight: bold; font-size: 0.95em;">-${abs(pior[1]['lucro_realizado']):.2f}</div></div>""", unsafe_allow_html=True)
            else: st.markdown(f"<div style='{style_base} border-top: 3px solid gray; color: gray; font-size: 0.7em;'>Sem perdas</div>", unsafe_allow_html=True)
            
        with c_d3:
            if maior_risco[0] and maior_risco[1]['investido_aberto'] > 0:
                ic = ASSETS_CONFIG.get(maior_risco[0], {}).get("icon", "")
                st.markdown(f"""<div style="{style_base} border-top: 3px solid #eab308;"><div style="font-size: 0.65em; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px;">Maior Exposição</div><div style="font-size: 1.1em; font-weight: bold; color: white;">{ic} {maior_risco[0]}</div><div style="color: #eab308; font-weight: bold; font-size: 0.95em;">${maior_risco[1]['investido_aberto']:.2f}</div></div>""", unsafe_allow_html=True)
            else: st.markdown(f"<div style='{style_base} border-top: 3px solid gray; color: gray; font-size: 0.7em;'>Líquido</div>", unsafe_allow_html=True)

    # --- PARTE B: LISTA DE CARDS WIDE ---
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### 📜 Detalhes por Ativo")
    
    ativos_ordenados = sorted(dados_ativos.keys())
    for simb in ativos_ordenados:
        stats = dados_ativos[simb]
        win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] > 0 else 0.0
        cor_lucro = "#22c55e" if stats['lucro_realizado'] >= 0 else "#ef4444"
        sinal_lucro = "+" if stats['lucro_realizado'] >= 0 else ""
        cor_wr = "#22c55e" if win_rate >= 50 else "#e2e8f0"
        icone = ASSETS_CONFIG.get(simb, {}).get("icon", "🪙")
        
        # HTML do Preço Médio (Se ativo)
        if stats['qtd_aberta'] > 0:
            preco_medio = stats['investido_aberto'] / stats['qtd_aberta']
            cotacao = cotacoes_atuais.get(simb, 0.0)
            cor_status = "#22c55e" if cotacao >= preco_medio else "#ef4444"
            diff_pct = ((cotacao - preco_medio) / preco_medio) * 100
            sinal_diff = "+" if diff_pct >= 0 else ""
            html_pm = f"""<div class="asset-stat-box" style="min-width: 140px;"><div class="asset-label">Status Posição</div><div style="font-size: 0.9em; color: gray;">PM: ${preco_medio:,.2f}</div><div style="font-size: 1.1em; font-weight: bold; color: {cor_status};">${cotacao:,.2f} ({sinal_diff}{diff_pct:.1f}%)</div></div><div class="vertical-divider"></div>"""
        else:
            html_pm = """<div class="asset-stat-box" style="min-width: 140px;"><div class="asset-label">Status</div><div style="font-size: 0.9em; color: gray; margin-top: 5px;">Posição Zerada</div></div><div class="vertical-divider"></div>"""

        # HTML DO CARD WIDE (SEM INDENTAÇÃO INTERNA PARA EVITAR BUGS)
        html_card = f"""
<div class="asset-row">
<div class="asset-identity">
<div class="asset-icon-large">{icone}</div>
<div class="asset-name-large">{simb}</div>
</div>
<div class="asset-stats-container">
{html_pm}
<div class="asset-stat-box">
<div class="asset-label">Lucro Realizado</div>
<div class="asset-value" style="color: {cor_lucro};">{sinal_lucro}${stats['lucro_realizado']:,.2f}</div>
</div>
<div class="vertical-divider"></div>
<div class="asset-stat-box">
<div class="asset-label">Taxa de Acerto</div>
<div class="asset-value" style="color: {cor_wr};">{win_rate:.0f}%</div>
</div>
<div class="vertical-divider"></div>
<div class="asset-stat-box">
<div class="asset-label">Total Trades</div>
<div class="asset-value" style="color: white;">{stats['trades']}</div>
</div>
</div>
</div>
"""
        st.markdown(html_card, unsafe_allow_html=True)

st.divider()
