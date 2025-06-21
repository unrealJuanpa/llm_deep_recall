# basic_agent.py
import requests
import re
from typing import Callable, Any, Optional


class BasicAgent:
    def __init__(self,
                 model: str = "gemma3:latest",
                 base_url: str = "http://localhost:11434",
                 n_interactions: int = 4):
        self.model = model
        self.base_url = base_url
        self.n_interactions = n_interactions
        self.chat_history: list[dict] = []
        self.tools: dict[str, Callable[..., Any]] = {}

    def register_tool(self, name: str, func: Callable[..., Any]):
        """Registra una función disponible para el agente."""
        self.tools[name] = func

    def _generate_system_prompt(self) -> str:
        """Genera la instrucción del sistema con funciones disponibles."""
        tool_descriptions = "\n".join(
            f"- {name}{self._get_signature(func)}: {func.__doc__ or 'Sin descripción'}"
            for name, func in self.tools.items()
        )
        return (
            "Eres un agente con acceso a las siguientes funciones:\n"
            f"{tool_descriptions}\n\n"
            "Si puedes responder usando una función, responde exclusivamente en el siguiente formato:\n"
            "`función: nombre_función(arg1, arg2, ...)`\n"
            "No expliques nada más. Si no puedes usar ninguna función, responde normalmente."
        )

    def _get_signature(self, func: Callable) -> str:
        """Extrae la firma de la función (solo nombres de argumentos)."""
        from inspect import signature
        sig = signature(func)
        args = ", ".join(sig.parameters.keys())
        return f"({args})"

    def _parse_function_call(self, text: str) -> Optional[str]:
        """Detecta y ejecuta una llamada a función tipo: función: sumar(2, 3)"""
        match = re.match(r"función:\s*(\w+)\((.*)\)", text.strip(), re.IGNORECASE)
        if match:
            tool_name = match.group(1)
            raw_args = match.group(2)
            if tool_name in self.tools:
                try:
                    args = eval(f"[{raw_args}]")
                    print(f"[Ejecutando función '{tool_name}' con argumentos {args}]")
                    result = self.tools[tool_name](*args)
                    return str(result)
                except Exception as e:
                    return f"[Error al ejecutar función '{tool_name}']: {e}"
        return None

    def chat(self, user_input: str) -> str:
        self.chat_history.append({"role": "user", "content": user_input})

        # Construir mensajes (incluir prompt del sistema + historia)
        messages = [{"role": "system", "content": self._generate_system_prompt()}]
        max_messages = self.n_interactions * 2
        messages.extend(self.chat_history[-max_messages:])

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            ai_reply = data.get("message", {}).get("content", "[Respuesta vacía]")

            # Detectar si el modelo respondió con una llamada a función
            function_result = self._parse_function_call(ai_reply)
            if function_result is not None:
                self.chat_history.append({"role": "assistant", "content": function_result})
                return function_result

            self.chat_history.append({"role": "assistant", "content": ai_reply})
            return ai_reply

        except requests.exceptions.RequestException as e:
            return f"[Error de conexión]: {e}"
