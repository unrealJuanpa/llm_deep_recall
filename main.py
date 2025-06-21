import tools
from ai_agent import AIAgent
import os

os.system("clear")

# Create agent instance
agent = AIAgent(
    model='llama3.2:3b-instruct-fp16',
    history_limit=30, 
    tools=[
        tools.buscar_en_internet, 
        tools.obtener_contenido_url, 
        tools.sumar, 
        tools.restar, 
        tools.multiplicar, 
        tools.dividir, 
        tools.potencia, 
        tools.modulo, 
        tools.obtener_fecha_hora_actual, 
        tools.calcular_distancia_en_anios
    ]
)


print(agent.get_info()['model'])


while True:
    try:
        # Get user input
        user_message = input("\nYou: ").strip()
        
        if user_message.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_message.lower() == 'clear':
            agent.clear_history()
            print("History cleared.")
            continue
        elif not user_message:
            continue
        
        # Send message and receive response
        agent.send_message(user_message)
        
    except KeyboardInterrupt:
        print("\nGoodbye!")
        break
    except Exception as e:
        print(f"Error: {e}")