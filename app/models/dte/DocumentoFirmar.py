from pydantic import BaseModel


class DocumentoFirmar(BaseModel):

    contentType: str = "application/JSON",
    nit: str
    activo: bool = True
    passwordPri: str
    dteJson: dict


class DocumentoFirmado(BaseModel):
    status: str
    body: str
