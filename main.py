import tools
from ai_agent import AIAgent


# Create agent instance
agent = AIAgent(history_limit=30, tools=[tools.buscar_en_brave, tools.sumar, tools.restar, tools.multiplicar, tools.dividir, tools.potencia, tools.modulo])


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