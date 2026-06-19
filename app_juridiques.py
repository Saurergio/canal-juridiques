"""
Projeto: Canal Juridiquês
Versão: 1.0.19
Descrição: Persistência de estado (Correção do botão que some) e botão genérico de Compartilhar.
Autoria: Sergio Moreira Neri
"""
import os
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
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets.")
    st.stop()

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
                # Prompt BISO: Injetamos as diretrizes estritas de diagramação e formatação
                prompt_tcc = f"""
Atue como um orientador acadêmico de Direito. Gere a estrutura de tópicos científicos para um TCC com o tema: '{tema_usuario}'.

DIRETRIZES DE FORMATAÇÃO ESTRITA (MARKDOWN):
1. Pule SEMPRE duas linhas entre os capítulos principais (I, II, III...) para criar respiro visual.
2. Use negrito (**texto**) exclusivamente nos títulos e subtítulos.
3. Utilize obrigatoriamente marcadores de lista (bullet points) ou numeração recuada para os itens e subitens.
4. Não gere blocos de texto contínuos. A diagramação deve ser hierárquica, espaçada e focada na legibilidade do aluno.
"""
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt_tcc, 
                    config=types.GenerateContentConfig(temperature=0.4)
                )
                
                if not response.text:
                    raise ValueError("A IA retornou um objeto vazio.")

                # Trava de Performance: Salvamos o texto, mas deixamos o áudio como nulo (None)
                st.session_state.metodologia = {"tema": tema_usuario, "texto": response.text, "audio": None}
                
            except Exception as e:
                # Erro detalhado para facilitar troubleshooting futuro
                st.error(f"Erro na comunicação. Detalhe técnico: {e}")

    # Exibe o resultado gravado na memória
    if st.session_state.metodologia:
        st.markdown("---")
        st.write(st.session_state.metodologia["texto"])
        
        # --- NOVO FLUXO DE ÁUDIO SOB DEMANDA ---
        if st.session_state.metodologia["audio"]:
            st.audio(st.session_state.metodologia["audio"], format="audio/mp3")
        else:
            # Botão com key única para não conflitar com a aba de Legislação
            if st.button("🔊 Gerar Áudio da Estrutura", key="btn_gerar_audio_met"):
                with st.spinner("Processando áudio..."):
                    novo_audio = gerar_audio_acessibilidade(st.session_state.metodologia["texto"])
                    st.session_state.metodologia["audio"] = novo_audio
                    st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            # Correção proativa: adicionado str() para evitar erro de tipagem
            st.download_button("📥 Salvar (.txt)", str(st.session_state.metodologia["texto"]), file_name=limpar_nome_arquivo(st.session_state.metodologia["tema"]), key="dl_met")
        with col2:
            # Correção proativa: adicionado str() para evitar erro de tipagem no link
            st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(str(st.session_state.metodologia['texto']))}")

