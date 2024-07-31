from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    EmisorFSE,
    Identificacion,
    ItemFSE,
    ItemApendice,
    ReceptorFSE,
    ResumenFSE,
)

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class FacturaSujetoExcluido(BaseModel):
    identificacion: Identificacion
    emisor: EmisorFSE
    sujetoExcluido: ReceptorFSE
    cuerpoDocumento: list[ItemFSE]
    resumen: ResumenFSE
    apendice: list[ItemApendice] | None = None

class FacturaSujetoExcluidoRespuesta(FacturaSujetoExcluido):
    respuestaHacienda: dict | None = None
