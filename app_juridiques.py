"""
Projeto: Canal Juridiquês
Versão: 1.0.15
Descrição: Reversão dos módulos de Legislação e Dicionário para formulários clássicos (Correção de UX do chat_input).
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
                
                # Gera o áudio
                audio_bytes = gerar_audio_acessibilidade(full_response)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                
                # Botão de Salvar
                st.download_button(
                    label="📥 Salvar Resposta (.txt)",
                    data=full_response,
                    file_name="tutor_juridiques.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ Nossa inteligência artificial está atendendo a muitos alunos agora! Por favor, aguarde cerca de 20 segundos e tente novamente.")
                else:
                    st.error(f"Ocorreu um erro de conexão. Detalhe técnico: {e}")

# --- 2ª OPÇÃO: METODOLOGIA ---
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    st.warning("⚠️ Esta ferramenta funciona exclusivamente como um **guia estrutural**. A IA não redigirá trabalhos prontos.")
    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:")
    botao_gerar = st.button("🚀 Gerar Estrutura")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = f"Atue como orientador de metodologia. Estruture em tópicos o tema: '{tema_usuario}'. Formato: Formato, Título, Problema, Objetivos, Sumário."
        with st.spinner("Analisando o tema..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=PROMPT_METODOLOGIA,
                    config=types.GenerateContentConfig(temperature=0.4) 
                )
                st.markdown("---")
                st.write(response.text)
                
                # Áudio
                audio_bytes = gerar_audio_acessibilidade(response.text)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    
                # Botão de Salvar
                st.download_button(
                    label="📥 Salvar Estrutura (.txt)",
                    data=response.text,
                    file_name="estrutura_tcc.txt",
                    mime="text/plain"
                )
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ Limite de requisições atingido. Aguarde 20 segundos e tente novamente.")
                else:
                    st.error(f"Erro na comunicação com o servidor. Detalhe técnico para depuração: {e}")

# --- 3ª OPÇÃO: LEGISLAÇÃO ---
elif opcao_menu == "📜 Consulta à Legislação e Letra da Lei":
    st.subheader("📜 Extrator da Letra da Lei")
    st.write("Consulte o texto exato de artigos de Leis, Códigos ou da Constituição Federal utilizando busca em tempo real.")

    pedido_lei = st.text_input("Qual lei ou artigo específico você precisa consultar?", placeholder="Ex: Artigo 5 da CF, Lei da LGPD...")
    botao_buscar = st.button("🔍 Buscar Texto Literal")

    if botao_buscar and pedido_lei:
        PROMPT_LEGISLACAO = f"Extraia o texto literal exato e atualizado da norma: '{pedido_lei}'. Use blocos de citação."
        with st.spinner("Buscando texto oficial atualizado..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_LEGISLACAO,
                    config=types.GenerateContentConfig(tools=[{"google_search": {}}], temperature=0.3)
                )
                st.markdown("---")
                st.markdown("### 🏛️ Texto Legal Encontrado")
                st.write(response.text)
                
                # Áudio
                audio_bytes = gerar_audio_acessibilidade(response.text)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    
                # Botão de Salvar
                st.download_button(
                    label="📥 Salvar Lei (.txt)",
                    data=response.text,
                    file_name="letra_da_lei.txt",
                    mime="text/plain"
                )
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ Servidores ocupados no momento. Aguarde uns 20 segundinhos e tente a busca novamente.")
                else:
                    st.error(f"Falha ao buscar a lei. Detalhe técnico: {e}")

# --- 4ª OPÇÃO: DICIONÁRIO COM CACHE ---
elif opcao_menu == "📔 Dicionário Jurídico e Latim":
    st.subheader("📔 Dicionário Jurídico e Expressões em Latim")
    st.write("Digite um termo técnico ou expressão em latim para obter a tradução e o significado aplicado ao Direito.")

    termo_busca = st.text_input("Qual termo você deseja consultar?", placeholder="Ex: Erga omnes, Vacatio Legis...")
    btn_dicionario = st.button("🔍 Consultar Termo")

    if btn_dicionario and termo_busca:
        with st.spinner(f"Buscando o significado de '{termo_busca}'..."):
            try:
                resultado = consultar_dicionario_cache(termo_busca.strip().lower())
                st.markdown("---")
                st.markdown(resultado)
                
                # Áudio
                audio_bytes = gerar_audio_acessibilidade(resultado)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                    
                # Botão de Salvar
                st.download_button(
                    label="📥 Salvar Significado (.txt)",
                    data=resultado,
                    file_name="dicionario_juridico.txt",
                    mime="text/plain"
                )
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    st.warning("⚠️ Muitos estudantes consultando o dicionário agora! Aguarde 20 segundos e tente novamente.")
                else:
                    st.error(f"Erro ao buscar o termo. Detalhe técnico: {e}")
