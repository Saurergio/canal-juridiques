"""
Projeto: Canal Juridiquês
Versão: 1.1.0
Descrição: Ecossistema acadêmico inteligente com Tutor de IA, Guia de Metodologia e Gerador de Simulados.
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

    /* REGRAS DE IMPRESSÃO: Esconde menus para gerar um PDF limpo se o usuário mandar imprimir a página */
    @media print {
        [data-testid="stSidebar"], 
        header, 
        footer, 
        .stActionButton,
        div.stButton {
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

# MENU LATERAL
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
    
    st.header("📬 Fale Conosco")
    st.write("Dúvidas, sugestões ou problemas?")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

# NAVEGAÇÃO PRINCIPAL (Agora com 3 opções)
opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
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
        "Você é o 'Tutor Jurídico Acadêmico' do portal Canal Juridiquês. Seu papel é auxiliar estudantes de graduação em Direito. "
        "Adote uma postura didática, acolhedora e altamente profissional. "
        "Ao explicar conceitos, especialmente de matérias propedêuticas (Introdução ao Estudo do Direito, Teoria Geral do Direito, "
        "Sociologia Jurídica, Filosofia e Direito Romano), quebre a resposta em três partes logicamente separadas:\n"
        "1) Conceito Puro (explicado de forma simples e direta, traduzindo termos em latim se houver);\n"
        "2) Exemplo Prático ou Analogia com o cotidiano moderno;\n"
        "3) Fundamentação (mencionando brevemente a doutrina tradicional ou a lei relevante).\n"
        "Use formatação Markdown com negritos e listas para leitura rápida no celular."
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


# 2ª OPÇÃO: GUIA DE METODOLOGIA (Protegido contra plágio)
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    st.warning(
        "⚠️ **Diretriz Ética e de Integridade Acadêmica:**\n\n"
        "Esta ferramenta funciona exclusivamente como um **guia de orientação e estrutura conceitual**. "
        "A IA **não redigirá** o conteúdo do seu trabalho."
    )
    tema_usuario = st.text_input("Digite a ideia central ou o tema do seu trabalho:", placeholder="Ex: A eficácia da LGPD na segurança pública")
    botao_gerar = st.button("🚀 Gerar Estrutura Acadêmica")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = (
            f"Você é um orientador acadêmico especialista em metodologia científica jurídica. Analise o tema: '{tema_usuario}'.\n"
            f"Gere estritamente em tópicos: a) Formato Ideal; b) Título Sugerido; c) Problema de Pesquisa; d) Três Objetivos Específicos; e) Sumário estrutural sugerido. Proibido escrever textos longos."
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


# 3ª OPÇÃO: GERADOR DE SIMULADOS ACADÊMICOS (Nova Ferramenta Interativa)
elif opcao_menu == "📝 Gerador de Simulados Acadêmicos":
    st.subheader("📝 Gerador de Simulados e Questões de Fixação")
    st.write("Monte um caderno de questões personalizado para testar seus conhecimentos ou gerar material para revisão impresso.")

    # Opções do Simulado agrupadas de forma elegante
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
            f"Você é um renomado Professor e Coordenador de Exames Acadêmicos de Direito. "
            f"Gere um caderno contendo exatamente {qtd_questoes} questões de nível universitário sobre a matéria: '{materia}'.\n"
            f"O tipo de questão deve ser: {tipo_questao}.\n\n"
            f"REGRAS DE FORMATO RIGOROSAS:\n"
            f"1. Divida sua resposta em duas grandes seções perfeitamente identificáveis:\n"
            f"   Use a hashtag '### 📝 CADERNO DE QUESTÕES' para listar as perguntas.\n"
            f"   Use a hashtag '### 🔑 GABARITO COMENTADO OFICIAL' no final da resposta para colocar as respostas.\n"
            f"2. Se for Múltipla Escolha, coloque 4 alternativas (A, B, C, D).\n"
            f"3. Se for Dissertativa, inclua um pequeno critério de correção esperado no gabarito.\n"
            f"4. Faça enunciados ricos, baseados em casos hipotéticos ou debates doutrinários modernos (Ex: vigência vs eficácia, positivismo vs jusnaturalismo).\n\n"
            f"Mantenha um alto rigor acadêmico."
        )

        with st.spinner("Elaborando questões inéditas e estruturando gabarito..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_SIMULADO,
                    config=types.GenerateContentConfig(temperature=0.6)
                )
                
                # Salva o resultado no estado da sessão para não sumir ao clicar em outros botões
                st.session_state.resultado_simulado = response.text
            except Exception as e:
                st.error(f"Erro ao gerar o simulado: {e}")

    # Se o simulado já foi gerado, exibe na tela com os recursos adicionais
    if "resultado_simulado" in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state.resultado_simulado)
        
        st.markdown("---")
        st.subheader("🖨️ Opções de Exportação")
        st.write("Use o botão abaixo para abrir a tela de impressão. Você pode selecionar a opção **'Salvar como PDF'** nas configurações da sua impressora para guardar o arquivo digitalmente.")
        
        # Botão JavaScript que aciona a impressão nativa do dispositivo (Mobile ou Desktop)
        st.markdown(
            '<button onclick="window.print()" style="background-color: #c5a059; color: white; border-radius: 10px; border: none; padding: 12px 20px; width: 100%; font-size: 16px; cursor: pointer;">'
            '🖨️ Imprimir ou Salvar Simulado como PDF'
            '</button>',
            unsafe_allow_html=True
        )