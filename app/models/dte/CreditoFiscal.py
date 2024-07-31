from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    Emisor,
    Extension,
    Identificacion,
    ItemCCF,
    ItemApendice,
    ReceptorCCF,
    ResumenCCF
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class CreditoFiscal(BaseModel):
    identificacion: Identificacion
    documentoRelacionado: dict | None = None
    emisor: Emisor
    receptor: ReceptorCCF
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    cuerpoDocumento: list[ItemCCF]
    resumen: ResumenCCF
    extension: Extension | None = None
    apendice: list[ItemApendice] | None = None


class CreditoFiscalRespuesta(CreditoFiscal):
    respuestaHacienda: dict | None = None
