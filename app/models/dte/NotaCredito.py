from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    DocumentoRelacionado,
    EmisorNC,
    Extension,
    Identificacion,
    ItemNC,
    ItemApendice,
    ReceptorCCF,
    ResumenNC,
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class NotaCredito(BaseModel):
    identificacion: Identificacion
    documentoRelacionado: list[DocumentoRelacionado]
    emisor: EmisorNC
    receptor: ReceptorCCF
    ventaTercero: dict | None = None
    cuerpoDocumento: list[ItemNC]
    resumen: ResumenNC
    extension: Extension | None = None
    apendice: list[ItemApendice] | None = None


class NotaCreditoRespuesta(NotaCredito):
    respuestaHacienda: dict | None = None
