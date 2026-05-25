"""
Projeto: Canal Juridiquês
Versão: 1.1.2
Descrição: Ecossistema inteligente com utilitários (Vade Mecum e Dicionário) centralizados na tela principal.
Autoria: Sergio Moreira Neri
"""

import streamlit as st
from google import genai
from google.genai import types
import os

# Configuração da página web (Otimizada para Mobile e Computador)
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# 1. ESTILIZAÇÃO CUSTOMIZADA (CSS Responsivo + Configuração de Impressão)
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Ajuste da Barra Lateral para todos os tamanhos de tela */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid #c5a059;
    }

    /* Botões grandes, confortáveis e fáceis de tocar no celular */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        background-color: #c5a059;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 12px 20px;
        width: 100%;
        font-size: 16px;
        transition: 0.3s;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        background-color: #a38446;
        color: white;
    }
    
    /* Ajuste da caixa de seleção para dar destaque */
    div[data-baseweb="select"] {
        border: 1px solid #c5a059;
        border-radius: 8px;
    }

    /* Caixas de chat adaptáveis */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        background-color: #1e2430;
        margin-bottom: 12px;
        padding: 14px;
    }

    /* REGRAS DE IMPRESSÃO NATIIVA DO NAVEGADOR */
    @media print {
        [data-testid="stSidebar"], 
        header, 
        footer, 
        .stActionButton,
        div.stButton,
        div.stDownloadButton,
        div.row-widget,
        div[data-testid="stSelectbox"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

NOME_LOGO = "logo.png"

# MENU LATERAL (Apenas Identidade e Contato)
with st.sidebar:
    if os.path.exists(NOME_LOGO):
        st.image(NOME_LOGO, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #c5a059;'>⚖️</h1>", unsafe_allow_html=True)
        
    st.markdown("<h3 style='text-align: center;'>Canal Juridiquês</h3>", unsafe_allow_html=True)
    st.markdown("---")
    st.header("📬 Fale Conosco")
    st.write("Dúvidas, sugestões ou problemas?")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

# --- RECURSOS DE APOIO CENTRALIZADOS NA TELA PRINCIPAL ---
col_vade, col_dict = st.columns(2)

with col_vade:
    with st.expander("📙 Vade Mecum Atualizado"):
        st.write("Consulte a legislação com o material recomendado por nossos parceiros:")
        st.link_button("👉 Ver na Amazon Brasil", "https://www.amazon.com.br/s?k=vade+mecum&i=books")

with col_dict:
    with st.expander("🔍 Dicionário de Latim"):
        st.markdown("**In dubio pro reo:** Na dúvida, a decisão favorece o réu.")
        st.markdown("**Jus Puniendi:** O direito de punir do Estado.")
        st.markdown("**Vacatio Legis:** Prazo até a lei entrar em vigor.")
        st.markdown("**Mens Legis:** A intenção/espírito da lei.")
        st.markdown("**Pacta sunt servanda:** Contratos devem ser cumpridos.")

st.markdown("---")

# NAVEGAÇÃO PRINCIPAL
opcao_menu = st.selectbox(
    "Escolha a ferramenta que deseja utilizar:",
    [
        "💬 Tutor de Inteligência Artificial", 
        "📖 Guia de Metodologia de Pesquisa",
        "📝 Gerador de Simulados Acadêmicos"
    ]
)

st.markdown("<br>", unsafe_allow_html=True)

# Inicialização da API do Gemini
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets.")
    st.stop()


# 1ª OPÇÃO: TUTOR DE IA
if opcao_menu == "💬 Tutor de Inteligência Artificial":
    PROMPT_TUTOR = (
        "Você é o 'Tutor Jurídico Acadêmico' do portal Canal Juridiquês. Seu papel é ajudar estudantes de Direito.\n"
        "Ao explicar conceitos, divida em: 1) Conceito Puro (simples e traduzindo latim); 2) Exemplo Prático moderno; 3) Fundamentação legal ou doutrinária básica."
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
            except Exception as e:
                st.error(f"Erro na requisição: {e}")


# 2ª OPÇÃO: GUIA DE METODOLOGIA
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    st.warning("⚠️ **Diretriz Ética:** Esta ferramenta funciona exclusivamente como um guia estrutural. A IA não redigirá o conteúdo do seu trabalho.")
    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:", placeholder="Ex: A eficácia da LGPD na segurança pública")
    botao_gerar = st.button("🚀 Gerar Estrutura Acadêmica")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = (
            f"Você é um orientador acadêmico especialista em metodologia jurídica. Analise o tema: '{tema_usuario}'.\n"
            f"Gere em tópicos: a) Formato; b) Título; c) Problema de Pesquisa; d) Objetivos; e) Sumário estrutural sugerido. Proibido escrever textos longos."
        )
        with st.spinner("Mapeando a estrutura ideal..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_METODOLOGIA,
                    config=types.GenerateContentConfig(temperature=0.4)
                )
                st.markdown("---")
                st.markdown("### 📋 Proposta Estrutural Obtida")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro ao processar a estrutura: {e}")


# 3ª OPÇÃO: GERADOR DE SIMULADOS ACADÊMICOS
elif opcao_menu == "📝 Gerador de Simulados Acadêmicos":
    st.subheader("📝 Gerador de Simulados e Questões de Fixação")
    st.write("Monte um caderno de questões personalizado para testar seus conhecimentos.")

    col1, col2, col3 = st.columns(3)
    with col1:
        materia = st.selectbox("Selecione a Matéria:", ["Teoria Geral do Direito", "Introdução ao Estudo do Direito", "Sociologia Jurídica", "Direito Romano"])
    with col2:
        qtd_questoes = st.slider("Quantidade:", min_value=1, max_value=5, value=3)
    with col3:
        tipo_questao = st.selectbox("Tipo de Questões:", ["Múltipla Escolha", "Dissertativa", "Mesclada"])

    btn_simulado = st.button("🎯 Gerar Caderno de Questões")

    if btn_simulado:
        PROMPT_SIMULADO = (
            f"Gere um caderno contendo exatamente {qtd_questoes} questões de nível universitário sobre a matéria: '{materia}'.\n"
            f"O tipo de questão deve ser: {tipo_questao}.\n\n"
            f"REGRAS DE FORMATO:\n"
            f"Use a hashtag '### 📝 CADERNO DE QUESTÕES' para as perguntas.\n"
            f"Use a hashtag '### 🔑 GABARITO COMENTADO OFICIAL' no final para as respostas.\n"
            f"Se for Múltipla Escolha, coloque 4 alternativas (A, B, C, D)."
        )

        with st.spinner("Elaborando questões inéditas..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_SIMULADO,
                    config=types.GenerateContentConfig(temperature=0.6)
                )
                st.session_state.resultado_simulado = response.text
            except Exception as e:
                st.error(f"Erro ao gerar o simulado: {e}")

    if "resultado_simulado" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.resultado_simulado)
        
        st.markdown("---")
        st.subheader("📥 Opções de Exportação Segura")
        
        st.download_button(
            label="📥 Baixar Caderno de Questões (Arquivo .txt)",
            data=st.session_state.resultado_simulado,
            file_name=f"simulado_{materia.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )
        
        st.info(
            "💡 **Dica de Impressão ou PDF:** Você também pode salvar este simulado com layout limpo usando o atalho de impressão do seu próprio navegador "
            "(**Ctrl + P** no computador, ou a opção **'Compartilhar > Imprimir'** no menu do seu navegador de celular). "
            "Nosso sistema vai esconder automaticamente todos os botões e menus, deixando apenas as perguntas prontas para salvar como PDF ou imprimir!"
        )