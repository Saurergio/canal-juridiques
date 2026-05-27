"""
Projeto: Canal Juridiquês
Versão: 1.0.14
Descrição: Refinamento visual da barra lateral (remoção de texto redundante quando o logo existe).
Autoria: Sergio Moreira Neri
"""
import streamlit as st
from google import genai
from google.genai import types
import os
from gtts import gTTS
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    html, body, [class*="css"] { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    [data-testid="stSidebar"] { background-color: #0e1117; border-right: 1px solid #c5a059; }
    div.stButton > button:first-child {
        background-color: #c5a059; color: white; border-radius: 10px; border: none;
        padding: 12px 20px; width: 100%; font-size: 16px; transition: 0.3s;
    }
    div.stButton > button:hover { background-color: #a38446; color: white; }
    div[data-baseweb="select"] { border: 1px solid #c5a059; border-radius: 8px; }
    [data-testid="stChatMessage"] { border-radius: 15px; background-color: #1e2430; margin-bottom: 12px; padding: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE TEXT-TO-SPEECH (ACESSIBILIDADE) ---
def gerar_audio_acessibilidade(texto):
    """Converte texto em áudio usando gTTS em memória."""
    try:
        tts = gTTS(text=texto, lang='pt', tld='com.br', slow=False)
        arquivo_em_memoria = io.BytesIO()
        tts.write_to_fp(arquivo_em_memoria)
        return arquivo_em_memoria.getvalue()
    except Exception:
        return None

NOME_LOGO = "logo.png"

# --- MENU LATERAL ---
with st.sidebar:
    # Lógica inteligente: se o logo existe, exibe só o logo. Se não, exibe emoji + texto.
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True, output_format="PNG")
    else:
        st.markdown("<h1 style='text-align: center; color: #c5a059;'>⚖️</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #c5a059;'>Canal Juridiquês</h3>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.header("📚 Indicações")
    st.write("Apoie o nosso projeto gratuito utilizando os links dos nossos parceiros!")
    st.markdown("### 📙 Vade Mecum Atualizado")
    st.link_button("👉 Ver na Amazon Brasil", "https://www.amazon.com.br/s?k=vade+mecum&i=books")
    st.markdown("---")
    st.header("📬 Fale Conosco")
    st.write("Dúvidas, sugestões ou problemas com a plataforma? Entre em contato conosco.")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# --- CABEÇALHO PRINCIPAL ORIGINAL ---
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

st.info("""
Olá! O **Canal Juridiquês** é o seu assistente virtual **100% gratuito** criado para descomplicar a jornada do estudante de Direito. 
Nossa missão é apoiar seus estudos, esclarecer dúvidas e fortalecer o seu aprendizado acadêmico sem cobrar nada por isso.
""")
st.markdown("<br>", unsafe_allow_html=True)

# --- NAVEGAÇÃO ---
opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
    [
        "💬 Tutor de Inteligência Artificial", 
        "📖 Guia de Metodologia de Pesquisa", 
        "📜 Consulta à Legislação e Letra da Lei",
        "📔 Dicionário Jurídico e Latim"
    ]
)
st.markdown("<br>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA API ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.stop()

# --- FUNÇÃO DE CACHE PARA O DICIONÁRIO ---
@st.cache_data(ttl=86400, show_spinner=False)
def consultar_dicionario_cache(termo):
    PROMPT_DICIONARIO = (
        f"Você é um Dicionário Jurídico dinâmico do Canal Juridiquês. "
        f"Explique de forma objetiva, didática e direta o significado do seguinte termo: '{termo}'.\n\n"
        f"REGRAS DE FORMATAÇÃO:\n"
        f"1. Se o termo for em latim, forneça a tradução literal destacada logo na primeira linha.\n"
        f"2. Explique o conceito jurídico em no máximo dois parágrafos curtos.\n"
        f"3. Forneça um exemplo rápido de aplicação desse termo no direito brasileiro."
    )
    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=PROMPT_DICIONARIO,
        config=types.GenerateContentConfig(temperature=0.3)
    )
    return resposta.text

# --- 1ª OPÇÃO: TUTOR IA ---
if opcao_menu == "💬 Tutor de Inteligência Artificial":
    PROMPT_TUTOR = (
        "Você é o 'Tutor Jurídico Acadêmico' do portal Canal Juridiquês. Adote uma postura didática. "
        "Ao explicar conceitos, quebre a resposta em:\n"
        "1) Conceito Puro;\n2) Exemplo Prático;\n3) Fundamentação.\n"
        "Use formatação Markdown para leitura rápida no celular."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st
