import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

def buscar_en_brave(query: str, limite: int = 5) -> str:
    if not API_KEY:
        return "No se encontró la clave API. Verifica tu archivo .env."
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": API_KEY
    }
    params = {"q": query}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        resultados = response.json()

        titulos = [
            item["title"]
            for item in resultados.get("web", {}).get("results", [])[:limite]
        ]
        return "\n".join(titulos) if titulos else "No se encontraron resultados."

    except requests.RequestException as e:
        return f"Error en la búsqueda: {e}"


def sumar(a: float, b: float) -> float:
    """
    Suma dos números.

    Args:
        a (float): El primer número.
        b (float): El segundo número.

    Returns:
        float: La suma de a y b.

    Ejemplo:
        >>> sumar(3, 5)
        8
    """
    return a + b


def restar(a: float, b: float) -> float:
    """
    Resta el segundo número al primero.

    Args:
        a (float): El primer número.
        b (float): El segundo número.

    Returns:
        float: El resultado de a - b.

    Ejemplo:
        >>> restar(10, 4)
        6
    """
    return a - b


def multiplicar(a: float, b: float) -> float:
    """
    Multiplica dos números.

    Args:
        a (float): El primer número.
        b (float): El segundo número.

    Returns:
        float: El producto de a y b.

    Ejemplo:
        >>> multiplicar(2, 3)
        6
    """
    return a * b


def dividir(a: float, b: float) -> float:
    """
    Divide el primer número entre el segundo.

    Args:
        a (float): El dividendo.
        b (float): El divisor (debe ser distinto de cero).

    Returns:
        float: El resultado de a / b.

    Raises:
        ValueError: Si b es cero.

    Ejemplo:
        >>> dividir(10, 2)
        5.0
    """
    if b == 0:
        raise ValueError("No se puede dividir entre cero.")
    return a / b


def potencia(a: float, b: float) -> float:
    """
    Eleva el primer número a la potencia del segundo.

    Args:
        a (float): La base.
        b (float): El exponente.

    Returns:
        float: El resultado de a elevado a la b.

    Ejemplo:
        >>> potencia(2, 3)
        8
    """
    return a ** b


def modulo(a: float, b: float) -> float:
    """
    Calcula el residuo de la división del primer número entre el segundo.

    Args:
        a (float): El dividendo.
        b (float): El divisor.

    Returns:
        float: El residuo de a dividido por b.

    Raises:
        ValueError: Si b es cero.

    Ejemplo:
        >>> modulo(10, 3)
        1
    """
    if b == 0:
        raise ValueError("No se puede calcular el módulo con divisor cero.")
    return a % b
