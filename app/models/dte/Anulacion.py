from pydantic import BaseModel as PydanticBaseModel

from app.models.dte import (
    EmisorAnulacion,
    IdentificacionAnulacion
)


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class DocumentoAnulacion(BaseModel):
    tipoDte: str
    codigoGeneracion: str
    selloRecibido: str
    numeroControl: str
    fecEmi: str
    montoIva: float | None = None
    codigoGeneracionR: str | None = None
    tipoDocumento: str | None = None
    numDocumento: str | None = None
    nombre: str | None = None
    telefono: str | None = None
    correo: str | None = None


class MotivoAnulacion(BaseModel):
    tipoAnulacion: int
    motivoAnulacion: str
    nombreResponsable: str
    tipDocResponsable: str
    numDocResponsable: str
    nombreSolicita: str
    tipDocSolicita: str
    numDocSolicita: str


class Anulacion(BaseModel):
    identificacion: IdentificacionAnulacion
    emisor: EmisorAnulacion
    documento: DocumentoAnulacion
    motivo: MotivoAnulacion
