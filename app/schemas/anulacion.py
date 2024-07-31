from pydantic import BaseModel


class DocumentoAnulacionAPI(BaseModel):
    codigoGeneracion: str
    fechaEmision: str
    horaEmision: str
    codigoGeneracionR: str | None = None


class MotivoAnulacionAPI(BaseModel):
    tipoAnulacion: int
    motivoAnulacion: str
    nombreResponsable: str
    tipoDocResponsable: str
    numDocResponsable: str
    nombreSolicita: str
    tipoDocSolicita: str
    numDocSolicita: str


class AnulacionAPI(BaseModel):
    documento: DocumentoAnulacionAPI
    motivo: MotivoAnulacionAPI
