from typing import List

from pydantic import BaseModel

from app.models.dte import (
    Extension,
    ItemApendice,
    ReceptorFE,
)

from app.schemas.item_api import ItemAPIFE
from app.schemas.resumen_api import ResumenAPIFE


class FacturaElectronicaAPI(BaseModel):
    receptor: ReceptorFE
    cuerpoDocumento: List[ItemAPIFE]
    documentoRelacionado: dict | None = None
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    resumen: ResumenAPIFE | None = None
    extension: Extension | None = None
    apendice: List[ItemApendice] | None = None
