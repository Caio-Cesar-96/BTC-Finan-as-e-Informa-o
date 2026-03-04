import streamlit as st

st.set_page_config(layout="wide", page_title="Laboratório de Design", page_icon="🧪")

# ==============================================================================
# 1. BANCO DE IMAGENS (DATA URIs - Leves e Vetoriais)
# ==============================================================================
# Estas strings substituem arquivos .png ou links externos.
# Elas desenham as logos oficiais matematicamente.

logos = {
    "BTC": "data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2032%2032%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%2216%22%20r%3D%2216%22%20fill%3D%22%23F7931A%22%2F%3E%3Cpath%20fill%3D%22%23FFF%22%20d%3D%22M23.189%2014.02c.314-2.096-1.283-3.223-3.465-3.975l.708-2.84-1.728-.43-.69%202.765c-.454-.114-.92-.22-1.385-.326l.695-2.783L15.596%206l-.708%202.839c-.376-.086-.746-.17-1.104-.26l.002-.009-2.384-.595-.46%201.846s1.283.294%201.256.312c.7.175.826.638.805%201.006l-.806%203.235c.048.012.11.03.18.057l-.183-.045-1.13%204.532c-.086.212-.303.531-.793.41.018.025-1.256-.313-1.256-.313l-.858%201.978%202.25.561c.418.105.828.215%201.231.318l-.715%202.872%201.727.43.708-2.84c.472.127.93.245%201.378.357l-.706%202.828%201.728.43.715-2.866c2.948.558%205.164.333%206.094-2.332.75-2.141-.037-3.385-1.588-4.192%201.13-.26%201.98-1.003%202.207-2.538zm-3.95%205.538c-.535%202.15-4.16.989-5.338.695l.952-3.819c1.18.295%204.92%20.88%204.385%203.124zm.535-5.569c-.487%201.953-3.495.96-4.464.72l.865-3.469c.969.24%204.067.683%203.6%202.75z%22%2F%3E%3C%2Fsvg%3E",
    "ETH": "data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2032%2032%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%2216%22%20r%3D%2216%22%20fill%3D%22%23627EEA%22%2F%3E%3Cpath%20fill%3D%22%23FFF%22%20d%3D%22M16.498%204v8.87l7.497%203.35zm0%200L9%2016.22l7.498-3.35zM16.5%2016.22v9l7.497-10.55zm0%2022.13l-7.5-10.55%207.5%2010.55zm0-22.13v8.87l-7.5%203.35zM16.5%2022.57l-7.5-3.75%207.5%2010.55z%22%2F%3E%3C%2Fsvg%3E",
    "SOL": "data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2032%2032%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%2216%22%20r%3D%2216%22%20fill%3D%22%23000%22%2F%3E%3Cpath%20d%3D%22M4.5%2011.5h17.2c.4%200%20.7-.1%201-.4l3-3.2c.4-.4.1-1.2-.5-1.2H8c-.4%200-.7.1-1%20.4l-3%203.2c-.4.4-.1%201.2.5%201.2zm23%204.2H10.3c-.4%200-.7.1-1%20.4l-3%203.2c-.4.4-.1%201.2.5%201.2h17.2c.4%200%20.7-.1%201-.4l3-3.2c.4-.4.1-1.2-.5-1.2zM4.5%2025.3h17.2c.4%200%20.7-.1%201-.4l3-3.2c.4-.4.1-1.2-.5-1.2H8c-.4%200-.7.1-1%20.4l-3%203.2c-.4.4-.1%201.2.5%201.2z%22%20fill%3D%22%2314F195%22%2F%3E%3C%2Fsvg%3E",
    "BNB": "data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2032%2032%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%2216%22%20r%3D%2216%22%20fill%3D%22%23F3BA2F%22%2F%3E%3Cpath%20d%3D%22M16%2010.5l-2.7%202.7%202.7%202.7%202.7-2.7L16%2010.5zm-5.7%205.7l2.7-2.7-2.7-2.7-4.6%204.6%204.6%204.6%202.7-2.7-2.7-2.7zm5.7%205.7l2.7-2.7-2.7-2.7-2.7%202.7%202.7%202.7zm5.7-5.7l-2.7%202.7%202.7%202.7%204.6-4.6-4.6-4.6-2.7%202.7z%22%20fill%3D%22%23FFF%22%2F%3E%3C%2Fsvg%3E",
    "PAXG": "data:image/svg+xml;utf8,%3Csvg%20viewBox%3D%220%200%2032%2032%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Ccircle%20cx%3D%2216%22%20cy%3D%2216%22%20r%3D%2216%22%20fill%3D%22%23DEB721%22%2F%3E%3Cpath%20d%3D%22M15.5%2023.5v-3h-3v-5h3v-3h-5v11h5zm2-3h4v-3h-4v-2h5v-3h-7v11h2v-3z%22%20fill%3D%22%23FFF%22%2F%3E%3C%2Fsvg%3E"
}

