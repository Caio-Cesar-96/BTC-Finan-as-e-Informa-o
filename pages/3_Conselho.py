import streamlit as st

st.set_page_config(layout="wide")

# --- BLOCO DE ESTILO (CSS) ---
st.markdown("""
<style>
.container-teste {
    display: flex;
    gap: 20px;
    justify-content: center;
    padding: 40px;
}
.card-teste {
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 15px;
    padding: 30px;
    width: 280px;
    text-align: center;
    transition: 0.3s;
}
.card-teste:hover {
    transform: translateY(-10px);
    border-color: #F3BA2F;
}
.icon-box {
    margin-bottom: 20px;
}
.icon-box img {
    width: 60px;
    height: 60px;
}
.titulo-card {
    color: #F3BA2F;
    font-size: 1.2em;
    font-weight: bold;
    margin-bottom: 10px;
}
.desc-card {
    color: #9ca3af;
    font-size: 0.85em;
}
</style>
""", unsafe_allow_html=True)

# --- ASSETS EM BASE64 ---
# 1. Logo Oficial Bitcoin
btc_logo = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA2NCA2NCI+PGNpcmNsZSBjeD0iMzIiIGN5PSIzMiIgcj0iMzIiIGZpbGw9IiNGNzkzMUEiLz48cGF0aCBkPSJNNDQgMzkuNGMtLjggNC4yLTQuMSA3LjItOC42IDcuMmgtNy40di05LjNoMy43YzIuMSAwIDMuOCAxLjcgMy44IDMuOC4xIDIuMiAxLjggMy45IDQgMy45eiIgZmlsbD0id2hpdGUiLz48cGF0aCBkPSJNMjggMjRoLTQuNHYtNC4zaDQuNHY0LjN6bTAgMjIuNmgtNC40di00LjNoNC40djQuM3ptMTIuNC0xNS45Yy0uNi0zLjMtMy02LTYuMi02LjJoLTYuMnYtNC4zaC00djQuM2gtMi40djRoMi40djE0LjdoLTIuNHY0aDIuNHY0LjNoNHYtNC4zaDcuOGM0LjkgMCA5LjEtMy41IDkuOS04LjMuNC0yLjMtLjEtNC42LTEuMy02LjV6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg=="

# 2. Ícone Trading Dourado (Customizado para o app)
trading_icon = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlPSIjRjNCQTJGIiBzdHJva2Utd2lkdGg9IjEuNSI+PHBhdGggc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBkPSJNMTEgM2gydjE0aC0yek03IDhoMnY5SDd6TTE1IDExaDJ2N2gtMnpNMyAxNWgydjJoLTN6TTE5IDhoMnY5aC0yeiIgLz48L3N2Zz4="

# 3. Ícone Segurança Minimalista
security_icon = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGZpbGw9Im5vbmUiIHZpZXdCb3g9IjAgMCAyNCAyNCIgc3Ryb2tlPSIjYThhOGE4IiBzdHJva2Utd2lkdGg9IjEuNSI+PHBhdGggc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBkPSJNMTIgMjJzOC00IDgtMTBWNWwtOC0zLTggM3Y3YzAgNiA4IDEwIDggMTB6IiAvPjwvc3ZnPg=="

st.title("Possibilidades Visuais com Base64")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
<div class="card-teste">
<div class="icon-box"><img src="{btc_logo}"></div>
<div class="titulo-card">Branding Oficial</div>
<div class="desc-card">Uso de logos originais com alta nitidez e cores fiéis aos ativos.</div>
</div>
""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
<div class="card-teste" style="border-top: 4px solid #F3BA2F;">
<div class="icon-box"><img src="{trading_icon}"></div>
<div class="titulo-card">Personalização</div>
<div class="desc-card">Ícones técnicos criados com a cor exata do seu Dourado Institucional.</div>
</div>
""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
<div class="card-teste">
<div class="icon-box"><img src="{security_icon}"></div>
<div class="titulo-card">Minimalismo</div>
<div class="desc-card">Estilo linear moderno para menus e ferramentas auxiliares.</div>
</div>
""", unsafe_allow_html=True)
