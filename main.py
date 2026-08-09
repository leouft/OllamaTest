import ollama, json

modelo = "gemma4"
history_save_file = "all_history.json"
file_code_name = "main.py"

# history é a memória local que será salva no disco rigido
history = [ 
    {
        "role": "system", 
        "content": (
            "Sessão de conversa inicializada. " 
            "Você é um assistente virtual chamado Kernel "
            "(nome que você mesmo escolheu) que está ajudando "
            "um aluno do 3° período de Ciência da Computação "
            "a entender Python e o uso da ferramenta Ollama. " 
            "Seu código fonte também será enviado junto."
        )
    }
]

def chat_with_context(messages, modelo):
    try:
        response = ollama.chat(
            model=modelo,
            messages=messages, # Passa toda a lista de conversa
            options={
                'num_ctx': 16384,
                'num_predict': -1
            }
        )

        resposta_text = response['message']['content'].strip()
        return resposta_text

    except Exception as e:
        print(f"Erro: {e}\n")

class ConversationManager:
    def __init__(self, code_file_name, save_file_name):
        self.code_file = code_file_name
        self.file_name = save_file_name

    def load_context(self):
        print("\n Carregando contexto... \n")

        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                saved_history = json.load(file)

                for message in saved_history:
                    if (
                        isinstance(message, dict)
                        and "role" in message
                        and "content" in message
                    ):
                        history.append({"role": message["role"], "content": message["content"]})

        except Exception as e:
            print(f"\nErro: {e}\n")

    def save_session(self):
        try:
            saved_history = []

            for message in history:
                if message["role"] != "system":
                    saved_history.append({
                        "role": message["role"],
                        "content": message["content"].strip()
                    })

            with open(self.file_name, "w", encoding="utf-8") as file:
                json.dump(
                    saved_history,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception as e:
            print(f"\nErro ao salvar arquivo: {e}.\n")

    def load_code(self):
        try:
            with open(self.code_file, "r", encoding="utf-8") as file:
                code = file.read()

            return {"role": "system", "content": "Código fonte atual:\n\n" + code}

        except Exception as e:
            print(f"Erro: {e}\n")
            return None

cManager = ConversationManager(file_code_name, history_save_file)

cManager.load_context()

while True:
    print("Usuário: ", end="")
    message = input()

    if message == "/exit":
        cManager.save_session()
        break

    elif message == "/delete":
        with open(history_save_file, "w", encoding="utf-8") as file:
            json.dump([], file)
        print("Histórico apagado.")
        break

    context = history.copy() # context é uma memória temporária da conversa

    code_message = cManager.load_code()
    if code_message:
        context.append(code_message)
        history.append(code_message)

    context.append({"role": "user", "content": message})

    response = chat_with_context(context, modelo)

    print(f"Kernel: {response}\n")

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})