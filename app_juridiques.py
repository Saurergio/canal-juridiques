"""
Projeto: Canal Juridiquês
Versão: 1.0.22
Descrição: Higienização de sintaxe, substituição de st.stop() por lógica de controle
fluida (UX), e desacoplamento do cliente Gemini no cache do Streamlit.
Autoria: Sergio Moreira Neri
"""

import base64
import io
import json
import os
import re
import urllib.parse

import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS


# =========================================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Canal Juridiquês",
    page_icon="⚖️",
    layout="centered"
)


# =========================================================
# CONSTANTES
# =========================================================
NOME_LOGO = "logo.png"
NOME_ICONE_PWA = "icon192.png"
MODELO_GEMINI = "gemini-2.5-flash"

MENU_TUTOR = "💬 Tutor de Inteligência Artificial"
MENU_METODOLOGIA = "📖 Guia de Metodologia de Pesquisa"
MENU_LEGISLACAO = "📜 Consulta à Legislação e Síntese Orientativa"
MENU_DICIONARIO = "📔 Dicionário Jurídico e Latim"


# =========================================================
# UTILITÁRIOS GERAIS
# =========================================================
def get_base64_of_bin_file(bin_file: str) -> str | None:
    """Converte arquivo binário local para base64. Retorna None se o arquivo não existir."""
    try:
        with open(bin_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode("utf-8")
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Erro ao converter arquivo para base64: {e}")
        return None


def inicializar_pwa() -> None:
    """Injeta ícone e manifesto PWA quando o arquivo icon192.png estiver disponível."""
    logo_base64 = get_base64_of_bin_file(NOME_ICONE_PWA)
    if not logo_base64:
        return

    st.markdown(
        f'<link rel="apple-touch-icon" href="data:image/png;base64,{logo_base64}">',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<link rel="icon" type="image/png" sizes="192x192" href="data:image/png;base64,{logo_base64}">',
        unsafe_allow_html=True,
    )

    manifest = {
        "name": "Canal Juridiquês",
        "short_name": "Juridiquês",
        "start_url": "./",
        "display": "standalone",
        "background_color": "#0e1117",
        "theme_color": "#c5a059",
        "description": "Seu ecossistema acadêmico inteligente com IA.",
        "icons": [
            {
                "src": f"data:image/png;base64,{logo_base64}",
                "sizes": "192x192",
                "type": "image/png",
            }
        ],
    }

    manifest_b64 = base64.b64encode(json.dumps(manifest).encode("utf-8")).decode("utf-8")
    st.markdown(
        f'<link rel="manifest" href="data:application/manifest+json;base64,{manifest_b64}">',
        unsafe_allow_html=True,
    )


def limpar_nome_arquivo(texto: str | None) -> str:
    """Gera um nome seguro e previsível para arquivos de download."""
    if not texto:
        return "pesquisa_juridica.txt"

    texto = texto.lower().strip()
    texto = re.sub(r"[^\w\s-]", "", texto)
    palavras = texto.split()[:4]

    if not palavras:
        return "pesquisa_juridica.txt"

    return "pesquisa_" + "_".join(palavras) + ".txt"


def gerar_audio_acessibilidade(texto: str, mostrar_erro: bool = False) -> bytes | None:
    """
    Gera áudio em português brasileiro usando gTTS.
    Retorna None em caso de falha para não interromper o app.
    """
    if not texto or not texto.strip():
        return None

    try:
        tts = gTTS(text=texto, lang="pt", tld="com.br", slow=False)
        arquivo_em_memoria = io.BytesIO()
        tts.write_to_fp(arquivo_em_memoria)
        return arquivo_em_memoria.getvalue()
    except Exception as e:
        print(f"Erro no gTTS: {e}")
        if mostrar_erro:
            st.warning("Não foi possível gerar o áudio neste momento. Tente novamente mais tarde.")
        return None


def texto_para_whatsapp(texto: str) -> str:
    """Codifica texto para compartilhamento no WhatsApp."""
    return urllib.parse.quote(texto or "")


# =========================================================
# CONFIGURAÇÃO DA API GEMINI
# =========================================================
def obter_api_key() -> str | None:
    """Obtém a chave da API por variável de ambiente ou Streamlit Secrets."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    try:
        key = st.secrets.get("GEMINI_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return None


@st.cache_resource(show_spinner=False)
def carregar_cliente_gemini(api_key: str) -> genai.Client:
    """Cria e reutiliza o cliente Gemini durante a sessão do Streamlit."""
    return genai.Client(api_key=api_key)


GEMINI_API_KEY = obter_api_key()

if not GEMINI_API_KEY:
    st.error(
        "Erro: a chave GEMINI_API_KEY não foi encontrada. "
        "Configure-a em Variable Environments, Secrets do Streamlit ou variável de ambiente."
    )
    st.stop()

client = carregar_cliente_gemini(GEMINI_API_KEY)


# =========================================================
# FUNÇÃO GLOBAL DO DICIONÁRIO COM CACHE
# =========================================================
@st.cache_data(ttl=86400, max_entries=500, show_spinner=False)
def consultar_dicionario_cache(termo: str, _client_api) -> str:
    """
    Consulta termo jurídico/latim e mantém cache por 24h.
    O _client_api com underscore informa ao Streamlit para ignorá-lo no hash do cache.
    """
    termo = termo.strip().lower()

    prompt = f"""
Você é o Dicionário Jurídico dinâmico do Canal Juridiquês.
Explique de forma objetiva o termo: "{termo}".

Regras:
- Se for uma expressão em latim, traduza e explique o sentido jurídico.
- Use linguagem clara para estudantes iniciantes de Direito.
- Use no máximo dois parágrafos.
- Se o termo for ambíguo, explique os sentidos principais sem inventar fontes.
"""

    resposta = _client_api.models.generate_content(
        model=MODELO_GEMINI,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.3),
    )

    if not resposta.text:
        raise ValueError("A IA retornou uma resposta vazia.")

    return resposta.text


# =========================================================
# PWA E ESTILO VISUAL
# =========================================================
inicializar_pwa()

st.markdown(
    """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
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
        padding: 12px 20px;
        width: 100%;
        font-size: 16px;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #a38446;
        color: white;
    }
    div[data-baseweb="select"] {
        border: 1px solid #c5a059;
        border-radius: 8px;
    }
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        background-color: #1e2430;
        margin-bottom: 12px;
        padding: 14px;
        color: #FAFAFA;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# MENU LATERAL
