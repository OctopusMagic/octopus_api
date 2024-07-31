from typing import List

from pydantic import BaseModel

from app.models.dte import (
    ItemApendice,
    ReceptorFEX,
)

from app.schemas.item_api import ItemAPIFEX
from app.schemas.resumen_api import ResumenAPIFEX


class EmisorFEXAPI(BaseModel):
    regimen: str
    recintoFiscal: str
    tipoItemExpor: int


class FacturaExportacionAPI(BaseModel):
    emisor: EmisorFEXAPI
    receptor: ReceptorFEX
    cuerpoDocumento: List[ItemAPIFEX]
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    resumen: ResumenAPIFEX | None = None
    apendice: List[ItemApendice] | None = None
