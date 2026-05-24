with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Prepara o histórico no formato esperado pela nova SDK da Google
                historico_api = []
                for m in st.session_state.messages[:-1]:  # Ignora a última enviada
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
