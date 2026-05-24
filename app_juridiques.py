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

# MENU LATERAL (Se adapta elegantemente no menu hambúrguer do celular)
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
    st.caption("📢 Espaço para anúncios Google AdSense.")

# CABEÇALHO PRINCIPAL (Centralizado e limpo)
st.markdown("<h2 style='color: #c5a059; margin-bottom: 0px; text-align: center;'>⚖️ Canal Juridiquês</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'><i>Seu ecossistema acadêmico inteligente.</i></p>", unsafe_allow_html=True)
st.markdown("---")

# NAVEGAÇÃO OTIMIZADA PARA DISPOSITIVOS MÓVEIS
opcao_menu = st.selectbox(
    "Escolha o que deseja acessar:",
    ["💬 Tutor de Inteligência Artificial", "📖 Guia de Metodologia de Pesquisa"]
)

st.markdown("<br>", unsafe_allow_html=True)

# 1ª OPÇÃO: O CHATBOT INTELIGENTE
if opcao_menu == "💬 Tutor de Inteligência Artificial":
    
    PROMPT_SISTEMA = (
        "Você é o 'Tutor Jurídico Acadêmico' do site Canal Juridiquês. Seu papel é auxiliar estudantes de Direito de forma clara, precisa e extremamente didática. "
        "Use formatação limpa (Markdown, negritos e listas). Quando mencionar livros ou materiais, utilize o formato de link padrão do site: [Compre na Amazon](https://www.amazon.com.br/s?k=NOME_DO_LIVRO&i=books)."
    )

    # Puxa de forma 100% segura a chave salva nos Secrets do Streamlit
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        st.error("Erro: A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit ou é inválida.")
        st.stop()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra o histórico de conversas na tela
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Caixa de entrada adaptada para o teclado do celular
    if prompt := st.chat_input("Digite sua dúvida jurídica aqui..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepara o histórico no formato esperado pela nova SDK da Google
                historico_api = []
                for m in st.session_state.messages[:-1]:
                    role_api = "user" if m["role"] == "user" else "model"
                    historico_api.append(types.Content(
                        role=role_api,
                        parts=[types.Part.from_text(text=m["content"])]
                    ))
                
                # Executa a chamada em Stream
                response_stream = client.models.generate_content_stream(
                    model='gemini-2.5-flash',
                    contents=[
                        *historico_api,
                        types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
                    ],
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_SISTEMA,
                        temperature=0.7,
                    )
                )
                
                # Renderiza o texto dinamicamente na tela
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                # Exibe o resultado final sem o cursor de digitação
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua solicitação: {e}")

# 2ª OPÇÃO: GUIA DE METODOLOGIA
elif opcao_menu == "📖 Guia de Metodologia de Pesquisa":
    st.subheader("📖 Guia de Metodologia de Pesquisa")
    st.write("Bem-vindo ao espaço de apoio à pesquisa científica e TCC do Canal Juridiquês!")
    st.info("Esta seção está pronta para receber suas diretrizes de artigos, formatação ABNT ou dicas de monografia.")
