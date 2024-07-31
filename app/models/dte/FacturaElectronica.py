from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    Emisor,
    Extension,
    Identificacion,
    ItemFE,
    ItemApendice,
    ReceptorFE,
    ResumenFE,
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class FacturaElectronica(BaseModel):
    identificacion: Identificacion
    documentoRelacionado: dict | None = None
    emisor: Emisor
    receptor: ReceptorFE
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    cuerpoDocumento: list[ItemFE]
    resumen: ResumenFE
    extension: Extension | None = None
    apendice: list[ItemApendice] | None = None


class FacturaElectronicaRespuesta(FacturaElectronica):
    respuestaHacienda: dict | None = None
