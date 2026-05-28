"""
Projeto: Canal Juridiquês
Versão: 1.0.18
Descrição: Nome dinâmico para downloads .txt, botão de compartilhar via WhatsApp e explicações de acessibilidade.
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
          "icons": [
            {
              "src": "data:image/png;base64,""" + logo_base64 + """ ",
              "sizes": "192x192",
              "type": "image/png"
            }
          ]
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
    """Transforma a pergunta do usuário em um nome de arquivo válido e curto."""
    texto = texto.lower()
    texto = re.sub(r'[^\w\s]', '', texto)  # Remove pontuação
    palavras = texto.split()[:4]           # Pega as primeiras 4 palavras
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
    st.write("Dúvidas, sugestões ou problemas com a plataforma? Entre em contato conosco.")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# --- CABEÇALHO PRINCIPAL ---
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
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets.")
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
        "Você é o 'Tutor Jurídico Acadêmico' do Canal Juridiquês. Adote postura didática. "
        "Explique conceitos em:\n1) Conceito Puro;\n2) Exemplo Prático;\n3) Fundamentação.\n"
        "Use formatação Markdown."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Digite sua dúvida jurídica aqui..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                historico_api = []
                for m in st.session_state.messages[:-1]:
                    role_api = "user" if m["role"] == "user" else "model"
                    historico_api.append(types.Content(role=role_api, parts=[types.Part.from_text(text=m["content"])]))
                
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
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Recursos adicionais
                audio_bytes = gerar_audio_acessibilidade(full_response)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                
                # Linha de Ações (Download e Compartilhar)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Salvar Resposta (.txt)",
                        data=full_response,
                        file_name=limpar_nome_arquivo(prompt),
                        mime="text/plain"
                    )
                with col2:
                    texto_zap = f"*Canal Juridiquês*\n\n*Pergunta:* {prompt}\n\n*Resposta:* {full_response}"
                    link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}"
                    st.link_button("🟢 Compartilhar no WhatsApp", link_whatsapp)
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) or "503" in str(e) or "UNAVAILABLE" in str(e):
                    st.warning("⚠️ O servidor da IA está sob alta demanda agora. Por favor, aguarde cerca de 20 segundos e envie sua pergunta novamente!")
                else:
                    st.error(f"Ocorreu um erro de conexão. Detalhe técnico: {e}")

# --- 2ª OPÇÃO: METODOLOGIA ---
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    st.warning("⚠️ Esta ferramenta funciona exclusivamente como um **guia estrutural**.")
    
    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:")
    botao_gerar = st.button("🚀 Gerar Estrutura")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = f"Atue como orientador de metodologia Jurídica científica. Estruture em tópicos o tema: '{tema_usuario}'."
        with st.spinner("Analisando o tema..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=PROMPT_METODOLOGIA,
                    config=types.GenerateContentConfig(temperature=0.4) 
                )
                st.markdown("---")
                st.write(response.text)
                
                audio_bytes = gerar_audio_acessibilidade(response.text)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📥 Salvar Estrutura (.txt)",
                        data=response.text,
                        file_name=limpar_nome_arquivo(tema_usuario),
                        mime="text/plain"
                    )
                with col2:
                    texto_zap = f"*Canal Juridiquês - Estrutura TCC*\n\n{response.text}"
                    link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}"
                    st.link_button("🟢 Compartilhar no WhatsApp", link_whatsapp)
            except Exception as e:
                st.error(f"Erro na comunicação com o servidor: {e}")

# --- 3ª OPÇÃO: LEGISLAÇÃO ---
elif opcao_menu == "📜 Consulta à Legislação e Letra da Lei":
    st.subheader("📜 Extrator da Letra da Lei")
    st.write("Consulte o texto exato de artigos de Leis, Códigos ou da Constituição Federal utilizando busca em tempo real.")

    if pedido_lei := st.chat_input("Ex: Artigo 5 da CF, Lei da LGPD..."):
        with st.chat_message("user"):
            st.markdown(pedido_lei)

        with st.chat_message("assistant"):
            PROMPT_LEGISLACAO = f"Extraia o texto literal exato e atualizado da norma: '{pedido_lei}'. Use blocos de citação."
            with st.spinner("Buscando texto oficial atualizado..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=PROMPT_LEGISLACAO,
                        config=types.GenerateContentConfig(tools=[{"google_search": {}}], temperature=0.3)
                    )
                    st.markdown("### 🏛️ Texto Legal Encontrado")
                    st.write(response.text)
                    
                    audio_bytes = gerar_audio_acessibilidade(response.text)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Salvar Lei (.txt)",
                            data=response.text,
                            file_name=limpar_nome_arquivo(pedido_lei),
                            mime="text/plain"
                        )
                    with col2:
                        texto_zap = f"*Canal Juridiquês - Legislação*\n\n{response.text}"
                        link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}"
                        st.link_button("🟢 Compartilhar no WhatsApp", link_whatsapp)
                except Exception as e:
                    st.error(f"Falha ao buscar a lei: {e}")

# --- 4ª OPÇÃO: DICIONÁRIO ---
elif opcao_menu == "📔 Dicionário Jurídico e Latim":
    st.subheader("📔 Dicionário Jurídico e Expressões em Latim")
    st.write("Digite um termo técnico ou expressão em latim para obter a tradução e o significado aplicado ao Direito.")

    if termo_busca := st.chat_input("Ex: Erga omnes, Vacatio Legis..."):
        with st.chat_message("user"):
            st.markdown(termo_busca)

        with st.chat_message("assistant"):
            with st.spinner(f"Buscando o significado de '{termo_busca}'..."):
                try:
                    resultado = consultar_dicionario_cache(termo_busca.strip().lower())
                    st.markdown(resultado)
                    
                    audio_bytes = gerar_audio_acessibilidade(resultado)
                    if audio_bytes:
                        st.audio(audio_bytes, format="audio/mp3")
                        
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Salvar Significado (.txt)",
                            data=resultado,
                            file_name=limpar_nome_arquivo(termo_busca),
                            mime="text/plain"
                        )
                    with col2:
                        texto_zap = f"*Canal Juridiquês - Dicionário*\n\n*Termo:* {termo_busca}\n\n{resultado}"
                        link_whatsapp = f"https://api.whatsapp.com/send?text={urllib.parse.quote(texto_zap)}"
                        st.link_button("🟢 Compartilhar no WhatsApp", link_whatsapp)
                except Exception as e:
                    st.error(f"Erro ao buscar o termo: {e}")
