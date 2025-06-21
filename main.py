from ai_agent import AIAgent


if __name__ == "__main__":
    # Create agent instance
    agent = AIAgent()
    
    print("=== AI Agent with Ollama ===")
    print(f"Configuration: {agent.get_info()}")
    print("Type 'exit' to quit, 'clear' to reset history")
    print("=" * 50)
    
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