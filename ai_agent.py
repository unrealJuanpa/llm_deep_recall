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
        
        # Sistema prompt interno optimizado - NO puede ser modificado desde el exterior
        base_system_prompt = """Eres un asistente IA que responde SOLO en español.

🚨 REGLA CRÍTICA: TODA conversación DEBE terminar con reply('tu respuesta') cuando termines de hacer tu analisis, con la funcion reply das tu conclusion
Sin reply() el sistema falla y entra en bucle infinito.

FLUJO OBLIGATORIO:
1. Analiza la consulta
2. Usa herramientas si necesitas información/cálculos (opcional)
3. Llama reply('respuesta completa en español') (OBLIGATORIO)

HERRAMIENTAS:
- Llama funciones directamente: buscar_en_internet('consulta')
- SIEMPRE termina con: reply('tu respuesta final')

EJEMPLOS:
• Pregunta simple → reply('Respuesta directa')
• Necesitas datos → buscar_en_internet('datos') → reply('Respuesta con datos')
• Necesitas cálculo → calcular(operación) → reply('Resultado explicado')

REGLAS:
✅ Usa herramientas cuando necesites información externa
✅ SIEMPRE termina con reply()
✅ Responde solo en español
❌ NUNCA respondas sin reply()
❌ NUNCA inventes información
❌ NUNCA termines sin reply()

CASOS ESPECIALES:
- Pregunta confusa → reply('Podrías aclarar...')
- Error → reply('Hubo un problema...')
- Todo caso DEBE terminar con reply()

🔴 CRÍTICO: reply() es OBLIGATORIO en cada interacción de finalizacion, con reply indicas tu conclusion"""
        
        # Add tools documentation to system prompt if tools are available
        if self.tools_documentation:
            self.system_prompt = f"{base_system_prompt}\n\n{self.tools_documentation}"
        else:
            self.system_prompt = base_system_prompt
        
        # Conversation history - always starts with system prompt
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
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
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
        else:
            self.GRAY = ''
            self.RESET = ''
            self.BOLD = ''
            self.GREEN = ''
            self.YELLOW = ''
    
    def _print_colored(self, text: str, color: str = '', end: str = '', flush: bool = True):
        """Print text with color if supported"""
        if color and self.colors_enabled:
            print(f"{color}{text}{self.RESET}", end=end, flush=flush)
        else:
            print(text, end=end, flush=flush)
    
    def _add_reply_function(self):
        """Adds the built-in reply function"""
        def reply(message: str):
            """
            Función OBLIGATORIA para enviar la respuesta final al usuario.
            Debes usar esta función para terminar cada conversación.
            
            Args:
                message (str): Tu respuesta completa para el usuario
            
            Returns:
                str: Confirmación de envío
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
        
        documentation_lines = ["\nHERRAMIENTAS DISPONIBLES:"]
        documentation_lines.append("=" * 40)
        
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
            
            # Add function documentation with clear formatting
            documentation_lines.append(f"\n• {func_name}:")
            documentation_lines.append(f"  Description: {docstring}")
            documentation_lines.append(f"  Usage: {func_name}(arguments)")
        
        documentation_lines.append("\nREMEMBER: Only YOU can execute these tools by calling them directly by name.")
        
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
            # Clean the function call (remove extra whitespace)
            function_call = function_call.strip()
            
            # Parse function name and arguments
            match = re.match(r'(\w+)\((.*)\)', function_call)
            if not match:
                return f"Error: Formato de función inválido: {function_call}. Usa el formato: nombre_funcion(argumentos)"
            
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Check if function exists
            if func_name not in self.tools_registry:
                available_tools = list(self.tools_registry.keys())
                return f"Error: Función '{func_name}' no encontrada. Herramientas disponibles: {available_tools}"
            
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
                return f"✓ Respuesta enviada al usuario"
            
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
                    return f"Error en argumentos de {func_name}: {str(e)}. Verifica la sintaxis."
            
            return str(result)
            
        except Exception as e:
            return f"Error procesando función: {str(e)}"
    
    def _extract_function_calls(self, text: str) -> List[str]:
        """
        Extracts all function calls from the text using multiple detection methods
        
        Args:
            text: Text that might contain function calls
            
        Returns:
            List of function call strings
        """
        function_calls = []
        
        try:
            # Method 1: Look for Python code blocks
            code_block_pattern = r'```python\s*\n?(.*?)\n?```'
            code_matches = re.findall(code_block_pattern, text, re.DOTALL | re.IGNORECASE)
            
            for match in code_matches:
                code_content = match.strip()
                lines = code_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if re.match(r'\w+\(.*\)', line):
                        function_calls.append(line)
            
            # Method 2: Look for direct function calls anywhere in text
            available_functions = list(self.tools_registry.keys())
            
            for func_name in available_functions:
                # Create pattern for this specific function
                # This pattern looks for: function_name followed by opening parenthesis
                pattern = rf'\b{re.escape(func_name)}\s*\('
                
                # Find all matches of this pattern
                matches = re.finditer(pattern, text)
                
                for match in matches:
                    start_pos = match.start()
                    # Find the complete function call by counting parentheses
                    paren_count = 0
                    pos = match.end() - 1  # Start from the opening parenthesis
                    
                    while pos < len(text):
                        if text[pos] == '(':
                            paren_count += 1
                        elif text[pos] == ')':
                            paren_count -= 1
                            if paren_count == 0:
                                # Found the complete function call
                                function_call = text[start_pos:pos+1]
                                function_calls.append(function_call)
                                break
                        pos += 1
            
            # Method 3: Look for function calls on their own lines
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                # Check if line looks like a function call
                if re.match(r'\w+\(.*\)', line):
                    func_name = line.split('(')[0]
                    if func_name in self.tools_registry:
                        function_calls.append(line)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_calls = []
            for call in function_calls:
                if call not in seen:
                    seen.add(call)
                    unique_calls.append(call)
            
            return unique_calls
            
        except Exception as e:
            print(f"Error extracting function calls: {e}")
            return []
    
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
        # Always preserve the system message (first message)
        if len(self.history) > (self.history_limit * 2 + 1):
            # Keep system message, and the last N exchanges
            messages_to_keep = self.history_limit * 2
            self.history = self.history[:1] + self.history[-(messages_to_keep):]
    
    # Mejoras sugeridas para el método send_message

    def send_message(self, message: str) -> str:
        """
        Send a message to the agent and receive response after internal iterations
        """
        # Reset reply state
        self._reply_called = False
        self._final_response = ""
        
        # Add user message to history
        self.history.append({"role": "user", "content": message})
        
        # Internal iteration loop
        current_messages = self.history.copy()
        iteration = 0
        consecutive_no_reply = 0  # Contador para respuestas sin reply()
        
        print(f"Usuario: {message}")
        print("--- Procesamiento interno del agente ---")
        
        while not self._reply_called and iteration < self.max_iterations:
            iteration += 1
            self._print_colored(f"\n[Iteración {iteration}]", self.YELLOW)
            
            # Get agent response
            self._print_colored(" Agente piensa: ", self.GRAY, end="", flush=True)
            agent_response = self._get_agent_response(current_messages)
            print()  # New line after streaming
            
            # Check if there are function calls in the response
            function_calls = self._extract_function_calls(agent_response)
            
            if function_calls:
                consecutive_no_reply = 0  # Reset counter si hay function calls
                
                # Execute all found function calls
                for function_call in function_calls:
                    self._print_colored(f"⚡ Ejecutando: {function_call}", self.GREEN)
                    
                    # Execute the function
                    function_result = self._execute_function(function_call)
                    self._print_colored(f"📋 Resultado: {function_result}", self.GREEN)
                    
                    # If reply was called, break out of both loops
                    if self._reply_called:
                        break
                
                # Add to conversation (only if not reply)
                if not self._reply_called:
                    current_messages.append({"role": "assistant", "content": agent_response})
                    # Combine all results into one message
                    results_message = "Resultados de la ejecución de funciones:\n" + "\n".join([
                        f"- {call}: {self._execute_function(call)}" 
                        for call in function_calls
                    ])
                    current_messages.append({"role": "user", "content": results_message})
                    
            else:
                consecutive_no_reply += 1
                
                # NUEVA LÓGICA: Detectar si necesita usar reply() y forzarlo
                if consecutive_no_reply >= 2:
                    # Después de 2 respuestas sin function calls, forzar reply()
                    current_messages.append({"role": "assistant", "content": agent_response})
                    current_messages.append({
                        "role": "user", 
                        "content": """🚨 CRÍTICO: DEBES usar la función reply() AHORA. 
                        
                        No puedes continuar sin usar reply(). El sistema requiere que uses:
                        reply('tu respuesta completa en español aquí')
                        
                        Esto es OBLIGATORIO para terminar la conversación correctamente."""
                    })
                    consecutive_no_reply = 0
                    continue
                
                # Check if the response looks like it's trying to be a final answer
                final_answer_indicators = [
                    'respuesta:', 'en resumen', 'por lo tanto', 'finalmente', 
                    'en conclusión', 'para concluir', 'respondiendo a tu pregunta',
                    'la respuesta es', 'puedo decirte que', 'según'
                ]
                
                if any(phrase in agent_response.lower() for phrase in final_answer_indicators):
                    # Looks like a final answer - force reply()
                    current_messages.append({"role": "assistant", "content": agent_response})
                    current_messages.append({
                        "role": "user", 
                        "content": """Parece que tienes una respuesta lista. DEBES usar la función reply() para enviarla:
                        
                        reply('tu respuesta completa aquí')
                        
                        Es OBLIGATORIO usar reply() para terminar la conversación."""
                    })
                else:
                    # If it doesn't look like a final answer, encourage progress
                    current_messages.append({"role": "assistant", "content": agent_response})
                    current_messages.append({
                        "role": "user", 
                        "content": "Continúa con tu análisis y usa las herramientas apropiadas, o si ya tienes la respuesta, usa reply() para enviarla."
                    })
        
        # Handle max iterations reached
        if iteration >= self.max_iterations and not self._reply_called:
            self._final_response = "Lo siento, se alcanzó el límite máximo de procesamiento. Por favor, reformula tu consulta."
            self._print_colored("⚠️ Límite de iteraciones alcanzado - forzando respuesta", self.YELLOW)
        
        print("\n--- Fin del procesamiento ---")
        print(f"✅ Respuesta final: {self._final_response}")
        
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
            {"role": "system", "content": self.system_prompt}
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