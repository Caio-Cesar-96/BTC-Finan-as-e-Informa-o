import streamlit as st
import datetime
import requests
import pandas as pd

st.set_page_config(page_title="Portfólio - O Conselho", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

# --- CSS INSTITUCIONAL E CARDS COM "VIDA" ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
        
        /* Oculta os links nativos padrão se quisermos usar só nossos botões */
        [data-testid="stPageLink-NavLink"] {
            width: fit-content;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* ESTILO DOS CARDS DE PERFORMANCE (AGORA COM CORES E SOMBRAS) */
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
        
        /* BORDAS DE ACENTO PARA DAR VIDA */
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
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÃO DE API ---
def obter_preco_btc():
    try:
        url = "https://api.binance.us/api/v3/ticker/price?symbol=BTCUSDT"
        resposta = requests.get(url, timeout=3)
        return float(resposta.json()["price"])
    except:
        return 65000.0

# --- CABEÇALHO E NAVEGAÇÃO FLUIDA ---
col_titulo, col_botao = st.columns([8, 2], vertical_alignment="center")

with col_titulo:
    st.title("💼 Cockpit de Performance")
with col_botao:
    st.page_link("pages/1_Calculadora.py", label="Ir para Calculadora", icon="🧮")

st.divider()

# --- VERIFICAÇÃO DE MEMÓRIA ---
if 'ordens_abertas' not in st.session_state: st.session_state['ordens_abertas'] = []
if 'historico_fechado' not in st.session_state: st.session_state['historico_fechado'] = []

ordens_abertas = st.session_state['ordens_abertas']
historico_fechado = st.session_state['historico_fechado']

# --- CÁLCULOS DO MOTOR PYTHON ---
preco_btc_atual = obter_preco_btc()

# 1. Dados das Ordens Abertas (Exposição e Flutuante)
total_investido_aberto = sum(o['valor_investido_usdt'] for o in ordens_abertas)
total_btc_aberto = sum(o['quantidade_btc'] for o in ordens_abertas)
valor_mercado_atual = total_btc_aberto * preco_btc_atual
pnl_flutuante = valor_mercado_atual - total_investido_aberto

pnl_flutuante_pct = 0.0
if total_investido_aberto > 0:
    pnl_flutuante_pct = (pnl_flutuante / total_investido_aberto) * 100

cor_flutuante = "text-green" if pnl_flutuante >= 0 else "text-red"
sinal_flutuante = "+" if pnl_flutuante >= 0 else ""

# 2. Dados do Histórico Fechado (Realizado e Win Rate)
lucro_realizado_total = sum(o['lucro_usdt'] for o in historico_fechado)
total_taxas_pagas = sum(o.get('total_taxas_usdt', 0.0) for o in historico_fechado) + sum(o.get('taxa_entrada_usdt', 0.0) for o in ordens_abertas)

ordens_vencedoras = sum(1 for o in historico_fechado if o['lucro_usdt'] > 0)
total_ordens_fechadas = len(historico_fechado)
win_rate = (ordens_vencedoras / total_ordens_fechadas * 100) if total_ordens_fechadas > 0 else 0.0

cor_realizado = "text-green" if lucro_realizado_total >= 0 else "text-red"
sinal_realizado = "+" if lucro_realizado_total >= 0 else ""

cor_winrate = "text-green" if win_rate >= 50 else ("text-red" if total_ordens_fechadas > 0 else "text-gray")

# --- DESENHANDO OS CARDS EM HTML ---
st.subheader("Visão Geral do Portfólio")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card card-capital">
            <div class="metric-title">Capital Alocado (Risco)</div>
            <div class="metric-value">&#36;{total_investido_aberto:,.2f}</div>
            <div class="metric-sub text-gold">{total_btc_aberto:.8f} BTC em custódia</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card card-pnl">
            <div class="metric-title">PnL Flutuante (Abertas)</div>
            <div class="metric-value {cor_flutuante}">{sinal_flutuante}&#36;{abs(pnl_flutuante):,.2f}</div>
            <div class="metric-sub {cor_flutuante}">{sinal_flutuante}{pnl_flutuante_pct:.2f}% sobre o investido</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card card-realizado">
            <div class="metric-title">Lucro Líquido Realizado</div>
            <div class="metric-value {cor_realizado}">{sinal_realizado}&#36;{abs(lucro_realizado_total):,.2f}</div>
            <div class="metric-sub text-gray">De {total_ordens_fechadas} ordens fechadas</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card card-winrate">
            <div class="metric-title">Win Rate (Taxa de Acerto)</div>
            <div class="metric-value {cor_winrate}">{win_rate:.1f}%</div>
            <div class="metric-sub text-gray">Ordens Positivas: {ordens_vencedoras}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- DETALHAMENTO DE CUSTÓDIA ---
aba_abertas, aba_fechadas = st.tabs(["🟢 Ordens em aberto", "🎯 Ordens finalizadas"])

with aba_abertas:
    if not ordens_abertas:
        st.info("Sua carteira está vazia. Nenhuma ordem aberta no momento.")
    else:
        df_abertas = pd.DataFrame(ordens_abertas)
        df_abertas = df_abertas[['id', 'data_abertura_br', 'valor_investido_usdt', 'quantidade_btc', 'preco_compra']]
        df_abertas.columns = ['Ordem', 'Data da Compra', 'Investimento (USDT)', 'Volume (BTC)', 'Preço Pago (USDT)']
        
        estilo_abertas = df_abertas.style.format({
            'Investimento (USDT)': '${:,.2f}',
            'Volume (BTC)': '{:.8f}',
            'Preço Pago (USDT)': '${:,.2f}'
        })
        
        st.dataframe(estilo_abertas, use_container_width=True, hide_index=True)

with aba_fechadas:
    if not historico_fechado:
        st.info("Nenhuma ordem foi liquidada ainda.")
    else:
        df_fechadas = pd.DataFrame(historico_fechado)
        df_fechadas = df_fechadas[['id', 'data_fechamento_br', 'valor_investido_usdt', 'valor_recebido_usdt', 'lucro_usdt', 'lucro_pct']]
        df_fechadas.columns = ['Ordem', 'Data da Venda', 'Custo Original', 'Retorno Final', 'Lucro Líquido ($)', 'Rentabilidade (%)']
        
        def pintar_lucro(val):
            color = '#16a34a' if val > 0 else '#dc2626' if val < 0 else 'gray'
            return f'color: {color}; font-weight: bold'

        estilo_fechadas = df_fechadas.style.format({
            'Custo Original': '${:,.2f}',
            'Retorno Final': '${:,.2f}',
            'Lucro Líquido ($)': '${:,.2f}',
            'Rentabilidade (%)': '{:.2f}%'
        }).map(pintar_lucro, subset=['Lucro Líquido ($)', 'Rentabilidade (%)'])

        st.dataframe(estilo_fechadas, use_container_width=True, hide_index=True)

st.divider()
st.caption(f"Custo Operacional Acumulado (Taxas Totais de Plataforma): **${total_taxas_pagas:.4f}**")
