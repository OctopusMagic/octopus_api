from math import modf

from num2words import num2words


def total_en_letras(total: float):
    """Convierte un total númerico a su equivalente en letras."""
    totalDecimal, totalEntero = modf(total)
    totalDecimal = int(round(totalDecimal * 100, 0))
    dolares = num2words(
        totalEntero,
        lang="es",
        to="currency",
        currency="USD"
    ).upper()
    dolares = dolares.replace("CON CERO CENTAVOS", "")
    return dolares + str(totalDecimal) + "/100 USD"
