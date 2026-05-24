import streamlit as st
from google import genai
from google.genai import types
import os

# Configuração da página web
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# 1. ESTILIZAÇÃO CUSTOMIZADA (CSS)
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid #c5a059;
    }

    div.stButton > button:first-child {
        background-color: #c5a059;
        color: white;
        border-radius: 10px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #a38446;
        color: white;
        transform: scale(1.02);
    }

    [data-testid="stChatMessage"] {
        border-radius: 15px;
        background-color: #1e2430;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# NOME DO ARQUIVO DA LOGO
NOME_LOGO = "logo.png"

# MENU LATERAL (A logo fica brilhando aqui!)
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #c5a059;'>⚖️</h1>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='text-align: center;'>Canal Juridiquês</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.header("📚 Indicações")
    st.write("Apoie o nosso projeto gratuito utilizando os links dos nossos parceiros!")
    
    st.markdown("### 📙 Vade Mecum Atualizado")
    st.link_button("👉 Ver na Amazon Brasil", "https://www.amazon.com.br/s?k=vade+mecum&i=books")
    
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL (LIMPO E MINIMALISTA NO CENTRO)
st.markdown("<h1 style='color: #c5a059; margin-bottom: 0px;'>⚖️ Canal Juridiquês</h1>", unsafe_allow_html=True)
st.write("*Seu ecossistema acadêmico inteligente.*")
st.markdown("---")

# ORGANIZAÇÃO EM ABAS
tab1, tab2 = st.tabs(["💬 Tutor de IA", "📖 Como Pesquisar"])

with tab1:
    PROMPT_SISTEMA = (
        "Você é o 'Tutor Jurídico Acadêmico' do site Canal Juridiquês. Ajude estudantes de Direito. "
        "Seja didático e use formatação limpa. Links: [Compre na Amazon](https://www.amazon.com.br/s?k=NOME_DO_LIVRO&i=books)"
    )

    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Em que posso ajudar na sua pesquisa hoje?"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            try:
                history_api = []
                for m in st.session_state.messages[:-1]:
                    role_api = "user" if m["role"] == "user" else "model"
                    history_api.append(types.Content(role=role_api, parts=[types.Part.from_text(text=m["content"])]))
                
                chat = client.chats.create(
                    model="gemini-2.5-flash",
                    history=history_api,
                    config=types.GenerateContentConfig(system_instruction=PROMPT_SISTEMA, temperature=0.3)
                )
                
                response = chat.send_message(prompt)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                message_placeholder.error(f"Erro na conexão: {e}")

with tab2:
    st.header("Metodologia de Pesquisa")
    st.info("Aprenda a usar o Canal Juridiquês para acelerar seus estudos.")
    with st.expander("🔎 Como buscar jurisprudência?"):
        st.write("Peça ao tutor para criar uma 'string de busca' com os termos AND e OR.")
    with st.expander("📚 Como estruturar meu TCC?"):
        st.write("Peça sugestões de 'Problema de Pesquisa' e 'Sumário Provisório'.")

# RODAPÉ
st.markdown("---")
st.caption("⚠️ O Canal Juridiquês é uma ferramenta de suporte pedagógico. Não substitui um advogado.")
