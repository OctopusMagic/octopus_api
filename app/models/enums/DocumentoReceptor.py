from enum import Enum


class DocumentoReceptor(str, Enum):

    CARNET_RESIDENTE: str = "02"
    PASAPORTE: str = "03"
    DUI: str = "13"
    NIT: str = "36"
    OTRO: str = "37"
