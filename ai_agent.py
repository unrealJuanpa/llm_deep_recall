import requests
import json
import re
import os
import sys
from typing import List, Dict, Optional, Callable

class AIAgent:
    def __init__(self, 
                 host: str = "127.0.0.1",
                 port: int = 11434,
                 model: str = "gemma3:latest",
                 history_limit: int = 5,
                 tools: Optional[List[Callable]] = None,
                 max_iterations: int = 10):
        """
        Initialize AI Agent with Ollama integration
        
        Args:
            host: Ollama server IP (default: 127.0.0.1)
            port: Ollama server port (default: 11434)
            model: Model to use (default: gemma3:latest)
            history_limit: Maximum number of interactions to maintain (default: 5)
            tools: List of functions available to the agent (default: None)
            max_iterations: Maximum internal iterations before forcing response (default: 10)
        """
        self.host = host
        self.port = port
        self.model = model
        self.history_limit = history_limit
        self.tools = tools or []
        self.max_iterations = max_iterations
        self.base_url = f"http://{host}:{port}"
        
        # Add built-in reply function
        self._add_reply_function()
        
        # Create tools registry for easy access
        self.tools_registry = {tool.__name__: tool for tool in self.tools}
        
        # Generate tools documentation
        self.tools_documentation = self._generate_tools_documentation()
        
        # Internal system prompt - CANNOT be modified from outside
        base_system_prompt = """Eres un asistente de IA servicial y amable. Puedes ejecutar funciones para ayudar al usuario.

IMPORTANTE: Para ejecutar una función, responde ÚNICAMENTE con un JSON en este formato:
{"function": "nombre_funcion(argumentos)"}

Por ejemplo:
{"function": "suma(3, 5)"}
{"function": "buscar_archivo('documento.txt')"}

Después de ejecutar una función, recibirás el resultado y podrás ejecutar más funciones si es necesario.

Para dar tu respuesta final al usuario, DEBES usar la función reply:
{"function": "reply('tu respuesta aquí')"}

Esta función reply terminará la conversación y enviará tu respuesta al usuario."""
        
        # Add tools documentation to system prompt if tools are available
        if self.tools_documentation:
            self.system_prompt = f"{base_system_prompt}\n\n{self.tools_documentation}"
        else:
            self.system_prompt = base_system_prompt
        
        # Conversation history - always starts with system prompt
        self.history: List[Dict[str, str]] = [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "Entendido. Puedo ejecutar funciones y usar reply() para responder."}
        ]
        
        # Flag to control reply function
        self._reply_called = False
        self._final_response = ""
        
        # Initialize color support
        self._init_color_support()
    
    def _init_color_support(self):
        """Initialize color support detection"""
        self.colors_enabled = False
        
        # Check if we're in a terminal that supports colors
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            # Check various environment variables that indicate color support
            term = os.environ.get('TERM', '').lower()
            colorterm = os.environ.get('COLORTERM', '').lower()
            
            # Common terminals that support colors
            color_terms = [
                'xterm', 'xterm-color', 'xterm-256color', 'screen', 'screen-256color',
                'tmux', 'tmux-256color', 'rxvt', 'ansi', 'cygwin', 'linux'
            ]
            
            # Enable colors if:
            # 1. TERM contains a known color terminal
            # 2. COLORTERM is set (usually indicates color support)
            # 3. Force enable if FORCE_COLOR is set
            if (any(ct in term for ct in color_terms) or 
                colorterm or 
                os.environ.get('FORCE_COLOR') or
                os.environ.get('CLICOLOR')):
                self.colors_enabled = True
        
        # Set color codes
        if self.colors_enabled:
            self.GRAY = '\033[90m'
            self.RESET = '\033[0m'
            self.BOLD = '\033[1m'
        else:
            self.GRAY = ''
            self.RESET = ''
            self.BOLD = ''
    
    def _print_colored(self, text: str, color: str = '', end: str = '', flush: bool = True):
        """Print text with color if supported"""
        if color and self.colors_enabled:
            print(f"{color}{text}{self.RESET}", end=end, flush=flush)
        else:
            print(text, end=end, flush=flush)
        """Adds the built-in reply function"""
        def reply(message: str):
            """
            Función para enviar la respuesta final al usuario.
            Esta función termina el ciclo de ejecución interno.
            """
            return message
        
    def _add_reply_function(self):
        """Adds the built-in reply function"""
        def reply(message: str):
            """
            Función para enviar la respuesta final al usuario.
            Esta función termina el ciclo de ejecución interno.
            """
            return message
        
        self.tools.append(reply)
    
    def _generate_tools_documentation(self) -> str:
        """
        Generates documentation string for available tools
        
        Returns:
            String with tools documentation or empty string if no tools
        """
        if not self.tools:
            return ""
        
        documentation_lines = ["Funciones disponibles:"]
        
        for tool in self.tools:
            # Get function name
            func_name = tool.__name__
            
            # Get function docstring
            docstring = tool.__doc__
            if docstring:
                # Clean and format docstring
                docstring = docstring.strip()
                # Replace multiple whitespaces and newlines with single spaces
                docstring = ' '.join(docstring.split())
            else:
                docstring = "Sin descripción disponible"
            
            # Add function documentation
            documentation_lines.append(f"{func_name}: {docstring}")
        
        return "\n".join(documentation_lines)
    
    def _execute_function(self, function_call: str) -> str:
        """
        Executes a function call string and returns the result
        
        Args:
            function_call: String like "function_name(args)"
            
        Returns:
            String representation of the function result
        """
        try:
            # Parse function name and arguments
            match = re.match(r'(\w+)\((.*)\)', function_call.strip())
            if not match:
                return f"Error: Formato de función inválido: {function_call}"
            
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Check if function exists
            if func_name not in self.tools_registry:
                return f"Error: Función '{func_name}' no encontrada"
            
            # Special handling for reply function
            if func_name == 'reply':
                self._reply_called = True
                # Extract the message from the arguments
                if args_str.startswith("'") and args_str.endswith("'"):
                    self._final_response = args_str[1:-1]
                elif args_str.startswith('"') and args_str.endswith('"'):
                    self._final_response = args_str[1:-1]
                else:
                    self._final_response = args_str
                return f"Respuesta enviada al usuario: {self._final_response}"
            
            # Execute the function
            func = self.tools_registry[func_name]
            
            # Simple argument parsing (handles basic cases)
            if not args_str.strip():
                result = func()
            else:
                # Use eval for argument parsing (be careful in production)
                # This is a simplified approach
                try:
                    result = eval(f"func({args_str})")
                except Exception as e:
                    return f"Error ejecutando {func_name}: {str(e)}"
            
            return str(result)
            
        except Exception as e:
            return f"Error procesando función: {str(e)}"
    
    def _extract_json_function(self, text: str) -> Optional[str]:
        """
        Extracts function call from JSON in the text
        
        Args:
            text: Text that might contain JSON function call
            
        Returns:
            Function call string or None if not found
        """
        try:
            # Look for JSON pattern
            json_match = re.search(r'\{[^}]*"function"[^}]*\}', text)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                if "function" in parsed:
                    return parsed["function"]
        except:
            pass
        return None
    
    def _get_agent_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Gets response from the agent with streaming
        
        Args:
            messages: Message history
            
        Returns:
            Complete agent response
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=30
            )
            response.raise_for_status()
            
            complete_response = ""
            
            # Process response stream with color
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            self._print_colored(content, self.GRAY, end="", flush=True)
                            complete_response += content
                            
                        # Check if stream is done
                        if chunk.get('done', False):
                            break
                            
                    except json.JSONDecodeError:
                        continue
            
            return complete_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _maintain_history_limit(self):
        """Maintains history within the specified limit"""
        # Always preserve the first 2 messages (system prompt + response)
        if len(self.history) > (self.history_limit * 2 + 2):
            # Keep system prompt + response, and the last N exchanges
            messages_to_keep = self.history_limit * 2
            self.history = self.history[:2] + self.history[-(messages_to_keep):]
    
    def send_message(self, message: str) -> str:
        """
        Send a message to the agent and receive response after internal iterations
        
        Args:
            message: User message
            
        Returns:
            Final agent response
        """
        # Reset reply state
        self._reply_called = False
        self._final_response = ""
        
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Internal iteration loop
        current_messages = self.history.copy()
        iteration = 0
        
        print(f"Usuario: {message}")
        print("--- Procesamiento interno del agente ---")
        
        while not self._reply_called and iteration < self.max_iterations:
            iteration += 1
            self._print_colored(f"\n[Iteración {iteration}]", self.GRAY)
            
            # Get agent response
            self._print_colored("Agente piensa: ", self.GRAY, end="", flush=True)
            agent_response = self._get_agent_response(current_messages)
            print()  # New line after streaming
            
            # Check if there's a function call
            function_call = self._extract_json_function(agent_response)
            
            if function_call:
                self._print_colored(f"Ejecutando: {function_call}", self.GRAY)
                
                # Execute the function
                function_result = self._execute_function(function_call)
                self._print_colored(f"Resultado: {function_result}", self.GRAY)
                
                # Add to conversation
                current_messages.append({"role": "assistant", "content": agent_response})
                current_messages.append({"role": "user", "content": f"Resultado de la función: {function_result}"})
                
                # If reply was called, break the loop
                if self._reply_called:
                    break
                    
            else:
                # No function call found, treat as final response
                self._final_response = agent_response
                break
        
        # Handle max iterations reached
        if iteration >= self.max_iterations and not self._reply_called:
            self._final_response = "Se alcanzó el límite máximo de iteraciones. Proceso terminado."
        
        print("\n--- Fin del procesamiento ---")
        print(f"Respuesta final: {self._final_response}")
        
        # Add final exchange to history
        self.history.append({"role": "assistant", "content": self._final_response})
        
        # Maintain history limit
        self._maintain_history_limit()
        
        return self._final_response
    
    def get_history(self) -> List[Dict[str, str]]:
        """Returns the current conversation history"""
        return self.history.copy()
    
    def clear_history(self):
        """Resets history keeping only the system prompt"""
        self.history = [
            {"role": "user", "content": self.system_prompt},
            {"role": "assistant", "content": "Entendido. Puedo ejecutar funciones y usar reply() para responder."}
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
            "max_iterations": self.max_iterations,
            "messages_in_history": len(self.history),
            "base_url": self.base_url,
            "tools_count": len(self.tools),
            "tools_documentation": self.tools_documentation
        }
    
    def get_tools_documentation(self) -> str:
        """Returns the tools documentation string"""
        return self.tools_documentation