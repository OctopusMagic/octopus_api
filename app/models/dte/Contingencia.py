from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    EmisorContingencia,
    IdentificacionContingencia,
    ItemContingencia,
    ResumenContingencia
)

class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class Contingencia(BaseModel):
    identificacion: IdentificacionContingencia
    emisor: EmisorContingencia
    detalleDTE: list[ItemContingencia]
    motivo: ResumenContingencia
