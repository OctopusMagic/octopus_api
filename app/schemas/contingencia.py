from pydantic import BaseModel

class ItemContingenciaAPI(BaseModel):
    codigoGeneracion: str
    tipoDoc: str


class ResumenContingenciaAPI(BaseModel):
    fInicio: str
    fFin: str
    hInicio: str
    hFin: str
    tipoContingencia: int
    motivoContingencia: str


class ContingenciaAPI(BaseModel):
    detalleDTE: list[ItemContingenciaAPI]
    motivo: ResumenContingenciaAPI
