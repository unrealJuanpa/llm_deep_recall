import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()
API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")

def obtener_contenido_url(url: str) -> str:
    """
    Realiza una solicitud HTTP GET a la URL dada y devuelve el contenido de la respuesta como texto.

    Args:
        url (str): Dirección URL a consultar.

    Returns:
        str: Contenido de la página o mensaje de error.
    """
    try:
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        return respuesta.text
    except requests.RequestException as e:
        return f"Error al acceder a la URL: {e}"

def buscar_en_internet(query: str, limite: int = 3) -> str:
    """
    Consulta Brave Search API y devuelve los primeros resultados con título, URL,
    descripción y contenido HTML completo de cada página encontrada.
    No sobrepasar el limite de 3 resultados.

    Args:
        query (str): Texto a buscar.
        limite (int): Número máximo de resultados a mostrar (por defecto 3).

    Returns:
        str: Resultados formateados o mensaje de error.
    """
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
        items = resultados.get("web", {}).get("results", [])[:limite]

        if not items:
            return "No se encontraron resultados."

        salida = []
        for i, item in enumerate(items, 1):
            titulo = item.get("title", "Sin título")
            url_res = item.get("url", "Sin URL")
            snippet = item.get("description", "Sin descripción")
            contenido = obtener_contenido_url(url_res)
            salida.append(f"{i}. {titulo}\nURL: {url_res}\nDescripción: {snippet}\nContenido:\n{contenido[:1000]}...\n")

        return "\n".join(salida)

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

def obtener_fecha_hora_actual(a: float, b: float) -> float:
    """
    Obtiene la fecha y hora completa del sistema.

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


def obtener_fecha_hora_actual() -> str:
    """
    Obtiene la fecha y hora actual del sistema en formato ISO 8601.

    Returns:
        str: Fecha y hora actual (ej. '2025-06-21T05:30:00').
    """
    return datetime.now().isoformat()


def calcular_distancia_en_anios(anio: int) -> int:
    """
    Calcula la diferencia en años entre el año actual y un año dado.

    Args:
        anio (int): Año con el que se quiere comparar (por ejemplo, 1990).

    Returns:
        int: Diferencia en años. Positivo si es pasado, negativo si es futuro, 0 si es el mismo año.

    Raises:
        ValueError: Si el año proporcionado es negativo.
    
    Ejemplo:
        >>> calcular_distancia_en_anios(2000)
        25  # si el año actual es 2025
    """
    if anio < 0:
        raise ValueError("El año no puede ser negativo.")
    
    anio_actual = datetime.now().year
    return anio_actual - anio
