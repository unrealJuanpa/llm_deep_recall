# main_basic.py
from basic_agent import BasicAgent

def main():
    agent = BasicAgent(n_interactions=4)

    print("🤖 Agente básico inicializado con gemma3:latest. Escribe 'salir' para terminar.")
    
    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("👋 Terminando conversación.")
            break

        respuesta = agent.chat(user_input)
        print("Agente:", respuesta)

if __name__ == "__main__":
    main()
