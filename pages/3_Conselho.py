import streamlit as st

st.set_page_config(layout="wide")

# CSS para os cards de teste
st.markdown("""
    <style>
    .test-container {
        display: flex;
        gap: 20px;
        padding: 20px;
    }
    .test-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        width: 250px;
        transition: 0.3s;
    }
    .test-card:hover {
        transform: translateY(-5px);
        border-color: #F3BA2F;
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    .img-box {
        margin-bottom: 15px;
        display: flex;
        justify-content: center;
    }
    .img-box img {
        width: 50px;
        height: 50px;
        filter: drop-shadow(0 0 8px rgba(243, 186, 47, 0.3));
    }
    .label { color: #9ca3af; font-size: 0.8em; text-transform: uppercase; letter-spacing: 1px; }
    .value { color: white; font-size: 1.4em; font-weight: bold; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# 1. BASE64 - LOGO BITCOIN (Colorida Oficial)
logo_btc = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCIgd2lkdGg9IjY0IiBoZWlnaHQ9IjY0Ij48Y2lyY2xlIGN4PSIzMiIgY3k9IjMyIiByPSIzMiIgZmlsbD0iI0Y3OTMxQSIvPjxwYXRoIGQ9Ik00NCAzOS40Yy0uOCA0LjItNC4xIDcuMi04LjYgNy4yaC03LjR2LTkuM2gzLjdjMi4xIDAgMy44IDEuNyAzLjggMy44LjEgMi4yIDEuOCAzLjkgNCAzLjl6IiBmaWxsPSJ3aGl0ZSIvPjxwYXRoIGQ9Ik0yOCAyNGgtNC40di00LjNoNC40djQuM3ptMCAyMi42aC00LjR2LTQuM2g0LjR2NC4zem0xMi40LTE1LjljLS42LTMuMy0zLTYtNi4yLTYuMmgtNi4ydi00LjNoLTR2NC4zaC0yLjR2NGgyLjR2MTQuN2gtMi40djRoMi40djQuM2g0di00LjNoNy44YzQuOSAwIDkuMS0zLjUgOS45LTguMy40LTIuMy0uMS00LjYtMS4zLTYuNXoiIGZpbGw9IndoaGl0ZSIvPjwvc3ZnPg=="

# 2. BASE64 - ÍCONE CALCULADORA (Dourado Custom)
icon_calc = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlPSIjRjNCQTJGIiBzdHJva2Utd2lkdGg9IjEuNSI+PHBhdGggc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBkPSJNMTUgNmgzYTIgMiAwIDAxMiAydjExYTIgMiAwIDAxLTIgMkg2YTIgMiAwIDAxLTItMlY4YTIgMiAwIDAxMi0yaDNtNC0zdi00bS03IDR2LTRtLTQgMTBoMTJtLTkgNGgybTMtNGgybS04LTRoMm0zLTRoMiIgLz48L3N2Zz4="

# 3. BASE64 - ÍCONE PORTFOLIO/MALETA (Minimalista)
icon_briefcase = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlPSIjRjNCQTJGIiBzdHJva2Utd2lkdGg9IjEuNSI+PHBhdGggc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBkPSJNMjEgOGgtMXYxMWExIDIgMCAwMS0yIDJINmExIDIgMCAwMS0yLTJWOGgtMVY3YTIgMiAwIDAxMi0yaDRWNGExIDIgMCAwMTEtMWg0YTEgMiAwIDAxMSAxdjFoNFY3YTIgMiAwIDAxMiAyVjh6bS05IDV2NG0tMy00aDZtLTYtOWg0djFIOXYtMXoiIC8+PC9zdmc+"

st.title("🧪 Laboratório de Estilização Base64")
st.write("Veja como os ícones vetoriais elevam o visual comparado aos emojis.")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
        <div class="test-card">
            <div class="img-box"><img src="{logo_btc}"></div>
            <div class="label">Ativo de Destaque</div>
            <div class="value">Bitcoin</div>
            <div style="color: #22c55e; font-size: 0.8em; margin-top: 10px;">Identidade Oficial</div>
        </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
        <div class="test-card" style="border-top: 3px solid #F3BA2F;">
            <div class="img-box"><img src="{icon_calc}"></div>
            <div class="label">Ferramenta</div>
            <div class="value">Calculadora</div>
            <div style="color: #F3BA2F; font-size: 0.8em; margin-top: 10px;">SVG Dourado Custom</div>
        </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
        <div class="test-card">
            <div class="img-box"><img src="{icon_briefcase}"></div>
            <div class="label">Gestão</div>
            <div class="value">Portfólio</div>
            <div style="color: #9ca3af; font-size: 0.8em; margin-top: 10px;">Traços Finos (Lineal)</div>
        </div>
    """, unsafe_allow_html=True)

st.info("💡 Observe como os ícones dourados (Calculadora e Maleta) têm a cor exata do seu layout, algo impossível de fazer com emojis padrão.")
