from typing import List

from pydantic import BaseModel

from app.models.dte import (
    Extension,
    ItemApendice,
    ReceptorCCF,
    DocumentoRelacionado,
    ItemNC,
)

from app.schemas.resumen_api import ResumenAPICCF

class NotaCreditoAPI(BaseModel):
    receptor: ReceptorCCF
    cuerpoDocumento: List[ItemNC]
    documentoRelacionado: List[DocumentoRelacionado]
    ventaTercero: dict | None = None
    resumen: ResumenAPICCF | None = None
    extension: Extension | None = None
    apendice: List[ItemApendice] | None = None