# =========================================================
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True, output_format="PNG")
    else:
        st.markdown(
            "<h1 style='text-align: center; color: #c5a059;'>⚖️</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='text-align: center; color: #c5a059;'>Canal Juridiquês</h3>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.header("📚 Indicações")
    st.write("Apoie o nosso projeto gratuito utilizando links dos nossos parceiros!")
    st.markdown("### 📙 Vade Mecum Atualizado")
    st.link_button(
        "👉 Ver na Amazon Brasil",
        "https://www.amazon.com.br/s?k=vade+mecum&i=books",
    )

    st.markdown("---")
    st.header("📬 Fale Conosco")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")


# =========================================================
# CABEÇALHO PRINCIPAL
# =========================================================
st.markdown(
    "<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>",
    unsafe_allow_html=True,
)
st.markdown("---")

opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
    [MENU_TUTOR, MENU_METODOLOGIA, MENU_LEGISLACAO, MENU_DICIONARIO],
)
st.markdown("<br>", unsafe_allow_html=True)


# =========================================================
# 1ª OPÇÃO: TUTOR IA
# =========================================================
if opcao_menu == MENU_TUTOR:
    st.subheader("💬 Tutor Jurídico Acadêmico")

    PROMPT_TUTOR = """
Você é o Tutor Jurídico Acadêmico do Canal Juridiquês.
Explique para estudantes iniciantes de Direito.

Estruture sempre em Markdown:
1. **Conceito Puro**
2. **Exemplo Prático**
3. **Fundamentação**

Regras:
- Seja didático, claro e objetivo.
- Quando houver risco de imprecisão jurídica, oriente o aluno a conferir a norma atualizada em fonte oficial.
- Não invente artigos, leis, autores ou jurisprudência.
"""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.session_state.messages:
        if st.button("🧹 Limpar conversa", key="limpar_tutor"):
            st.session_state.messages = []
            st.rerun()

    # Renderiza histórico e botões associados às respostas do assistente.
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            if msg["role"] == "assistant":
                if msg.get("audio"):
                    st.audio(msg["audio"], format="audio/mp3")
                else:
                    if st.button("🔊 Gerar Áudio", key=f"audio_tutor_{i}"):
                        audio = gerar_audio_acessibilidade(msg["content"], mostrar_erro=True)
                        if audio:
                            st.session_state.messages[i]["audio"] = audio
                            st.rerun()

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Salvar (.txt)",
                        msg["content"],
                        file_name=limpar_nome_arquivo(msg.get("prompt", "resposta")),
                        key=f"dl_tutor_{i}",
                    )
                with col2:
                    texto_zap = (
                        f"*Canal Juridiquês*\n\n"
                        f"*Pergunta:* {msg.get('prompt', '')}\n\n"
                        f"*Resposta:* {msg['content']}"
                    )
                    st.link_button(
                        "📤 Compartilhar",
                        f"https://api.whatsapp.com/send?text={texto_para_whatsapp(texto_zap)}",
                        key=f"zap_tutor_{i}",
                    )

    if prompt_usuario := st.chat_input("Digite sua dúvida jurídica aqui..."):
        prompt_usuario = prompt_usuario.strip()

        if not prompt_usuario:
            st.warning("Por favor, digite uma dúvida válida antes de enviar.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt_usuario})

            with st.chat_message("user"):
                st.markdown(prompt_usuario)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""

                try:
                    historico_api = [
                        types.Content(
                            role="user" if m["role"] == "user" else "model",
                            parts=[types.Part.from_text(text=m["content"])],
                        )
                        for m in st.session_state.messages[:-1]
                    ]

                    response_stream = client.models.generate_content_stream(
                        model=MODELO_GEMINI,
                        contents=[
                            *historico_api,
                            types.Content(
                                role="user",
                                parts=[types.Part.from_text(text=prompt_usuario)],
                            ),
                        ],
                        config=types.GenerateContentConfig(
                            system_instruction=PROMPT_TUTOR,
                            temperature=0.6,
                        ),
                    )

                    for chunk in response_stream:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")

                    if not full_response.strip():
                        raise ValueError("A IA retornou uma resposta vazia.")

                    message_placeholder.markdown(full_response)

                    # Áudio fica sob demanda para evitar lentidão e bloqueios de IP no deploy.
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response,
                            "audio": None,
                            "prompt": prompt_usuario,
                        }
                    )
                    st.rerun()

                except Exception as e:
                    st.error(f"⚠️ Erro ao gerar resposta: {e}")


