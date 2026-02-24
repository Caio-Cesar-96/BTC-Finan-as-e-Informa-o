import streamlit as st

# Configuração da página
st.set_page_config(page_title="Laboratório UI", page_icon="🧪", layout="wide")

# ==========================================
# O "MOTOR" DO VISUAL (NOSSO CSS INJETADO)
# ==========================================
st.markdown("""
    <style>
    /* 1. BOTÃO NEON / CYBERPUNK */
    .btn-neon {
        display: block;
        background-color: transparent;
        color: #0ff;
        border: 2px solid #0ff;
        padding: 12px 20px;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 2px;
        border-radius: 5px;
        box-shadow: 0 0 5px #0ff, inset 0 0 5px #0ff;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .btn-neon:hover {
        background-color: #0ff;
        color: #000;
        box-shadow: 0 0 10px #0ff, 0 0 30px #0ff;
    }

    /* 2. BOTÃO WEB3 / CRYPTO (Gradiente) */
    .btn-crypto {
        display: block;
        background: linear-gradient(45deg, #8b5cf6, #d946ef);
        color: white;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(217, 70, 239, 0.4);
        cursor: pointer;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .btn-crypto:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(217, 70, 239, 0.6);
    }

    /* 3. BOTÃO INSTITUCIONAL / WALL STREET */
    .btn-wallstreet {
        display: block;
        background-color: #0f172a;
        color: #94a3b8;
        border: 1px solid #334155;
        padding: 12px 20px;
        border-radius: 3px;
        font-family: monospace;
        font-size: 14px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-wallstreet:hover {
        background-color: #f8fafc;
        color: #0f172a;
        border-color: #f8fafc;
    }

    /* 4. EFEITO VIDRO (Glassmorphism) */
    .btn-glass {
        display: block;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white;
        padding: 12px 24px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    .btn-glass:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
    }

    /* UM CARD DE INFORMAÇÃO ELEGANTE */
    .card-pro {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-left: 4px solid #F3BA2F;
        padding: 20px;
        border-radius: 8px;
        color: #cbd5e1;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# A INTERFACE DO LABORATÓRIO
# ==========================================
st.title("🧪 Laboratório de Interface (UI/UX)")
st.write("Aqui estão as principais vertentes de design que podemos aplicar no nosso sistema com HTML e CSS.")
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.subheader("1. Cyberpunk")
    st.markdown('<div class="btn-neon">Comprar BTC</div>', unsafe_allow_html=True)

with col2:
    st.subheader("2. Web3 Crypto")
    st.markdown('<div class="btn-crypto">Stake Agora</div>', unsafe_allow_html=True)

with col3:
    st.subheader("3. Wall Street")
    st.markdown('<div class="btn-wallstreet">EXEC_ORDER()</div>', unsafe_allow_html=True)

with col4:
    st.subheader("4. Glass Apple")
    st.markdown('<div class="btn-glass">Ver Portfólio</div>', unsafe_allow_html=True)


st.divider()
st.subheader("📊 Painéis e Cards em HTML")
st.write("Além dos botões, o HTML brilha mesmo é na hora de mostrar dados em formato de 'Dashboards', como fizemos na calculadora. Olha o nível de profissionalismo de um Card Avançado:")

st.markdown("""
    <div class="card-pro">
        <span style="color: #9ca3af; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px;">Desempenho Geral do Portfólio</span><br>
        <span style="font-size: 2.5em; font-weight: bold; color: white;">&#36;14,250.80</span>
        <span style="color: #16a34a; font-size: 1.2em; font-weight: bold; margin-left: 10px;">+&#36;1,250.00 (+8.5%)</span>
        <hr style="border: 0; height: 1px; background: rgba(255,255,255,0.1); margin: 15px 0;">
        <span style="font-size: 0.9em; color: #cbd5e1;">🟢 Bitcoin (BTC) puxou a alta hoje. Última atualização: 2 min atrás.</span>
    </div>
""", unsafe_allow_html=True)#Em brave
