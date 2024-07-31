from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    EmisorCRE,
    Extension,
    Identificacion,
    ItemApendice,
    ItemCRE,
    ReceptorCRE,
    ResumenCRE
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class ComprobanteRetencion(BaseModel):
    identificacion: Identificacion
    emisor: EmisorCRE
    receptor: ReceptorCRE
    cuerpoDocumento: list[ItemCRE]
    resumen: ResumenCRE
    extension: Extension | None = None
    apendice: list[ItemApendice] | None = None


class ComprobanteRetencionRespuesta(ComprobanteRetencion):
    respuestaHacienda: dict | None = None
