from enum import Enum


class Ambientes(str, Enum):
    """[CAT-001] Enum de ambientes del sistema"""
    PRUEBA: str = '00'
    PRODUCCION: str = '01'