# =========================================================
# 2ª OPÇÃO: METODOLOGIA
# =========================================================
elif opcao_menu == MENU_METODOLOGIA:
    st.subheader("📖 Assistente de Projetos Científicos")

    if "metodologia" not in st.session_state:
        st.session_state.metodologia = None

    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:")

    if st.button("🚀 Gerar Estrutura"):
        tema_usuario = tema_usuario.strip()

        if not tema_usuario:
            st.warning("Por favor, digite um tema válido antes de prosseguir.")
        else:
            with st.spinner("Analisando o tema..."):
                try:
                    prompt_tcc = f"""
Atue como um orientador acadêmico de Direito.
Gere uma estrutura de tópicos científicos para um TCC com o tema: "{tema_usuario}".

DIRETRIZES DE FORMATAÇÃO ESTRITA EM MARKDOWN:
1. Pule sempre duas linhas entre os capítulos principais para criar respiro visual.
2. Use negrito exclusivamente nos títulos e subtítulos.
3. Utilize obrigatoriamente marcadores de lista ou numeração recuada para itens e subitens.
4. Não gere blocos longos de texto contínuo.
5. A diagramação deve ser hierárquica, espaçada e focada na legibilidade do aluno.

Inclua, quando fizer sentido:
- Problema de pesquisa.
- Hipótese.
- Objetivo geral.
- Objetivos específicos.
- Justificativa.
- Possível estrutura de capítulos.
- Sugestões iniciais de fontes normativas, doutrinárias ou jurisprudenciais, sem inventar referências.
"""

                    response = client.models.generate_content(
                        model=MODELO_GEMINI,
                        contents=prompt_tcc,
                        config=types.GenerateContentConfig(temperature=0.4),
                    )

                    if not response.text:
                        raise ValueError("A IA retornou uma resposta vazia.")

                    st.session_state.metodologia = {
                        "tema": tema_usuario,
                        "texto": response.text,
                        "audio": None,
                    }

                except Exception as e:
                    st.error(f"Erro na comunicação. Detalhe técnico: {e}")

    if st.session_state.metodologia:
        st.markdown("---")
        st.markdown(st.session_state.metodologia["texto"])

        if st.session_state.metodologia["audio"]:
            st.audio(st.session_state.metodologia["audio"], format="audio/mp3")
        else:
            if st.button("🔊 Gerar Áudio da Estrutura", key="btn_gerar_audio_met"):
                with st.spinner("Processando áudio..."):
                    novo_audio = gerar_audio_acessibilidade(
                        st.session_state.metodologia["texto"],
                        mostrar_erro=True,
                    )
                    if novo_audio:
                        st.session_state.metodologia["audio"] = novo_audio
                        st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📥 Salvar (.txt)",
                str(st.session_state.metodologia["texto"]),
                file_name=limpar_nome_arquivo(st.session_state.metodologia["tema"]),
                key="dl_met",
            )
        with col2:
            st.link_button(
                "📤 Compartilhar",
                f"https://api.whatsapp.com/send?text={texto_para_whatsapp(str(st.session_state.metodologia['texto']))}",
                key="zap_met",
            )


