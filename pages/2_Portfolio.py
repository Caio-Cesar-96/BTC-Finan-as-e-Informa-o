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
        
        [data-testid="stPageLink-NavLink"] {
            width: fit-content;
            padding: 5px 15px;
            border-radius: 5px;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
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

total_investido_aberto = sum(o['valor_investido_usdt'] for o in ordens_abertas)
total_btc_aberto = sum(o['quantidade_btc'] for o in ordens_abertas)
valor_mercado_atual = total_btc_aberto * preco_btc_atual
pnl_flutuante = valor_mercado_atual - total_investido_aberto

pnl_flutuante_pct = 0.0
if total_investido_aberto > 0:
    pnl_flutuante_pct = (pnl_flutuante / total_investido_aberto) * 100

cor_flutuante = "text-green" if pnl_flutuante >= 0 else "text-red"
sinal_flutuante = "+" if pnl_flutuante >= 0 else "-"

lucro_realizado_total = sum(o['lucro_usdt'] for o in historico_fechado)
total_taxas_pagas = sum(o.get('total_taxas_usdt', 0.0) for o in historico_fechado) + sum(o.get('taxa_entrada_usdt', 0.0) for o in ordens_abertas)

ordens_vencedoras = sum(1 for o in historico_fechado if o['lucro_usdt'] > 0)
total_ordens_fechadas = len(historico_fechado)
win_rate = (ordens_vencedoras / total_ordens_fechadas * 100) if total_ordens_fechadas > 0 else 0.0

cor_realizado = "text-green" if lucro_realizado_total >= 0 else "text-red"
sinal_realizado = "+" if lucro_realizado_total >= 0 else "-"

cor_winrate = "text-green" if win_rate >= 50 else ("text-red" if total_ordens_fechadas > 0 else "text-gray")

# --- CÁLCULO DE TEMPO MÉDIO DE OPERAÇÃO ---
tempos_operacao = []
for o in historico_fechado:
    try:
        dt_abertura = datetime.datetime.strptime(f"{o['data_abertura']} {o['hora_abertura']}", "%Y-%m-%d %H:%M")
        dt_fechamento = datetime.datetime.strptime(f"{o['data_fechamento']} {o['hora_fechamento']}", "%Y-%m-%d %H:%M")
        tempos_operacao.append((dt_fechamento - dt_abertura).total_seconds())
    except:
        pass

tempo_medio_str = "0m"
if tempos_operacao:
    media_seg = sum(tempos_operacao) / len(tempos_operacao)
    horas = int(media_seg // 3600)
    minutos = int((media_seg % 3600) // 60)
    tempo_medio_str = f"{horas}h {minutos}m" if horas > 0 else f"{minutos}m"

# --- DESENHANDO OS CARDS ---
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
            <div class="metric-sub {cor_flutuante}">{sinal_flutuante}{abs(pnl_flutuante_pct):,.2f}% sobre o investido</div>
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

# --- LAYOUT DIVIDIDO NO MEIO (50/50) ---
col_tabelas, col_lateral = st.columns([1.1, 0.9], gap="large")

with col_tabelas:
    st.subheader("📋 Relatórios de Custódia")
    aba_abertas, aba_fechadas = st.tabs(["🟢 Ordens em aberto", "🎯 Ordens finalizadas"])

    def pintar_tabela(val):
        if isinstance(val, (int, float)):
            if val > 0:
                return 'color: #16a34a; font-weight: bold;'
            elif val < 0:
                return 'color: #dc2626; font-weight: bold;'
        return 'color: gray;'

    with aba_abertas:
        if not ordens_abertas:
            st.info("Sua carteira está vazia. Nenhuma ordem aberta no momento.")
        else:
            dados_abertas = []
            for o in ordens_abertas:
                valor_atual_ordem = o['quantidade_btc'] * preco_btc_atual
                pnl_dolar = valor_atual_ordem - o['valor_investido_usdt']
                pnl_pct = (pnl_dolar / o['valor_investido_usdt']) * 100
                
                dados_abertas.append({
                    'Ordem': f"#{o['id']}",
                    'Investido': o['valor_investido_usdt'],
                    'Volume (BTC)': o['quantidade_btc'],
                    'Preço Pago': o['preco_compra'],
                    'PnL Atual ($)': pnl_dolar,
                    'Rentabilidade (%)': pnl_pct,
                    'Data Compra': f"{o['data_abertura_br']} {o['hora_abertura']}"
                })
                
            df_abertas = pd.DataFrame(dados_abertas)
            
            estilo_abertas = df_abertas.style.map(pintar_tabela, subset=['PnL Atual ($)', 'Rentabilidade (%)']).format({
                'Investido': '${:,.2f}',
                'Volume (BTC)': '{:.8f}',
                'Preço Pago': '${:,.2f}',
                'PnL Atual ($)': '${:,.2f}',
                'Rentabilidade (%)': '{:+.2f}%'
            })
            
            st.dataframe(estilo_abertas, use_container_width=True, hide_index=True)

    with aba_fechadas:
        if not historico_fechado:
            st.info("Nenhuma ordem foi liquidada ainda.")
        else:
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
                })
                
            df_fechadas = pd.DataFrame(dados_fechadas)
            
            estilo_fechadas = df_fechadas.style.map(pintar_tabela, subset=['Lucro Líquido ($)', 'Rentabilidade (%)']).format({
                'Investido': '${:,.2f}',
                'Retorno Final': '${:,.2f}',
                'Lucro Líquido ($)': '${:,.2f}',
                'Rentabilidade (%)': '{:+.2f}%',
                'Taxas Totais ($)': '${:,.4f}'
            })

            st.dataframe(estilo_fechadas, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(255, 255, 255, 0.05); padding: 8px 15px; border-radius: 6px; display: inline-block; font-size: 0.85em;">
            <span style="color: #9ca3af;">Custo Operacional Acumulado:</span> 
            <strong style="color: #e2e8f0; margin-left: 5px;">&#36;{total_taxas_pagas:.4f}</strong>
        </div>
    """, unsafe_allow_html=True)

with col_lateral:
    st.subheader("📊 Raio-X de Performance")
    
    # 1. BARRA DE FORÇA (WIN/LOSS)
    loss_rate = 100.0 - win_rate if total_ordens_fechadas > 0 else 0.0
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 25px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-family: sans-serif;">
                <span style="color: #22c55e; font-weight: 600; font-size: 0.95em; text-shadow: 0 0 5px rgba(34,197,94,0.3);">🟢 Vitórias {win_rate:.0f}%</span>
                <span style="color: #ef4444; font-weight: 600; font-size: 0.95em; text-shadow: 0 0 5px rgba(239,68,68,0.3);">Derrotas {loss_rate:.0f}% 🔴</span>
            </div>
            <div style="width: 100%; height: 12px; background-color: rgba(239,68,68,0.2); border-radius: 6px; overflow: hidden; display: flex; box-shadow: inset 0 1px 3px rgba(0,0,0,0.5);">
                <div style="width: {win_rate}%; background: linear-gradient(90deg, #16a34a, #22c55e); height: 100%; box-shadow: 0 0 10px rgba(34,197,94,0.4);"></div>
                <div style="width: {loss_rate}%; background: linear-gradient(90deg, #dc2626, #ef4444); height: 100%; box-shadow: 0 0 10px rgba(239,68,68,0.4);"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # 2. GRÁFICO DE LINHA (CURVA DE CAPITAL POR OPERAÇÃO - AJUSTADO)
    st.markdown("<div style='font-size: 0.9em; color: #9ca3af; margin-bottom: 10px;'>Curva de Capital</div>", unsafe_allow_html=True)
    if not historico_fechado:
        st.info("O gráfico aparecerá após sua primeira venda.")
    else:
        df_hist = pd.DataFrame(historico_fechado)
        df_hist['Datahora'] = pd.to_datetime(df_hist['data_fechamento'] + ' ' + df_hist['hora_fechamento'])
        df_hist = df_hist.sort_values('Datahora').reset_index(drop=True)
        
        eixo_x = []
        eixo_y = []
        
        lucro_acumulado = 0.0
        for i, row in df_hist.iterrows():
            lucro_acumulado += row['lucro_usdt']
            eixo_x.append(i + 1) # Usar números garante a identificação do eixo e leitura deitada
            eixo_y.append(lucro_acumulado)
            
        df_chart_final = pd.DataFrame({
            'Nº da Operação': eixo_x,
            'Lucro Acumulado (USDT)': eixo_y
        })
        
        cor_grafico = "#16a34a" if eixo_y[-1] >= 0 else "#dc2626"
        
        # Inserido X e Y para nomear os eixos, e height=300 para dar espaço
        st.line_chart(df_chart_final, x='Nº da Operação', y='Lucro Acumulado (USDT)', color=cor_grafico, height=300)

    # 3. TEMPO MÉDIO DE OPERAÇÃO (DISCRETO E COMPACTO)
    st.markdown(f"""
        <div style="background-color: rgba(59, 130, 246, 0.05); border: 1px solid rgba(255, 255, 255, 0.05); padding: 8px 15px; border-radius: 6px; display: inline-block; font-size: 0.85em; margin-top: 10px;">
            <span style="color: #9ca3af;">⏱️ Tempo Médio em Operação:</span> 
            <strong style="color: #e2e8f0; margin-left: 5px;">{tempo_medio_str}</strong>
        </div>
    """, unsafe_allow_html=True)

st.divider()
