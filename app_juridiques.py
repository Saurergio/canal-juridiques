"""
Projeto: Canal Juridiquês
Versão: 1.0.19
Descrição: Persistência de estado (Correção do botão que some) e botão genérico de Compartilhar.
Autoria: Sergio Moreira Neri
"""
import streamlit as st
from google import genai
from google.genai import types
import os
from gtts import gTTS
import io
import base64
import re
import urllib.parse

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# --- UTILITÁRIO PWA ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return None

def inicializar_pwa():
    logo_base64 = get_base64_of_bin_file('icon192.png')
    if logo_base64:
        st.markdown(f'<link rel="apple-touch-icon" href="data:image/png;base64,{logo_base64}">', unsafe_allow_html=True)
        st.markdown(f'<link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,{logo_base64}">', unsafe_allow_html=True)
        manifest_text = """
        {
          "name": "Canal Juridiquês",
          "short_name": "Juridiquês",
          "start_url": "./",
          "display": "standalone",
          "background_color": "#0e1117",
          "theme_color": "#c5a059",
          "description": "Seu ecossistema acadêmico inteligente com IA.",
          "icons": [{"src": "data:image/png;base64,""" + logo_base64 + """ ","sizes": "192x192","type": "image/png"}]
        }
        """
        manifest_b64 = base64.b64encode(manifest_text.encode('utf-8')).decode('utf-8')
        st.markdown(f'<link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">', unsafe_allow_html=True)

inicializar_pwa()

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
    [data-testid="stChatMessage"] { border-radius: 15px; background-color: #1e2430; margin-bottom: 12px; padding: 14px; color: #FAFAFA; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES UTILITÁRIAS ---
def gerar_audio_acessibilidade(texto):
    try:
        tts = gTTS(text=texto, lang='pt', tld='com.br', slow=False)
        arquivo_em_memoria = io.BytesIO()
        tts.write_to_fp(arquivo_em_memoria)
        return arquivo_em_memoria.getvalue()
    except Exception:
        return None

def limpar_nome_arquivo(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    palavras = texto.split()[:4]
    return "pesquisa_" + "_".join(palavras) + ".txt"

NOME_LOGO = "logo.png"

# --- MENU LATERAL ---
with st.sidebar:
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
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")

# --- CABEÇALHO PRINCIPAL ---
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
    ["💬 Tutor de Inteligência Artificial", "📖 Guia de Metodologia de Pesquisa", "📜 Consulta à Legislação e Letra da Lei", "📔 Dicionário Jurídico e Latim"]
)
st.markdown("<br>", unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA API ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets.")
    st.stop()

@st.cache_data(ttl=86400, show_spinner=False)
def consultar_dicionario_cache(termo):
    PROMPT = f"Você é um Dicionário Jurídico dinâmico do Canal Juridiquês. Explique de forma objetiva o termo: '{termo}'. Se for latim, traduza. Use máximo dois parágrafos e dê um exemplo."
    resposta = client.models.generate_content(model='gemini-2.5-flash', contents=PROMPT, config=types.GenerateContentConfig(temperature=0.3))
    return resposta.text

# --- 1ª OPÇÃO: TUTOR IA ---
if opcao_menu == "💬 Tutor de Inteligência Artificial":
    PROMPT_TUTOR = "Você é o 'Tutor Jurídico Acadêmico' do Canal Juridiquês. Quebre a explicação em:\n1) Conceito Puro;\n2) Exemplo Prático;\n3) Fundamentação. Use Markdown."

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Renderiza o histórico e fixa os botões
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if msg.get("audio"):
                    st.audio(msg["audio"], format="audio/mp3")
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Salvar (.txt)", msg["content"], file_name=limpar_nome_arquivo(msg.get("prompt", "resposta")), key=f"dl_tutor_{i}")
                with col2:
                    texto_zap = f"*Canal Juridiquês*\n\n*Pergunta:* {msg.get('prompt', '')}\n\n*Resposta:* {msg['content']}"
                    st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}")

    if prompt := st.chat_input("Digite sua dúvida jurídica aqui..."):
        # Impede renderização dupla do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                historico_api = [types.Content(role="user" if m["role"] == "user" else "model", parts=[types.Part.from_text(text=m["content"])]) for m in st.session_state.messages[:-1]]
                response_stream = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=[*historico_api, types.Content(role="user", parts=[types.Part.from_text(text=prompt)])],
                    config=types.GenerateContentConfig(system_instruction=PROMPT_TUTOR, temperature=0.6)
                )
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
                audio_bytes = gerar_audio_acessibilidade(full_response)
                # Salva TUDO no estado para não sumir no F5
                st.session_state.messages.append({"role": "assistant", "content": full_response, "audio": audio_bytes, "prompt": prompt})
                st.rerun() # Força o recarregamento limpo com os botões
                
            except Exception as e:
                st.error("⚠️ O servidor está sob alta demanda ou ocorreu um erro. Tente novamente.")