# =========================================================
# 3ª OPÇÃO: LEGISLAÇÃO
# =========================================================
elif opcao_menu == MENU_LEGISLACAO:
    st.subheader("📜 Consulta à Legislação e Síntese Orientativa")
    st.info(
        "Esta ferramenta oferece uma síntese educacional. "
        "Para trabalhos acadêmicos, petições ou decisões práticas, confirme sempre o texto atualizado em fonte oficial."
    )

    if "legislacao" not in st.session_state:
        st.session_state.legislacao = None

    if pedido_lei := st.chat_input("Ex: Artigo 5º da CF, Lei 13.709/2018, Lei Berenice Piana..."):
        pedido_lei = pedido_lei.strip()

        if not pedido_lei:
            st.warning("Por favor, digite a norma ou tema legislativo que deseja consultar.")
        else:
            with st.spinner("Gerando síntese orientativa..."):
                try:
                    prompt_legislacao = f"""
Atue como um assistente jurídico educacional do Canal Juridiquês.
O aluno deseja uma orientação sobre a seguinte norma, artigo ou tema legislativo: "{pedido_lei}".

IMPORTANTE:
Você NÃO está acessando bases oficiais em tempo real.
Por isso, não prometa transcrição literal atualizada da lei e não invente links diretos.

Responda usando esta estrutura:

1. **Síntese didática**
Explique, em linguagem clara, do que trata a norma, artigo ou tema solicitado.
Use entre 2 e 3 parágrafos curtos.

2. **Atenção sobre precisão jurídica**
Informe que a resposta é educacional e que o aluno deve conferir a redação atualizada em fonte oficial.

3. **Como consultar a fonte oficial**
Oriente o aluno a pesquisar pelo número da lei, artigo ou termo nos seguintes portais oficiais ou institucionais:
- Portal da Legislação do Planalto;
- LexML;
- Senado Federal, quando for proposição legislativa.

TRAVAS DE SEGURANÇA JURÍDICA:
- Não invente leis, artigos, incisos, autores, jurisprudência ou URLs diretas.
- Não afirme que uma norma está vigente se não tiver segurança.
- Se o pedido for obscuro, inexistente ou impreciso, diga claramente que não há segurança suficiente para sintetizar a norma específica e recomende consulta direta em fonte oficial.
- Se houver ambiguidade, explique a ambiguidade e peça que o aluno confira o dado oficial.

FORMATAÇÃO:
- Use Markdown puro.
- Use negrito apenas para destaques importantes.
- Não use tags HTML.
"""

                    response = client.models.generate_content(
                        model=MODELO_GEMINI,
                        contents=prompt_legislacao,
                        config=types.GenerateContentConfig(temperature=0.1),
                    )

                    if not response.text:
                        motivo = "Desconhecido"
                        if response.candidates:
                            motivo = response.candidates[0].finish_reason
                        raise ValueError(
                            f"A API do Google retornou resposta vazia. Finish Reason: {motivo}"
                        )

                    st.session_state.legislacao = {
                        "pedido": pedido_lei,
                        "texto": response.text,
                        "audio": None,
                    }

                except Exception as e:
                    st.error(f"Falha ao processar a requisição. Detalhe técnico: {e}")

    if st.session_state.legislacao:
        with st.chat_message("user"):
            st.markdown(st.session_state.legislacao["pedido"])

        with st.chat_message("assistant"):
            st.markdown(st.session_state.legislacao["texto"])

            if st.session_state.legislacao["audio"]:
                st.audio(st.session_state.legislacao["audio"], format="audio/mp3")
            else:
                if st.button("🔊 Gerar Áudio de Acessibilidade", key="btn_gerar_audio_leg"):
                    with st.spinner("Processando áudio..."):
                        novo_audio = gerar_audio_acessibilidade(
                            st.session_state.legislacao["texto"],
                            mostrar_erro=True,
                        )
                        if novo_audio:
                            st.session_state.legislacao["audio"] = novo_audio
                            st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Salvar (.txt)",
                    str(st.session_state.legislacao["texto"]),
                    file_name=limpar_nome_arquivo(st.session_state.legislacao["pedido"]),
                    key="dl_leg",
                )
            with col2:
                texto_zap = (
                    f"*Canal Juridiquês - Síntese Legislativa*\n\n"
                    f"*Pedido:* {st.session_state.legislacao['pedido']}\n\n"
                    f"{st.session_state.legislacao['texto']}"
                )
                st.link_button(
                    "📤 Compartilhar",
                    f"https://api.whatsapp.com/send?text={texto_para_whatsapp(texto_zap)}",
                    key="zap_leg",
                )


