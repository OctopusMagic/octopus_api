from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    EmisorFEX,
    IdentificacionFEX,
    ItemFEX,
    ItemApendice,
    ReceptorFEX,
    ResumenFEX
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class FacturaExportacion(BaseModel):
    identificacion: IdentificacionFEX
    emisor: EmisorFEX
    receptor: ReceptorFEX
    otrosDocumentos: dict | None = None
    ventaTercero: dict | None = None
    cuerpoDocumento: list[ItemFEX]
    resumen: ResumenFEX
    apendice: list[ItemApendice] | None = None


class FacturaExportacionRespuesta(FacturaExportacion):
    respuestaHacienda: dict | None = None
