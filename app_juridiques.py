"""
Projeto: Canal Juridiquês
Versão: 1.0.8
Descrição: Ecossistema acadêmico com Dicionário Interativo, Limpeza Visual e Disclaimer de Boas-vindas.
Autoria: Sergio Moreira Neri
"""
import streamlit as st
from google import genai
from google.genai import types
import os

# Configuração da página web (Otimizada para Mobile e Computador)
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# 1. ESTILIZAÇÃO CUSTOMIZADA (CSS Totalmente Responsivo + Ocultação de Elementos)
st.markdown("""
    <style>
    /* Oculta o cabeçalho padrão do Streamlit (Share, GitHub, 3 pontinhos) */
    header {visibility: hidden;}
    
    /* Oculta o rodapé padrão "Made with Streamlit" */
    footer {visibility: hidden;}
    
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

    /* Caixas de chat adaptáveis com bom espaçamento para leitura */
    [data-testid="stChatMessage"] {
        border-radius: 15px;
        background-color: #1e2430;
        margin-bottom: 12px;
        padding: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

NOME_LOGO = "logo.png"

# MENU LATERAL (Com a propaganda do Vade Mecum)
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
    st.write("Dúvidas, sugestões ou problemas com a plataforma? Entre em contato conosco.")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

# --- NOVO: Disclaimer 100% Gratuito ---
st.info("""
Olá! O **Canal Juridiquês** é o seu assistente virtual **100% gratuito** criado para descomplicar a jornada do estudante de Direito. 
Nossa missão é apoiar seus estudos, esclarecer dúvidas e fortalecer o 
seu aprendizado acadêmico sem cobrar nada por isso.
""")
st.markdown("<br>", unsafe_allow_html=True)

# NAVEGAÇÃO OTIMIZADA PARA DISPOSITIVOS MÓVEIS
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

# Inicialização da API do Gemini de forma segura
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception:
    st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
    st.stop()

# 1ª OPÇÃO: O CHATBOT INTELIGENTE REFINADO
if opcao_menu == "💬 Tutor de Inteligência Artificial":
    
    PROMPT_TUTOR = (
        "Você é o 'Tutor Jurídico Acadêmico' do portal Canal Juridiquês. Seu papel é auxiliar estudantes de graduação em Direito. "
        "Adote uma postura didática, acolhedora e altamente profissional. "
        "Ao explicar conceitos, especialmente de matérias propedêuticas (Introdução ao Estudo do Direito, Teoria Geral do Direito, "
        "Sociologia Jurídica, Filosofia e Direito Romano), quebre a resposta em três partes logicamente separadas:\n"
        "1) Conceito Puro (explicado de forma simples e direta, traduzindo termos em latim se houver);\n"
        "2) Exemplo Prático ou Analogia com o cotidiano moderno;\n"
        "3) Fundamentação (mencionando brevemente a doutrina tradicional ou a lei relevante).\n"
        "Use formatação Markdown com negritos e listas para leitura rápida no celular. "
        "Sempre que sugerir leituras complementares, use o formato: [Compre na Amazon](https://www.amazon.com.br/s?k=NOME_DO_LIVRO&i=books)."
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
                    historico_api.append(types.Content(
                        role=role_api,
                        parts=[types.Part.from_text(text=m["content"])]
                    ))
                
                response_stream = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=[
                        *historico_api,
                        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_TUTOR,
                        temperature=0.6,
                    )
                )
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Erro na requisição: {e}")

# 2ª OPÇÃO: GUIA DE METODOLOGIA INTERATIVO
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    
    st.warning(
        "⚠️ **Diretriz Ética e de Integridade Acadêmica:**\n\n"
        "Esta ferramenta funciona exclusivamente como um **guia de orientação e estrutura conceitual**. "
        "A IA **não redigirá** o conteúdo do seu trabalho, evitando práticas que configurem plágio ou violação de direitos autorais."
    )
    
    st.write("Insira a ideia central do seu projeto para obter um esqueleto metodológico personalizado no padrão acadêmico correto.")
    
    tema_usuario = st.text_input(
        "Digite a ideia central ou o tema do seu trabalho:",
        placeholder="Ex: A eficácia da LGPD na segurança pública"
    )
    
    botao_gerar = st.button("🚀 Gerar Estrutura Acadêmica")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = (
            f"Você é um orientador acadêmico especialista em metodologia científica jurídica. "
            f"Analise o seguinte pedido do estudante: '{tema_usuario}'.\n\n"
            f"DIRETRIZES OBRIGATÓRIAS:\n"
            f"1. Identifique o formato solicitado pelo usuário (se ele mencionou artigo, TCC, monografia, etc.).\n"
            f"2. Você está RIGOROSAMENTE PROIBIDO de escrever textos longos, parágrafos de desenvolvimento ou conclusões prontas.\n"
            f"O QUE VOCÊ DEVE GERAR (De forma puramente estrutural e em tópicos):\n"
            f"a) Formato Identificado;\n"
            f"b) Sugestão de Título Refinado;\n"
            f"c) Problema de Pesquisa;\n"
            f"d) Três Objetivos Específicos;\n"
            f"e) Sumário Provisório Sugerido.\n"
        )
        
        with st.spinner("Analisando o tema e mapeando a estrutura ideal..."):
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
                
    elif botao_gerar and not tema_usuario:
        st.warning("Por favor, digite um tema ou comando antes de clicar em gerar.")

# 3ª OPÇÃO: CONSULTA DE LEGISLAÇÃO
elif opcao_menu == "📜 Consulta à Legislação e Letra da Lei":
    st.subheader("📜 Extrator da Letra da Lei")
    st.write("Consulte o texto exato de artigos de Leis, Códigos ou da Constituição Federal utilizando busca em tempo real.")

    pedido_lei = st.text_input(
        "Qual lei ou artigo específico você precisa consultar?",
        placeholder="Ex: Artigo 5 da CF / Lei da LGPD / Artigo 1 da LGPD"
    )

    botao_buscar = st.button("🔍 Buscar Texto Literal")

    if botao_buscar and pedido_lei:
        PROMPT_LEGISLACAO = (
            f"Você é o 'Consultor de Legislação Oficial' do Canal Juridiquês. Sua única missão é extrair e apresentar de forma clara "
            f"o texto literal da norma jurídica solicitada pelo usuário: '{pedido_lei}'.\n\n"
            f"INSTRUÇÕES DE EXECUÇÃO:\n"
            f"1. Você tem acesso à ferramenta de busca do Google. Utilize-a para encontrar o texto exato diretamente em fontes confiáveis (como os portais do Planalto, Senado ou sites institucionais).\n"
            f"2. Identifique claramente o nome oficial e o número da norma no topo.\n"
            f"3. Transcreva fielmente o caput, parágrafos ou incisos solicitados pelo usuário utilizando blocos de citação do Markdown para leitura rápida no celular.\n"
            f"4. Não faça análises ou comentários longos. O foco absoluto é entregar o texto seco da lei de forma rápida e precisa."
        )

        with st.spinner("Buscando texto oficial atualizado..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_LEGISLACAO,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        tools=[{"google_search": {}}],
                    )
                )

                st.markdown("---")
                st.markdown("### 🏛️ Texto Legal Encontrado")
                st.write(response.text)
                st.success("✔ Conteúdo sincronizado com fontes oficiais da legislação brasileira.")

            except Exception as e:
                st.error(f"Erro ao buscar o texto legal: {e}")

    elif botao_buscar and not pedido_lei:
        st.warning("Por favor, informe o artigo ou lei que deseja ler.")

# 4ª OPÇÃO: DICIONÁRIO JURÍDICO INTERATIVO
elif opcao_menu == "📔 Dicionário Jurídico e Latim":
    st.subheader("📔 Dicionário Jurídico e Expressões em Latim")
    st.write("Digite um termo técnico ou expressão em latim para obter a tradução e o significado aplicado ao Direito.")

    termo_busca = st.text_input(
        "Qual termo você deseja consultar?",
        placeholder="Ex: In dubio pro reo, Jus puniendi, Vacatio Legis, Erga omnes"
    )

    btn_dicionario = st.button("🔍 Consultar Termo")

    if btn_dicionario and termo_busca:
        PROMPT_DICIONARIO = (
            f"Você é um Dicionário Jurídico dinâmico do Canal Juridiquês, focado em ajudar estudantes de graduação em Direito. "
            f"Explique de forma objetiva, didática e direta o significado do seguinte termo: '{termo_busca}'.\n\n"
            f"REGRAS DE FORMATAÇÃO:\n"
            f"1. Se o termo for em latim, forneça a tradução literal destacada logo na primeira linha.\n"
            f"2. Explique o conceito jurídico em no máximo dois parágrafos curtos.\n"
            f"3. Forneça um exemplo rápido de aplicação desse termo no direito brasileiro.\n"
            f"4. Mantenha uma linguagem acessível e profissional."
        )

        with st.spinner(f"Buscando o significado de '{termo_busca}'..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_DICIONARIO,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                    )
                )

                st.markdown("---")
                st.markdown(response.text)

            except Exception as e:
                st.error(f"Erro ao buscar o termo: {e}")

    elif btn_dicionario and not termo_busca:
        st.warning("Por favor, digite uma palavra ou expressão para consultar.")
