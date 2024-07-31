from enum import IntEnum


class TipoItem(IntEnum):
    """[CAT-011] Enum de tipo de item"""
    BIENES: int = 1
    SERVICIO: int = 2
    AMBOS: int = 3
    OTROS: int = 4
