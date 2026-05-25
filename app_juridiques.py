"""
Projeto: Canal Juridiquês
Versão: 1.0.5
Descrição: Ecossistema acadêmico inteligente com Tutor, Metodologia, Vade Mecum, Simulador, Dicionário e Fale Conosco.
Autoria: Sergio Moreira Neri
"""

import streamlit as st
from google import genai
from google.genai import types
import os

# Configuração da página web (Otimizada para Mobile e Computador)
st.set_page_config(page_title="Canal Juridiquês", page_icon="⚖️", layout="centered")

# 1. ESTILIZAÇÃO CUSTOMIZADA (CSS Totalmente Responsivo)
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
    
    # SEÇÃO: FALE CONOSCO
    st.header("📬 Fale Conosco")
    st.write("Dúvidas, sugestões ou problemas com a plataforma? Entre em contato conosco.")
    st.link_button("📧 Enviar E-mail", "mailto:contato@canaljuridiques.com.br")
    
    st.markdown("---")
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

# NAVEGAÇÃO DO MENU ATUALIZADA (VERSÃO 1.0.5)
opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
    [
        "💬 Tutor de Inteligência Artificial", 
        "📖 Guia de Metodologia de Pesquisa",
        "📜 Consulta à Legislação e Letra da Lei",
        "🧠 Simulador de Questões e Simulado",
        "📖 Dicionário de Termos e Latim"
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


# 2ª OPÇÃO: GUIA DE METODOLOGIA INTERATIVO (Protegido contra plágio)
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Assistente de Projetos Científicos e TCC")
    
    st.warning(
        "⚠️ **Diretriz Ética e de Integridade Acadêmica:**\n\n"
        "Esta ferramenta funciona exclusivamente como um **guia de orientação e estrutura conceitual**. "
        "A IA **não redigirá** o conteúdo do seu trabalho (parágrafos, capítulos ou introduções), "
        "evitando práticas que configurem plágio ou violação de direitos autorais. "
        "A autoria e o desenvolvimento do texto científico são de responsabilidade exclusiva do estudante."
    )
    
    st.write("Insira a ideia central do seu projeto para obter um esqueleto metodológico personalizado no padrão acadêmico correto.")
    
    tema_usuario = st.text_input(
        "Digite a ideia central ou o tema do seu trabalho:",
        placeholder="Ex: A eficácia da LGPD na segurança pública"
    )
    
    botao_gerar = st.button("🚀 Gerar Estrutura Acadêmica")
    
    if botao_gerar and tema_usuario:
        PROMPT_METODOLOGIA = (
            f"Você é um orientador acadêmico especialista em metodologia científica jurídica, com foco estrito na ética e integridade acadêmica. "
            f"Analise o seguinte pedido do estudante: '{tema_usuario}'.\n\n"
            f"DIRETRIZES OBRIGATÓRIAS DE ESCOPO:\n"
            f"1. Identifique o formato solicitado pelo usuário (se ele mencionou artigo, TCC, monografia, etc.). Se não especificou, adote o padrão de Artigo Científico.\n"
            f"2. Você está RIGOROSAMENTE PROIBIDO de escrever textos longos, parágrafos de desenvolvimento, introduções prontas, conclusões prontas ou qualquer conteúdo que o aluno possa copiar e colar direto no trabalho final.\n"
            f"3. Seu papel é apenas fornecer INSIGHTS E MAPEAMENTO ESTRUTURAL. Se o usuário solicitar explicitamente para você 'escrever o trabalho', 'fazer o capítulo' ou 'redigir', recuse educadamente, explicando brevemente que a redação integral por IA fere a integridade acadêmica e pode caracterizar plágio.\n\n"
            f"O QUE VOCÊ DEVE GERAR (De forma puramente estrutural e em tópicos):\n"
            f"a) Formato Identificado (Ex: Artigo, TCC, Monografia);\n"
            f"b) Sugestão de Título Refinado;\n"
            f"c) Problema de Pesquisa (pergunta norteadora em uma única frase);\n"
            f"d) Três Objetivos Específicos (em tópicos curtos começando com verbos no infinitivo);\n"
            f"e) Sumário Provisório Sugerido (apenas os títulos dos capítulos/seções adequados ao formato, sem texto descritivo).\n\n"
            f"Mantenha um tom profissional, técnico e pedagógico."
        )
        
        with st.spinner("Analisando o tema e mapeando a estrutura ideal..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_METODOLOGIA,
                    config=types.GenerateContentConfig(
                        temperature=0.4,
                    )
                )
                
                st.markdown("---")
                st.markdown("### 📋 Proposta Estrutural Obtida")
                st.write(response.text)
                st.info("💡 **Como usar este resultado:** Utilize este mapa como base para pesquisar sua doutrina, jurisprudência e iniciar a sua própria escrita de forma autêntica.")
                
            except Exception as e:
                st.error(f"Erro ao processar a estrutura: {e}")
                
    elif botao_gerar and not tema_usuario:
        st.warning("Por favor, digite um tema ou comando antes de clicar em gerar.")


# 3ª OPÇÃO: CONSULTA DE LEGISLAÇÃO (Otimizada com Busca do Google em Tempo Real)
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


# 4ª OPÇÃO: SIMULADOR DE QUESTÕES (NOVO)
elif opcao_menu == "🧠 Simulador de Questões e Simulado":
    st.subheader("🧠 Simulado de Fixação Acadêmica")
    st.write("Teste seus conhecimentos em disciplinas jurídicas chaves. Escolha a matéria abaixo para gerar uma questão de múltipla escolha inédita padrão OAB/Banca.")
    
    materia_escolhida = st.selectbox(
        "Selecione a matéria que deseja treinar:",
        ["Introdução ao Estudo do Direito (IED)", "Direito Constitucional", "Teoria Geral do Direito", "Direito Penal", "Sociologia Jurídica"]
    )
    
    botao_questao = st.button("🎯 Gerar Nova Questão")
    
    # Armazena a questão gerada no estado da sessão para não sumir ao clicar no botão de revelar gabarito
    if botao_questao:
        PROMPT_QUESTOES = (
            f"Você é um docente de Direito especialista na elaboração de exames da OAB e ENADE. "
            f"Gere uma questão inédita de múltipla escolha sobre a matéria: '{materia_escolhida}'.\n\n"
            f"A estrutura da resposta deve conter obrigatoriamente:\n"
            f"1) Um enunciado baseado em um caso prático ou problema teórico acadêmico;\n"
            f"2) Quatro alternativas de resposta rotuladas de A até D;\n"
            f"3) Abaixo de tudo, adicione uma linha divisória com traços '---' e escreva o GABARITO COMENTADO de cada alternativa de forma detalhada, indicando qual é a correta e o porquê."
        )
        
        with st.spinner("Estruturando questão inédita..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_QUESTOES,
                    config=types.GenerateContentConfig(temperature=0.7)
                )
                # Separa a resposta entre a Questão e o Gabarito com base no divisor '---'
                partes = response.text.split("---")
                st.session_state.txt_questao = partes[0]
                st.session_state.txt_gabarito = partes[1] if len(partes) > 1 else "Gabarito indisponível para esta questão."
            except Exception as e:
                st.error(f"Erro ao processar o simulador: {e}")
                
    # Exibe a questão se ela já tiver sido gerada
    if "txt_questao" in st.session_state:
        st.markdown("---")
        st.markdown("### 📝 Questão Proposta")
        st.write(st.session_state.txt_questao)
        
        # Sistema interativo antifrustração: o aluno só abre o gabarito se acionar o switch
        mostrar_gabarito = st.toggle("👁️ Revelar Resposta e Gabarito Comentado")
        if mostrar_gabarito:
            st.info(st.session_state.txt_gabarito)


# 5ª OPÇÃO: DICIONÁRIO JURÍDICO (NOVO)
elif opcao_menu == "📖 Dicionário de Termos e Latim":
    st.subheader("📖 Dicionário de Juridiquês e Latim")
    st.write("Digite termos técnicos, expressões em latim ou brocardos jurídicos para descobrir o significado exato no ordenamento brasileiro.")
    
    termo_pesquisa = st.text_input(
        "Qual palavra ou jargão em latim deseja traduzir?",
        placeholder="Ex: In dubio pro reo / Pacta sunt servanda / Erga omnes"
    )
    
    botao_dicionario = st.button("📚 Consultar Dicionário")
    
    if botao_dicionario and termo_pesquisa:
        PROMPT_DICIONARIO = (
            f"Você é um lexicógrafo jurídico renomado especialista em termos jurídicos e latim forense. "
            f"Analise a expressão ou palavra informada pelo aluno: '{termo_pesquisa}'.\n\n"
            f"Forneça um verbete de dicionário claro contendo:\n"
            f"1) Tradução Literal (se for do latim) ou Significado Direto;\n"
            f"2) Contexto Acadêmico (como e onde essa expressão é aplicada no Direito moderno);\n"
            f"3) Um exemplo de frase ou cenário prático onde esse termo é comumente empregado nas petições ou decisões."
        )
        
        with st.spinner("Buscando significado no repositório lexicográfico..."):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=PROMPT_DICIONARIO,
                    config=types.GenerateContentConfig(temperature=0.4)
                )
                st.markdown("---")
                st.markdown(f"### 🔍 Significado de: *{termo_pesquisa}*")
                st.write(response.text)
            except Exception as e:
                st.error(f"Erro ao processar o dicionário: {e}")
                
    elif botao_dicionario and not termo_pesquisa:
        st.warning("Por favor, digite um termo para realizar a busca.")