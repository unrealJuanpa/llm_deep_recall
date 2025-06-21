# basic_agent.py
import requests

class BasicAgent:
    def __init__(self,
                 model: str = "gemma3:latest",
                 base_url: str = "http://localhost:11434",
                 n_interactions: int = 4):
        self.model = model
        self.base_url = base_url
        self.n_interactions = n_interactions
        self.chat_history: list[dict] = []

    def chat(self, user_input: str) -> str:
        # Agregar mensaje del usuario
        self.chat_history.append({"role": "user", "content": user_input})

        # Limitar historial a las últimas N interacciones
        max_messages = self.n_interactions * 2
        recent_history = self.chat_history[-max_messages:]

        payload = {
            "model": self.model,
            "messages": recent_history,
            "stream": False
        }

        try:
            response = requests.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            ai_reply = data.get("message", {}).get("content", "[Respuesta vacía]")

            # Agregar respuesta del agente
            self.chat_history.append({"role": "assistant", "content": ai_reply})

            return ai_reply
        except requests.exceptions.RequestException as e:
            return f"[Error de conexión]: {e}"