# ==============================================================================
# 2. CSS PARA OS ESTILOS DE CARDS (SEM INDENTAÇÃO INTERNA NO PYTHON)
# ==============================================================================
st.markdown("""
<style>
    /* CONFIGURAÇÃO GERAL DO GRID */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-bottom: 40px;
    }

    /* ESTILO 1: BRUTALISM GLASS (Fundo escuro, brilho na imagem) */
    .card-style-1 {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.2s;
    }
    .card-style-1:hover {
        transform: scale(1.05);
        border-color: #F3BA2F;
        box-shadow: 0 0 15px rgba(243, 186, 47, 0.2);
    }
    .img-glow img {
        width: 64px;
        height: 64px;
        filter: drop-shadow(0 0 8px rgba(255,255,255,0.2));
    }

    /* ESTILO 2: GOLD PREMIUM (Borda Dourada, Imagem Saturada) */
    .card-style-2 {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-top: 4px solid #F3BA2F;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .img-gold img {
        width: 50px;
        height: 50px;
        /* Truque CSS para deixar qualquer imagem levemente dourada/quente */
        filter: sepia(0.2) contrast(1.1); 
    }

    /* ESTILO 3: MINIMALIST (Ícone Pequeno + Texto Grande) */
    .card-style-3 {
        display: flex;
        align-items: center;
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 50px; /* Pill Shape */
        padding: 10px 25px;
        gap: 15px;
    }
    .img-mini img {
        width: 32px;
        height: 32px;
    }
    
    .label { font-size: 0.8em; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; }
    .value { font-size: 1.2em; color: white; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Laboratório de Visual (Base64/SVG)")
st.write("Teste de renderização de ícones reais sem emojis.")

# ==============================================================================
# 3. RENDERIZAÇÃO DOS EXEMPLOS
# ==============================================================================

st.subheader("Estilo 1: Glassmorphism (Foco na Identidade)")
c1, c2, c3, c4, c5 = st.columns(5)

# Função auxiliar para gerar HTML sem quebrar indentação
def card_glass(nome, ticker, img_url):
    return f"""
<div class="card-style-1">
<div class="img-glow"><img src="{img_url}"></div>
<div class="value">{ticker}</div>
<div class="label">{nome}</div>
</div>
"""

with c1: st.markdown(card_glass("Bitcoin", "BTC", logos["BTC"]), unsafe_allow_html=True)
with c2: st.markdown(card_glass("Ethereum", "ETH", logos["ETH"]), unsafe_allow_html=True)
with c3: st.markdown(card_glass("Solana", "SOL", logos["SOL"]), unsafe_allow_html=True)
with c4: st.markdown(card_glass("Binance", "BNB", logos["BNB"]), unsafe_allow_html=True)
with c5: st.markdown(card_glass("Pax Gold", "PAXG", logos["PAXG"]), unsafe_allow_html=True)


st.divider()
st.subheader("Estilo 2: Gold Premium (Para o seu Cofre)")
k1, k2, k3, k4, k5 = st.columns(5)

def card_gold(ticker, valor, img_url):
    return f"""
<div class="card-style-2">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
<div class="img-gold"><img src="{img_url}"></div>
<div style="text-align:right;">
<div style="color:#F3BA2F; font-size:0.8em;">Saldo</div>
<div style="color:white; font-weight:bold;">{valor}</div>
</div>
</div>
<div style="width:100%; height:1px; background:rgba(255,255,255,0.1);"></div>
<div style="margin-top:10px; font-size:0.9em; color:#94a3b8;">{ticker} / USDT</div>
</div>
"""

with k1: st.markdown(card_gold("BTC", "0.054", logos["BTC"]), unsafe_allow_html=True)
with k2: st.markdown(card_gold("ETH", "1.200", logos["ETH"]), unsafe_allow_html=True)
with k3: st.markdown(card_gold("SOL", "45.00", logos["SOL"]), unsafe_allow_html=True)
with k4: st.markdown(card_gold("BNB", "12.50", logos["BNB"]), unsafe_allow_html=True)
with k5: st.markdown(card_gold("PAXG", "0.100", logos["PAXG"]), unsafe_allow_html=True)


st.divider()
st.subheader("Estilo 3: Minimalista (Listas)")
m1, m2 = st.columns(2)

def card_mini(ticker, img_url):
    return f"""
<div class="card-style-3">
<div class="img-mini"><img src="{img_url}"></div>
<div style="flex-grow:1; color:white; font-weight:bold;">{ticker}</div>
<div style="color:#22c55e;">+2.4%</div>
</div>
"""

with m1:
    st.markdown(card_mini("BTC", logos["BTC"]), unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(card_mini("ETH", logos["ETH"]), unsafe_allow_html=True)

with m2:
    st.markdown(card_mini("SOL", logos["SOL"]), unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    st.markdown(card_mini("PAXG", logos["PAXG"]), unsafe_allow_html=True)
