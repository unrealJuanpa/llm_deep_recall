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
