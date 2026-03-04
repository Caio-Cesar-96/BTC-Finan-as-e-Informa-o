import streamlit as st

st.set_page_config(layout="wide", page_title="Laboratório Final", page_icon="🧪")

# ==============================================================================
# 1. BANCO DE IMAGENS (LINKS DIRETOS OFICIAIS)
# ==============================================================================
# Usando a CDN do CoinMarketCap para garantir qualidade perfeita instantânea.
logos_web = {
    "BTC": "https://s2.coinmarketcap.com/static/img/coins/64x64/1.png",
    "ETH": "https://s2.coinmarketcap.com/static/img/coins/64x64/1027.png",
    "SOL": "https://s2.coinmarketcap.com/static/img/coins/64x64/5426.png",
    "BNB": "https://s2.coinmarketcap.com/static/img/coins/64x64/1839.png",
    "PAXG": "https://s2.coinmarketcap.com/static/img/coins/64x64/4705.png"
}

# ==============================================================================
# 2. CSS "GLASS PREMIUM" (Sem indentação para não quebrar)
# ==============================================================================
st.markdown("""
<style>
    .card-final {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.4), rgba(15, 23, 42, 0.6));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
        transition: transform 0.3s ease, border-color 0.3s ease;
        backdrop-filter: blur(10px);
    }
    .card-final:hover {
        transform: translateY(-5px);
        border-color: #F3BA2F;
        box-shadow: 0 10px 30px -10px rgba(243, 186, 47, 0.2);
    }
    .img-container {
        margin-bottom: 15px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .img-container img {
        width: 64px;
        height: 64px;
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.1));
        border-radius: 50%;
    }
    .ticker-text {
        color: white;
        font-size: 1.4em;
        font-weight: 800;
        letter-spacing: 1px;
    }
    .name-text {
        color: #94a3b8;
        font-size: 0.8em;
        text-transform: uppercase;
        margin-top: 5px;
        letter-spacing: 2px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧪 Teste Visual Definitivo")
st.write("Visualização usando Logos Oficiais (CDN High-Res).")
st.markdown("<br>", unsafe_allow_html=True)

# ==============================================================================
# 3. RENDERIZAÇÃO
# ==============================================================================

c1, c2, c3, c4, c5 = st.columns(5)

def render_card(nome, ticker, url):
    return f"""
<div class="card-final">
<div class="img-container"><img src="{url}"></div>
<div class="ticker-text">{ticker}</div>
<div class="name-text">{nome}</div>
</div>
"""

with c1: st.markdown(render_card("Bitcoin", "BTC", logos_web["BTC"]), unsafe_allow_html=True)
with c2: st.markdown(render_card("Ethereum", "ETH", logos_web["ETH"]), unsafe_allow_html=True)
with c3: st.markdown(render_card("Solana", "SOL", logos_web["SOL"]), unsafe_allow_html=True)
with c4: st.markdown(render_card("Binance", "BNB", logos_web["BNB"]), unsafe_allow_html=True)
with c5: st.markdown(render_card("Pax Gold", "PAXG", logos_web["PAXG"]), unsafe_allow_html=True)

st.divider()
st.info("ℹ️ Se estas imagens aparecerem, significa que este é o visual que teremos no app. O método anterior (Base64) estava corrompendo o texto por ser muito longo.")
