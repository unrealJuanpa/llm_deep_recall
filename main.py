# main.py
from basic_agent import BasicAgent

def sumar(a: int, b: int) -> int:
    """Devuelve la suma de a y b."""
    return a + b

def multiplicar(a: int, b: int) -> int:
    """Devuelve el producto de a y b."""
    return a * b

agent = BasicAgent()
agent.register_tool("sumar", sumar)
agent.register_tool("multiplicar", multiplicar)

print("Agente iniciado. Puedes decir cosas como '¿cuánto es 7 por 8?' o 'suma 2 y 5'\n")

while True:
    user_input = input("Tú: ")
    respuesta = agent.chat(user_input)
    print(f"Agente: {respuesta}")
