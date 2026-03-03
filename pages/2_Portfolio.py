import streamlit as st
import datetime
import requests
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client, Client

st.set_page_config(page_title="Portfólio - O Conselho", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

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

# --- CSS INSTITUCIONAL E CARDS COM "VIDA" ---
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

# --- CABEÇALHO E NAVEGAÇÃO ---
col_titulo, col_btn_home, col_btn_calc = st.columns([6, 2, 2], vertical_alignment="center")

with col_titulo:
    st.title("💼 Cockpit de Performance")
with col_btn_home:
    st.page_link("pages/0_Terminal.py", label="Voltar ao Terminal", icon="🏠")
with col_btn_calc:
    st.page_link("pages/1_Calculadora.py", label="Ir para Calculadora", icon="🧮")

st.divider()

# --- VERIFICAÇÃO DE MEMÓRIA BLINDADA ---
if 'dados_sincronizados' not in st.session_state:
    with st.spinner("Sincronizando Portfólio com o Banco de Dados..."):
        abertas, fechadas = carregar_dados_nuvem()
        st.session_state['ordens_abertas'] = abertas
        st.session_state['historico_fechado'] = fechadas
        st.session_state['dados_sincronizados'] = True

# Recarregando via botão oculto
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

total_investido_aberto = sum(float(o['valor_investido_usdt']) for o in ordens_abertas)
total_btc_aberto = sum(float(o['quantidade_btc']) for o in ordens_abertas)
valor_mercado_atual = total_btc_aberto * preco_btc_atual
pnl_flutuante = valor_mercado_atual - total_investido_aberto

pnl_flutuante_pct = 0.0
if total_investido_aberto > 0:
    pnl_flutuante_pct = (pnl_flutuante / total_investido_aberto) * 100

cor_flutuante = "text-green" if pnl_flutuante >= 0 else "text-red"
sinal_flutuante = "+" if pnl_flutuante >= 0 else "-"

lucro_realizado_total = sum(float(o.get('lucro_usdt', 0)) for o in historico_fechado)
total_taxas_pagas = sum(float(o.get('total_taxas_usdt', 0)) for o in historico_fechado) + sum(float(o.get('taxa_entrada_usdt', 0)) for o in ordens_abertas)

ordens_vencedoras = sum(1 for o in historico_fechado if float(o.get('lucro_usdt', 0)) > 0)
total_ordens_fechadas = len(historico_fechado)
win_rate = (ordens_vencedoras / total_ordens_fechadas * 100) if total_ordens_fechadas > 0 else 0.0

cor_realizado = "text-green" if lucro_realizado_total >= 0 else "text-red"
sinal_realizado = "+" if lucro_realizado_total >= 0 else "-"

cor_winrate = "text-green" if win_rate >= 50 else ("text-red" if total_ordens_fechadas > 0 else "text-gray")

# --- CÁLCULOS AVANÇADOS ---
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
        elif l_usdt == 0:
            continue
        else:
            break

# --- TEMPO MÉDIO ---
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

# --- DESENHO DOS CARDS SUPERIORES ---
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
                valor_atual_ordem = float(o['quantidade_btc']) * preco_btc_atual
                pnl_dolar = valor_atual_ordem - float(o['valor_investido_usdt'])
                pnl_pct = (pnl_dolar / float(o['valor_investido_usdt'])) * 100
                
                dados_abertas.append({
                    'Ordem': f"#{o.get('display_id', '???')}",
                    'Investido': float(o['valor_investido_usdt']),
                    'Volume (BTC)': float(o['quantidade_btc']),
                    'Preço Pago': float(o['preco_compra']),
                    'PnL Atual ($)': pnl_dolar,
                    'Rentabilidade (%)': pnl_pct,
                    'Data Compra': f"{o.get('data_abertura_br', '')} {o.get('hora_abertura', '')}"
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
                comportamento = o.get('comportamento_final')
                if not comportamento:
                    comportamento = "---"
                    
                dados_fechadas.append({
                    'Ordem': f"#{o.get('display_id', '???')}",
                    'Investido': float(o.get('valor_investido_usdt', 0)),
                    'Retorno Final': float(o.get('valor_recebido_usdt', 0)),
                    'Lucro Líquido ($)': float(o.get('lucro_usdt', 0)),
                    'Rentabilidade (%)': float(o.get('lucro_pct', 0)),
                    'Disciplina': comportamento,
                    'Entrada': f"{o.get('data_abertura_br', '')}",
                    'Saída': f"{o.get('data_fechamento_br', '')}"
                })
                
            df_fechadas = pd.DataFrame(dados_fechadas)
            
            estilo_fechadas = df_fechadas.style.map(pintar_tabela, subset=['Lucro Líquido ($)', 'Rentabilidade (%)']).format({
                'Investido': '${:,.2f}',
                'Retorno Final': '${:,.2f}',
                'Lucro Líquido ($)': '${:,.2f}',
                'Rentabilidade (%)': '{:+.2f}%'
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
    
    loss_rate = 100.0 - win_rate if total_ordens_fechadas > 0 else 0.0
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;">
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

    col_payoff, col_streak, col_tempo = st.columns(3)
    
    with col_payoff:
        st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 12px 5px; border-radius: 6px; text-align: center; margin-bottom: 20px; height: 100%;">
                <div style="color: #9ca3af; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Média (L/P)</div>
                <div style="font-size: 1.1em; font-weight: bold;">
                    <span style="color: #22c55e;">+${media_gain:.2f}</span>
                    <span style="color: rgba(255,255,255,0.2); margin: 0 2px;">|</span>
                    <span style="color: #ef4444;">-${abs(media_loss):.2f}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_streak:
        cor_streak = "#22c55e" if streak_tipo == "Lucro" else "#ef4444" if streak_tipo == "Prejuízo" else "gray"
        st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 12px 5px; border-radius: 6px; text-align: center; margin-bottom: 20px; height: 100%;">
                <div style="color: #9ca3af; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Sequência</div>
                <div style="font-size: 1.2em; font-weight: bold; color: {cor_streak};">
                    {icone_streak} {streak_count} {streak_tipo}s
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col_tempo:
        st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 12px 5px; border-radius: 6px; text-align: center; margin-bottom: 20px; height: 100%;">
                <div style="color: #9ca3af; font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px;">Tempo Médio</div>
                <div style="font-size: 1.2em; font-weight: bold; color: white;">
                    ⏱️ {tempo_medio_str}
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.9em; color: #9ca3af; margin-bottom: 10px;'>Curva de Capital (Acumulado)</div>", unsafe_allow_html=True)
    if not historico_fechado:
        st.info("O gráfico aparecerá após sua primeira venda.")
    else:
        df_hist = pd.DataFrame(historico_fechado)
        df_hist['Datahora'] = pd.to_datetime(df_hist['data_fechamento'] + ' ' + df_hist['hora_fechamento'])
        df_hist = df_hist.sort_values('Datahora').reset_index(drop=True)
        
        eixo_x = []
        eixo_y = []
        labels_x = []
        
        lucro_acumulado = 0.0
        for i, row in df_hist.iterrows():
            lucro_acumulado += float(row.get('lucro_usdt', 0))
            eixo_x.append(i + 1)
            eixo_y.append(lucro_acumulado)
            labels_x.append(f"#{row.get('display_id', '???')}")
            
        cor_grafico = "#22c55e" if eixo_y[-1] >= 0 else "#ef4444"
        cor_fundo = "rgba(34, 197, 94, 0.1)" if eixo_y[-1] >= 0 else "rgba(239, 68, 68, 0.1)"
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=eixo_x,
            y=eixo_y,
            mode='lines+markers',
            name='Lucro Acum.',
            line=dict(color=cor_grafico, width=3, shape='spline'),
            marker=dict(size=8, color=cor_grafico, line=dict(color='white', width=1)),
            fill='tozeroy',
            fillcolor=cor_fundo,
            customdata=labels_x,
            hovertemplate="<b>Ordem %{customdata}</b><br>Acumulado: $%{y:.2f}<extra></extra>"
        ))
        
        fig.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title=dict(text="Sequência de Fechamento", font=dict(size=12, color="#9ca3af")),
                showgrid=False,
                zeroline=False,
                tickmode='linear',
                tick0=1,
                dtick=1,
                color="#9ca3af",
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                title=dict(text="Lucro Acumulado ($)", font=dict(size=12, color="#9ca3af")),
                showgrid=True,
                gridcolor="rgba(255,255,255,0.05)",
                zeroline=True,
                zerolinecolor="rgba(255,255,255,0.2)",
                zerolinewidth=1.5,
                color="#9ca3af",
                tickprefix="$",
                tickfont=dict(size=11)
            ),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="rgba(30, 41, 59, 0.95)",
                font_size=12,
                font_family="sans-serif"
            )
        )
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# =========================================================
# SEÇÃO FINAL: DNA OPERACIONAL & LABORATÓRIO
# =========================================================

