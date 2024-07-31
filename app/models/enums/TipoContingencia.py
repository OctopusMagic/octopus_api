from enum import IntEnum


class TipoContingencia(IntEnum):
    """[CAT-005] Enum de tipo de contingencia"""
    MH_NO_DISPONIBLE: int = 1
    EMISOR_NO_DISPONIBLE: int = 2
    EMISOR_SIN_INTERNET: int = 3
    EMISOR_SIN_ELECTRICIDAD: int = 4
    OTROS: int = 5
