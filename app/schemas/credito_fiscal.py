from typing import List

from pydantic import BaseModel

from app.models.dte import (
    Extension,
    ItemApendice,
    ReceptorCCF,
)

from app.schemas.item_api import ItemAPICCF
from app.schemas.resumen_api import ResumenAPICCF


class CreditoFiscalAPI(BaseModel):
    receptor: ReceptorCCF
    cuerpoDocumento: List[ItemAPICCF]
    documentoRelacionado: dict | None = None
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    resumen: ResumenAPICCF | None = None
    extension: Extension | None = None
    apendice: List[ItemApendice] | None = None