# --- 3ª OPÇÃO: LEGISLAÇÃO ---
elif opcao_menu == "📜 Consulta à Legislação e Letra da Lei":
    st.subheader("📜 Extrator da Letra da Lei")
    if 'legislacao' not in st.session_state: st.session_state.legislacao = None

    if pedido_lei := st.chat_input("Ex: Artigo 5 da CF, Lei da LGPD..."):
        with st.spinner("Buscando texto oficial..."):
            try:
                # O bloco try exige que tudo abaixo dele tenha 4 espaços a mais (um recuo extra)
                prompt_legislacao = f"""
Atue como um curador jurídico do Canal Juridiquês. O aluno deseja consultar a seguinte norma: '{pedido_lei}'.

Para garantir a precisão absoluta da fonte, siga estritamente esta estrutura:

1. SÍNTESE DA NORMA: Escreva um resumo objetivo e didático (com suas próprias palavras, entre 2 e 3 parágrafos) explicando do que se trata essa norma, artigo ou inciso, e qual é o seu principal impacto jurídico.
2. FONTE OFICIAL: Indique como o aluno pode encontrar o texto na íntegra. IMPORTANTE: Só forneça URLs diretas (links) se você tiver 100% de certeza de que são hiperlinks reais e funcionais dos portais Planalto, Senado ou LexML. Se houver qualquer dúvida, forneça apenas a instrução de busca (Ex: "Pesquise por 'Lei 13.709/2018 Planalto' no Google").

TRAVAS DE SEGURANÇA (ANTI-ALUCINAÇÃO) - REGRA ABSOLUTA:
- O ecossistema jurídico não tolera invenções. Você está TERMINANTEMENTE PROIBIDO de criar leis falsas, inventar números de artigos ou associar conceitos incorretos a uma norma.
- Se o usuário pedir uma norma que não existe (ex: "Artigo 900 da CF"), uma lei obscura, ou se sua confiança no dado for baixa, NÃO TENTE ADIVINHAR. Interrompa a geração do resumo e responda APENAS: "⚠️ Para garantir sua segurança jurídica, informo que não possuo dados com o nível de precisão exigido para sintetizar esta norma específica. Recomendo a busca direta no portal oficial do Planalto ou LexML."

DIRETRIZES DE FORMATAÇÃO (MARKDOWN PURO):
- Use negrito para dar destaque a termos jurídicos importantes.
- Proibido o uso de tags HTML (como <br>).
"""
                response = client.models.generate_content(
                    model='gemini-2.5-flash', 
                    contents=prompt_legislacao, 
                    config=types.GenerateContentConfig(temperature=0.1)
                )
                
                # MODO AUDITORIA: Capturando o real motivo do bloqueio da API
                if not response.text:
                    motivo = "Desconhecido"
                    if response.candidates:
                        motivo = response.candidates[0].finish_reason
                    raise ValueError(f"A API do Google bloqueou a resposta. Motivo interno (Finish Reason): {motivo}")
                st.session_state.legislacao = {"pedido": pedido_lei, "texto": response.text, "audio": None}
                
            except Exception as e:
                st.error(f"Falha ao processar a requisição. Detalhe técnico: {e}")    # Exibe o resultado gravado na memória
    if st.session_state.legislacao:
        with st.chat_message("user"): st.markdown(st.session_state.legislacao["pedido"])
        with st.chat_message("assistant"):
            st.write(st.session_state.legislacao["texto"])
            
            # --- NOVO FLUXO DE ÁUDIO SOB DEMANDA ---
            if st.session_state.legislacao["audio"]:
                # Se o áudio já existe na memória, apenas exibe o player
                st.audio(st.session_state.legislacao["audio"], format="audio/mp3")
            else:
                # Se não existe, cria um botão para gerar
                if st.button("🔊 Gerar Áudio de Acessibilidade", key="btn_gerar_audio"):
                    with st.spinner("Processando áudio..."):
                        # Só chama a função pesada se o usuário clicar
                        novo_audio = gerar_audio_acessibilidade(st.session_state.legislacao["texto"])
                        st.session_state.legislacao["audio"] = novo_audio
                        st.rerun() # Atualiza a interface instantaneamente para trocar o botão pelo player

            # Botões de utilidade
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 Salvar (.txt)", str(st.session_state.legislacao["texto"]), file_name=limpar_nome_arquivo(st.session_state.legislacao["pedido"]), key="dl_leg")
            with col2:
                st.link_button("📤 Compartilhar", f"https://api.whatsapp.com/send?text={urllib.parse.quote(str(st.session_state.legislacao['texto']))}")

# --- FUNÇÃO DO DICIONÁRIO (A PEÇA QUE FALTAVA) ---
@st.cache_data(ttl=86400, show_spinner=False)
def consultar_dicionario_cache(termo):
    PROMPT = f"Você é um Dicionário Jurídico dinâmico do Canal Juridiquês. Explique de forma objetiva o termo: '{termo}'. Se for latim, traduza. Use máximo dois parágrafos."
    resposta = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=PROMPT, 
        config=types.GenerateContentConfig(temperature=0.3)
    )
    return resposta.text

# --- 4ª OPÇÃO: DICIONÁRIO ---
# --- 4ª OPÇÃO: DICIONÁRIO ---
elif opcao_menu == "📔 Dicionário Jurídico e Latim":
    st.subheader("📔 Dicionário Jurídico e Latim")
    if 'dicionario' not in st.session_state: st.session_state.dicionario = None

    if termo_busca := st.chat_input("Ex: Erga omnes..."):
        with st.spinner("Buscando..."):
            try:
                resultado = consultar_dicionario_cache(termo_busca.strip().lower())
                
                # Desativando o áudio temporariamente para testar o bloqueio de IP
                # audio = gerar_audio_acessibilidade(resultado)
                audio = None 
                
                st.session_state.dicionario = {"termo": termo_busca, "texto": resultado, "audio": audio}
            except Exception as e:
                st.error(f"Erro ao buscar o termo. Detalhe técnico: {e}")

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