# =========================================================
# 4ª OPÇÃO: DICIONÁRIO
# =========================================================
elif opcao_menu == MENU_DICIONARIO:
    st.subheader("📔 Dicionário Jurídico e Latim")

    if "dicionario" not in st.session_state:
        st.session_state.dicionario = None

    if termo_busca := st.chat_input("Ex: Erga omnes, vacatio legis, habeas corpus..."):
        termo = termo_busca.strip().lower()

        if not termo:
            st.warning("Por favor, digite um termo válido para pesquisar.")
        else:
            with st.spinner("Buscando..."):
                try:
                    # Passando a instância do client explicitamente
                    resultado = consultar_dicionario_cache(termo, client)

                    # Áudio sob demanda para reduzir lentidão e risco de bloqueio por IP no deploy.
                    st.session_state.dicionario = {
                        "termo": termo_busca.strip(),
                        "texto": resultado,
                        "audio": None,
                    }
                except Exception as e:
                    st.error(f"Erro ao buscar o termo. Detalhe técnico: {e}")

    if st.session_state.dicionario:
        with st.chat_message("user"):
            st.markdown(st.session_state.dicionario["termo"])

        with st.chat_message("assistant"):
            st.markdown(st.session_state.dicionario["texto"])

            if st.session_state.dicionario["audio"]:
                st.audio(st.session_state.dicionario["audio"], format="audio/mp3")
            else:
                if st.button("🔊 Gerar Áudio", key="btn_gerar_audio_dic"):
                    with st.spinner("Processando áudio..."):
                        novo_audio = gerar_audio_acessibilidade(
                            st.session_state.dicionario["texto"],
                            mostrar_erro=True,
                        )
                        if novo_audio:
                            st.session_state.dicionario["audio"] = novo_audio
                            st.rerun()

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Salvar (.txt)",
                    st.session_state.dicionario["texto"],
                    file_name=limpar_nome_arquivo(st.session_state.dicionario["termo"]),
                    key="dl_dic",
                )
            with col2:
                texto_zap = (
                    f"*Dicionário Jurídico*\n\n"
                    f"*Termo:* {st.session_state.dicionario['termo']}\n\n"
                    f"{st.session_state.dicionario['texto']}"
                )
                st.link_button(
                    "📤 Compartilhar",
                    f"https://api.whatsapp.com/send?text={texto_para_whatsapp(texto_zap)}",
                    key="zap_dic",
                )