# --- 2ª OPÇÃO: METODOLOGIA ---
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos")
    if 'metodologia' not in st.session_state: st.session_state.metodologia = None
    
    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:")
    if st.button("🚀 Gerar Estrutura") and tema_usuario:
        with st.spinner("Analisando o tema..."):
            try:
                response = client.models.generate_content(model='gemini-2.5-flash', contents=f"Estruture em tópicos científicos o tema: '{tema_usuario}'.", config=types.GenerateContentConfig(temperature=0.4))
                audio = gerar_audio_acessibilidade(response.text)
                st.session_state.metodologia = {"tema": tema_usuario, "texto": response.text, "audio": audio}
            except Exception as e:
                st.error("Erro na comunicação.")

    # Exibe o resultado gravado na memória
    if st.session_state.metodologia:
        st.markdown("---")
        st.write(st.session_state.metodologia["texto"])
        if st.session_state.metodologia["audio"]: st.audio(st.session_state.metodologia["audio"], format="audio/mp3")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("📥 Salvar (.txt)", st.session_state.metodologia["texto"], file_name=limpar_nome_arquivo(st.session_state.metodologia["tema"]), key="dl_met")
        with col2:
            st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(st.session_state.metodologia['texto'])}")

# --- 3ª OPÇÃO: LEGISLAÇÃO ---
elif opcao_menu == "📜 Consulta à Legislação e Letra da Lei":
    st.subheader("📜 Extrator da Letra da Lei")
    if 'legislacao' not in st.session_state: st.session_state.legislacao = None

    if pedido_lei := st.chat_input("Ex: Artigo 5 da CF, Lei da LGPD..."):
        with st.spinner("Buscando texto oficial..."):
            try:
                response = client.models.generate_content(model='gemini-2.5-flash', contents=f"Extraia o texto literal exato da norma: '{pedido_lei}'.", config=types.GenerateContentConfig(tools=[{"google_search": {}}], temperature=0.3))
                audio = gerar_audio_acessibilidade(response.text)
                st.session_state.legislacao = {"pedido": pedido_lei, "texto": response.text, "audio": audio}
            except Exception:
                st.error("Falha ao buscar a lei.")

    # Exibe o resultado gravado na memória
    if st.session_state.legislacao:
        with st.chat_message("user"): st.markdown(st.session_state.legislacao["pedido"])
        with st.chat_message("assistant"):
            st.write(st.session_state.legislacao["texto"])
            if st.session_state.legislacao["audio"]: st.audio(st.session_state.legislacao["audio"], format="audio/mp3")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Salvar (.txt)", str(st.session_state.legislacao["texto"]), file_name=limpar_nome_arquivo(st.session_state.legislacao["pedido"]), key="dl_leg")
            with col2:
                st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(str(st.session_state.legislacao['texto']))}")

# --- 4ª OPÇÃO: DICIONÁRIO ---
elif opcao_menu == "📔 Dicionário Jurídico e Latim":
    st.subheader("📔 Dicionário Jurídico e Latim")
    if 'dicionario' not in st.session_state: st.session_state.dicionario = None

    if termo_busca := st.chat_input("Ex: Erga omnes..."):
        with st.spinner("Buscando..."):
            try:
                resultado = consultar_dicionario_cache(termo_busca.strip().lower())
                audio = gerar_audio_acessibilidade(resultado)
                st.session_state.dicionario = {"termo": termo_busca, "texto": resultado, "audio": audio}
            except Exception:
                st.error("Erro ao buscar o termo.")

    # Exibe o resultado gravado na memória
    if st.session_state.dicionario:
        with st.chat_message("user"): st.markdown(st.session_state.dicionario["termo"])
        with st.chat_message("assistant"):
            st.markdown(st.session_state.dicionario["texto"])
            if st.session_state.dicionario["audio"]: st.audio(st.session_state.dicionario["audio"], format="audio/mp3")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Salvar (.txt)", st.session_state.dicionario["texto"], file_name=limpar_nome_arquivo(st.session_state.dicionario["termo"]), key="dl_dic")
            with col2:
                texto_zap = f"*Dicionário Jurídico*\n\n*Termo:* {st.session_state.dicionario['termo']}\n\n{st.session_state.dicionario['texto']}"
                st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}")
