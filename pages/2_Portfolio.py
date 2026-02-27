import requests
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

st.set_page_config(page_title="Portfólio - O Conselho", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

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

# --- CSS INSTITUCIONAL E CARDS COM "VIDA" ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        [data-testid="stPageLink-NavLink"] {
            width: fit-content;
            padding: 5px 15px;
@@ -65,7 +76,7 @@
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE API ---
# --- FUNÇÕES DE API E SINCRONIZAÇÃO COM MÁSCARA ---
def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
@@ -74,6 +85,22 @@ def obter_preco_btc():
    except:
        return 65000.0

def carregar_dados_nuvem():
    try:
        resposta = supabase.table("operacoes").select("*").execute()
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

col_titulo, col_botao = st.columns([8, 2], vertical_alignment="center")

with col_titulo:
@@ -83,18 +110,31 @@ def obter_preco_btc():

st.divider()

# --- VERIFICAÇÃO DE MEMÓRIA ---
if 'ordens_abertas' not in st.session_state: st.session_state['ordens_abertas'] = []
if 'historico_fechado' not in st.session_state: st.session_state['historico_fechado'] = []

ordens_abertas = st.session_state['ordens_abertas']
historico_fechado = st.session_state['historico_fechado']
# --- VERIFICAÇÃO DE MEMÓRIA BLINDADA ---
if 'dados_sincronizados' not in st.session_state:
    with st.spinner("Sincronizando Portfólio com o Banco de Dados..."):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.session_state['dados_sincronizados'] = True

# Recarregando via botão oculto para forçar atualização se a página ficar aberta por horas
col_refresh, col_vazia = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 Atualizar Dados"):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.rerun()

ordens_abertas = st.session_state.get('ordens_abertas', [])
historico_fechado = st.session_state.get('historico_fechado', [])

# --- CÁLCULOS DO MOTOR PYTHON ---
preco_btc_atual = obter_preco_btc()

total_investido_aberto = sum(o['valor_investido_usdt'] for o in ordens_abertas)
total_btc_aberto = sum(o['quantidade_btc'] for o in ordens_abertas)
total_investido_aberto = sum(float(o['valor_investido_usdt']) for o in ordens_abertas)
total_btc_aberto = sum(float(o['quantidade_btc']) for o in ordens_abertas)
valor_mercado_atual = total_btc_aberto * preco_btc_atual
pnl_flutuante = valor_mercado_atual - total_investido_aberto

@@ -105,10 +145,10 @@ def obter_preco_btc():
cor_flutuante = "text-green" if pnl_flutuante >= 0 else "text-red"
sinal_flutuante = "+" if pnl_flutuante >= 0 else "-"

lucro_realizado_total = sum(o['lucro_usdt'] for o in historico_fechado)
total_taxas_pagas = sum(o.get('total_taxas_usdt', 0.0) for o in historico_fechado) + sum(o.get('taxa_entrada_usdt', 0.0) for o in ordens_abertas)
lucro_realizado_total = sum(float(o.get('lucro_usdt', 0)) for o in historico_fechado)
total_taxas_pagas = sum(float(o.get('total_taxas_usdt', 0)) for o in historico_fechado) + sum(float(o.get('taxa_entrada_usdt', 0)) for o in ordens_abertas)

ordens_vencedoras = sum(1 for o in historico_fechado if o['lucro_usdt'] > 0)
ordens_vencedoras = sum(1 for o in historico_fechado if float(o.get('lucro_usdt', 0)) > 0)
total_ordens_fechadas = len(historico_fechado)
win_rate = (ordens_vencedoras / total_ordens_fechadas * 100) if total_ordens_fechadas > 0 else 0.0

@@ -125,25 +165,24 @@ def obter_preco_btc():
icone_streak = "➖"

if historico_fechado:
    # 1. Payoff (Médias)
    gains = [o['lucro_usdt'] for o in historico_fechado if o['lucro_usdt'] > 0]
    losses = [o['lucro_usdt'] for o in historico_fechado if o['lucro_usdt'] < 0]
    gains = [float(o['lucro_usdt']) for o in historico_fechado if float(o.get('lucro_usdt', 0)) > 0]
    losses = [float(o['lucro_usdt']) for o in historico_fechado if float(o.get('lucro_usdt', 0)) < 0]

    if gains: media_gain = sum(gains) / len(gains)
    if losses: media_loss = sum(losses) / len(losses)

    # 2. Sequência Atual (Streak)
    historico_cronologico = sorted(historico_fechado, key=lambda x: f"{x['data_fechamento']} {x['hora_fechamento']}")
    ordens_reversas = list(reversed(historico_cronologico))

    ultimo_resultado_positivo = ordens_reversas[0]['lucro_usdt'] > 0
    ultimo_resultado_positivo = float(ordens_reversas[0].get('lucro_usdt', 0)) > 0
    streak_tipo = "Lucro" if ultimo_resultado_positivo else "Prejuízo"
    icone_streak = "🔥" if ultimo_resultado_positivo else "🧊"

    for o in ordens_reversas:
        if (o['lucro_usdt'] > 0 and ultimo_resultado_positivo) or (o['lucro_usdt'] < 0 and not ultimo_resultado_positivo):
        l_usdt = float(o.get('lucro_usdt', 0))
        if (l_usdt > 0 and ultimo_resultado_positivo) or (l_usdt < 0 and not ultimo_resultado_positivo):
            streak_count += 1
        elif o['lucro_usdt'] == 0:
        elif l_usdt == 0:
            continue
        else:
            break
@@ -229,18 +268,18 @@ def pintar_tabela(val):
        else:
            dados_abertas = []
            for o in ordens_abertas:
                valor_atual_ordem = o['quantidade_btc'] * preco_btc_atual
                pnl_dolar = valor_atual_ordem - o['valor_investido_usdt']
                pnl_pct = (pnl_dolar / o['valor_investido_usdt']) * 100
                valor_atual_ordem = float(o['quantidade_btc']) * preco_btc_atual
                pnl_dolar = valor_atual_ordem - float(o['valor_investido_usdt'])
                pnl_pct = (pnl_dolar / float(o['valor_investido_usdt'])) * 100

                dados_abertas.append({
                    'Ordem': f"#{o['id']}",
                    'Investido': o['valor_investido_usdt'],
                    'Volume (BTC)': o['quantidade_btc'],
                    'Preço Pago': o['preco_compra'],
                    'Ordem': f"#{o.get('display_id', '???')}",
                    'Investido': float(o['valor_investido_usdt']),
                    'Volume (BTC)': float(o['quantidade_btc']),
                    'Preço Pago': float(o['preco_compra']),
                    'PnL Atual ($)': pnl_dolar,
                    'Rentabilidade (%)': pnl_pct,
                    'Data Compra': f"{o['data_abertura_br']} {o['hora_abertura']}"
                    'Data Compra': f"{o.get('data_abertura_br', '')} {o.get('hora_abertura', '')}"
                })

            df_abertas = pd.DataFrame(dados_abertas)
@@ -262,14 +301,14 @@ def pintar_tabela(val):
            dados_fechadas = []
            for o in historico_fechado:
                dados_fechadas.append({
                    'Ordem': f"#{o['id']}",
                    'Investido': o['valor_investido_usdt'],
                    'Retorno Final': o['valor_recebido_usdt'],
                    'Lucro Líquido ($)': o['lucro_usdt'],
                    'Rentabilidade (%)': o['lucro_pct'],
                    'Taxas Totais ($)': o['total_taxas_usdt'],
                    'Entrada': f"{o['data_abertura_br']}",
                    'Saída': f"{o['data_fechamento_br']}"
                    'Ordem': f"#{o.get('display_id', '???')}",
                    'Investido': float(o.get('valor_investido_usdt', 0)),
                    'Retorno Final': float(o.get('valor_recebido_usdt', 0)),
                    'Lucro Líquido ($)': float(o.get('lucro_usdt', 0)),
                    'Rentabilidade (%)': float(o.get('lucro_pct', 0)),
                    'Taxas Totais ($)': float(o.get('total_taxas_usdt', 0)),
                    'Entrada': f"{o.get('data_abertura_br', '')}",
                    'Saída': f"{o.get('data_fechamento_br', '')}"
                })

            df_fechadas = pd.DataFrame(dados_fechadas)
@@ -311,7 +350,7 @@ def pintar_tabela(val):
        </div>
    """, unsafe_allow_html=True)

    # 2. A TRINDADE: PAYOFF, STREAK E TEMPO MÉDIO
    # 2. A TRINDADE
    col_payoff, col_streak, col_tempo = st.columns(3)

    with col_payoff:
@@ -358,12 +397,14 @@ def pintar_tabela(val):

        eixo_x = []
        eixo_y = []
        labels_x = []

        lucro_acumulado = 0.0
        for i, row in df_hist.iterrows():
            lucro_acumulado += row['lucro_usdt']
            lucro_acumulado += float(row.get('lucro_usdt', 0))
            eixo_x.append(i + 1)
            eixo_y.append(lucro_acumulado)
            labels_x.append(f"#{row.get('display_id', '???')}")

        cor_grafico = "#22c55e" if eixo_y[-1] >= 0 else "#ef4444"
        cor_fundo = "rgba(34, 197, 94, 0.1)" if eixo_y[-1] >= 0 else "rgba(239, 68, 68, 0.1)"
@@ -379,7 +420,8 @@ def pintar_tabela(val):
            marker=dict(size=8, color=cor_grafico, line=dict(color='white', width=1)),
            fill='tozeroy',
            fillcolor=cor_fundo,
            hovertemplate="<b>Operação #%{x}</b><br>Acumulado: $%{y:.2f}<extra></extra>"
            customdata=labels_x,
            hovertemplate="<b>Ordem %{customdata}</b><br>Acumulado: $%{y:.2f}<extra></extra>"
        ))

        fig.update_layout(
@@ -388,7 +430,7 @@ def pintar_tabela(val):
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text="Nº da Operação", font=dict(size=12, color="#9ca3af")),
                title=dict(text="Sequência de Fechamento", font=dict(size=12, color="#9ca3af")),
                showgrid=False,
                zeroline=False,
                tickmode='linear',