# ESTILO ATUALIZADO (Cards compactos e elegantes)
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# SEPARADOR VISUAL DOURADO
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="width: 100%; height: 2px; background: linear-gradient(90deg, rgba(255,255,255,0.05), rgba(243, 186, 47, 0.5), rgba(255,255,255,0.05)); margin-bottom: 30px;"></div>
""", unsafe_allow_html=True)

st.subheader("🧬 DNA Operacional", help="Painel comportamental que analisa sua disciplina com base em metas predefinidas de Alvo e Stop.")

if not historico_fechado:
    st.info("O perfil comportamental será gerado após o fechamento das primeiras operações com projeção (Alvo/Stop).")
else:
    # --- PARTE 1: O GRÁFICO DE ROSCA E BARRAS ---
    contagem_comportamento = {
        "🏆 Sniper": 0,
        "🥬 Mão de Alface": 0,
        "🛡️ Saída Estratégica": 0,
        "🛑 Resiliência": 0,
        "💥 Descontrole": 0
    }
    
    total_validos = 0
    for o in historico_fechado:
        comp = o.get('comportamento_final')
        if comp and comp in contagem_comportamento:
            contagem_comportamento[comp] += 1
            total_validos += 1
            
    dados_grafico = {k: v for k, v in contagem_comportamento.items() if v > 0}
    
    col_dna_grafico, col_dna_barras = st.columns([1, 2], gap="large")
    
    cores_map = {
        "🏆 Sniper": "#10b981",       # Emerald
        "🥬 Mão de Alface": "#F3BA2F",# Dourado
        "🛡️ Saída Estratégica": "#64748b", # Slate
        "🛑 Resiliência": "#f97316",  # Laranja
        "💥 Descontrole": "#ef4444",  # Vermelho
    }
    
    if total_validos > 0:
        with col_dna_grafico:
            labels = list(dados_grafico.keys())
            values = list(dados_grafico.values())
            colors = [cores_map.get(l, "gray") for l in labels]
            
            fig_dna = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=.6,
                marker=dict(colors=colors, line=dict(color='#0f172a', width=3)),
                textinfo='percent',
                textposition='outside',
                textfont=dict(size=14, color='white', family="sans-serif"),
                hoverinfo='label+value'
            )])
            
            fig_dna.update_layout(
                showlegend=False,
                margin=dict(l=10, r=10, t=10, b=50),
                height=250,
                paper_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text=f"{total_validos}", x=0.5, y=0.5, font_size=20, showarrow=False, font_color="white")]
            )
            st.plotly_chart(fig_dna, use_container_width=True)
            st.markdown(f"<div style='text-align: center; color: gray; font-size: 0.8em; margin-top: -10px;'>Operações Qualificadas</div>", unsafe_allow_html=True)

        with col_dna_barras:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            for item, qtd in dados_grafico.items():
                pct = (qtd / total_validos) * 100
                cor = cores_map.get(item, "gray")
                st.markdown(f"""
                    <div style="margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="color: #e2e8f0; font-size: 0.9em; font-weight: 500;">{item}</span>
                        </div>
                        <div style="width: 100%; background-color: rgba(255,255,255,0.05); height: 8px; border-radius: 4px;">
                            <div style="width: {pct}%; background-color: {cor}; height: 100%; border-radius: 4px; box-shadow: 0 0 8px {cor}40;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aguardando dados de operações com alvo e stop para gerar o DNA.")

    # --- PARTE 2: COMPARAÇÃO COMPORTAMENTAL ---
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""<div style="border-top: 1px dashed rgba(255,255,255,0.1); margin: 20px 0;"></div>""", unsafe_allow_html=True)
    st.subheader("⚖️ Comparação Comportamental")
    
    # [AJUSTE 3] TEXTO SIMPLIFICADO
    st.caption("Comparativo de performance entre operações planejadas e operações livres.")
    
    # CÁLCULOS
    ops_estruturadas = [o for o in historico_fechado if o.get('teve_projecao')]
    ops_livres = [o for o in historico_fechado if not o.get('teve_projecao')]
    
    lucro_est = sum(o['lucro_usdt'] for o in ops_estruturadas)
    wins_est = sum(1 for o in ops_estruturadas if o['lucro_usdt'] > 0)
    total_est = len(ops_estruturadas)
    wr_est = (wins_est / total_est * 100) if total_est > 0 else 0.0
    media_est = (lucro_est / total_est) if total_est > 0 else 0.0
    
    lucro_liv = sum(o['lucro_usdt'] for o in ops_livres)
    wins_liv = sum(1 for o in ops_livres if o['lucro_usdt'] > 0)
    total_liv = len(ops_livres)
    wr_liv = (wins_liv / total_liv * 100) if total_liv > 0 else 0.0
    media_liv = (lucro_liv / total_liv) if total_liv > 0 else 0.0
    
    cor_azul = "#3b82f6"
    cor_amarela = "#F3BA2F"
    
    col_c1, col_c2, col_c3 = st.columns(3)
    
    # CARD 1: LUCRO
    with col_c1:
        st.markdown(f"""
            <div class="mini-metric">
                <span class="mini-label">LUCRO LÍQUIDO</span>
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="text-align: center;">
                        <div style="color: {cor_azul}; font-size: 1.8em; font-weight: bold; line-height: 1;">${lucro_est:.2f}</div>
                        <div style="font-size: 0.75em; color: {cor_azul}; opacity: 0.7; font-weight: 500; margin-top: 4px;">planejado</div>
                    </div>
                    <div style="border-left: 1px solid rgba(255,255,255,0.1); height: 30px;"></div>
                    <div style="text-align: center;">
                        <div style="color: {cor_amarela}; font-size: 1.8em; font-weight: bold; line-height: 1;">${lucro_liv:.2f}</div>
                        <div style="font-size: 0.75em; color: {cor_amarela}; opacity: 0.7; font-weight: 500; margin-top: 4px;">livre</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # CARD 2: WIN RATE
    with col_c2:
        st.markdown(f"""
            <div class="mini-metric">
                <span class="mini-label">WIN RATE</span>
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="text-align: center;">
                        <div style="color: {cor_azul}; font-size: 1.8em; font-weight: bold; line-height: 1;">{wr_est:.0f}%</div>
                        <div style="font-size: 0.75em; color: {cor_azul}; opacity: 0.7; font-weight: 500; margin-top: 4px;">planejado</div>
                    </div>
                    <div style="border-left: 1px solid rgba(255,255,255,0.1); height: 30px;"></div>
                    <div style="text-align: center;">
                        <div style="color: {cor_amarela}; font-size: 1.8em; font-weight: bold; line-height: 1;">{wr_liv:.0f}%</div>
                        <div style="font-size: 0.75em; color: {cor_amarela}; opacity: 0.7; font-weight: 500; margin-top: 4px;">livre</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    # CARD 3: PAYOFF
    with col_c3:
        st.markdown(f"""
            <div class="mini-metric">
                <span class="mini-label">PAYOFF MÉDIO</span>
                <div style="display: flex; justify-content: space-around; align-items: center;">
                    <div style="text-align: center;">
                        <div style="color: {cor_azul}; font-size: 1.8em; font-weight: bold; line-height: 1;">${media_est:.2f}</div>
                        <div style="font-size: 0.75em; color: {cor_azul}; opacity: 0.7; font-weight: 500; margin-top: 4px;">planejado</div>
                    </div>
                    <div style="border-left: 1px solid rgba(255,255,255,0.1); height: 30px;"></div>
                    <div style="text-align: center;">
                        <div style="color: {cor_amarela}; font-size: 1.8em; font-weight: bold; line-height: 1;">${media_liv:.2f}</div>
                        <div style="font-size: 0.75em; color: {cor_amarela}; opacity: 0.7; font-weight: 500; margin-top: 4px;">livre</div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # GRÁFICO COMPARATIVO DE LINHAS
    st.markdown("<br>", unsafe_allow_html=True)
    
    df_comp = pd.DataFrame(historico_fechado)
    if not df_comp.empty:
        df_comp['Datahora'] = pd.to_datetime(df_comp['data_fechamento'] + ' ' + df_comp['hora_fechamento'])
        df_comp = df_comp.sort_values('Datahora')
        
        x_axis = []
        y_est = []
        y_liv = []
        
        acum_est = 0.0
        acum_liv = 0.0
        
        count = 1
        for _, row in df_comp.iterrows():
            lucro = float(row['lucro_usdt'])
            if row.get('teve_projecao'):
                acum_est += lucro
            else:
                acum_liv += lucro
            
            x_axis.append(count)
            y_est.append(acum_est)
            y_liv.append(acum_liv)
            count += 1
            
        fig_comp = go.Figure()
        
        # Linha Planejada
        fig_comp.add_trace(go.Scatter(
            x=x_axis, y=y_est, mode='lines', name='Com Planejamento',
            line=dict(color=cor_azul, width=2),
            hovertemplate="Planejado: $%{y:.2f}<extra></extra>"
        ))
        
        # Linha Livre - [AJUSTE 2] LINHA SÓLIDA AGORA (Sem dash)
        fig_comp.add_trace(go.Scatter(
            x=x_axis, y=y_liv, mode='lines', name='Sem Planejamento',
            line=dict(color=cor_amarela, width=2), 
            hovertemplate="Livre: $%{y:.2f}<extra></extra>"
        ))
        
        fig_comp.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white", size=10)),
            # [AJUSTE 1] TÍTULO DO EIXO X LIMPO
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title="Quantidade de Trades Executados"),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=True, zerolinecolor='rgba(255,255,255,0.1)', tickfont=dict(color="gray")),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig_comp, use_container_width=True, config={'displayModeBar': False})

st.divider()
