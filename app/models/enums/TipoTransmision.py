from enum import IntEnum


class TipoTransmision(IntEnum):
    """[CAT-004] Enum de tipo de transmisión"""
    NORMAL: int = 1
    CONTINGENCIA: int = 2
