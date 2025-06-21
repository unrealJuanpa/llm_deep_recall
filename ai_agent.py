import requests
import json
from typing import List, Dict, Optional

class AIAgent:
    def __init__(self, 
                 host: str = "127.0.0.1",
                 port: int = 11434,
                 model: str = "gemma3:latest",
                 history_limit: int = 5):
        """
        Initialize AI Agent with Ollama integration
        
        Args:
            host: Ollama server IP (default: 127.0.0.1)
            port: Ollama server port (default: 11434)
            model: Model to use (default: gemma3:latest)
            history_limit: Maximum number of interactions to maintain (default: 5)
        """
        self.host = host
        self.port = port
        self.model = model
        self.history_limit = history_limit
        self.base_url = f"http://{host}:{port}"
        
        # Internal system prompt - CANNOT be modified from outside
        self.system_prompt = """Eres un asistente de IA servicial y amable. Responde con claridad, concisión y siempre en el lenguaje apropiado. Mantén un tono profesional pero accesible."""
        
        # Conversation history - always starts with system prompt
        self.history: List[Dict[str, str]] = [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "Entendido."}
        ]
    
    def _maintain_history_limit(self):
        """Maintains history within the specified limit"""
        # Always preserve the first 2 messages (system prompt + response)
        if len(self.history) > (self.history_limit * 2 + 2):
            # Keep system prompt + response, and the last N exchanges
            messages_to_keep = self.history_limit * 2
            self.history = self.history[:2] + self.history[-(messages_to_keep):]
    
    def send_message(self, message: str) -> str:
        """
        Send a message to the agent and receive streaming response
        
        Args:
            message: User message
            
        Returns:
            Complete agent response
        """
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Prepare payload for Ollama
        payload = {
            "model": self.model,
            "messages": self.history,
            "stream": True
        }
        
        try:
            # Make POST request with streaming
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            complete_response = ""
            print("Agent: ", end="", flush=True)
            
            # Process response stream
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            print(content, end="", flush=True)
                            complete_response += content
                            
                        # Check if stream is done
                        if chunk.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            print()  # New line at the end
            
            # Add agent response to history
            self.history.append({"role": "assistant", "content": complete_response})
            
            # Maintain history limit
            self._maintain_history_limit()
            
            return complete_response
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Connection error with Ollama: {e}"
            print(f"Error: {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"Error: {error_msg}")
            return error_msg
    
    def get_history(self) -> List[Dict[str, str]]:
        """Returns the current conversation history"""
        return self.history.copy()
    
    def clear_history(self):
        """Resets history keeping only the system prompt"""
        self.history = [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "Understood"}
        ]
    
    def change_model(self, new_model: str):
        """Changes the AI model to use"""
        self.model = new_model
        print(f"Model changed to: {new_model}")
    
    def get_info(self) -> Dict[str, any]:
        """Returns information about the current agent configuration"""
        return {
            "host": self.host,
            "port": self.port,
            "model": self.model,
            "history_limit": self.history_limit,
            "messages_in_history": len(self.history),
            "base_url": self.base_url
        }