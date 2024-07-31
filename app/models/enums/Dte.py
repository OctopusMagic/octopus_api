from enum import Enum


class Dte(str, Enum):
    """[CAT-002] Enum de Documento Tributario Electrónico"""
    FACTURA: str = '01'
    CREDITO_FISCAL: str = '03'
    NOTA_CREDITO: str = '05'
    COMPROBANTE_RETENCION: str = '07'
    EXPORTACION: str = '11'
    SUJETO_EXCLUIDO: str = '14'
