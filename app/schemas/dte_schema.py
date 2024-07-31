from datetime import datetime

from pydantic import BaseModel


class DTESchema(BaseModel):
    codGeneracion: str
    selloRecibido: str | None
    estado: str
    documento: str
    fhProcesamiento: datetime | None
    observaciones: str | None
    tipo_dte: str
    enlace_pdf: str
    enlace_json: str
    enlace_rtf: str


class DTE(BaseModel):
    id: int
    codGeneracion: str
    selloRecibido: str | None
    estado: str
    documento: str
    fhProcesamiento: datetime | None
    observaciones: str | None
    tipo_dte: str

    @property
    def enlace_pdf(self) -> str:
        return f"https://octopus-dtes.s3.amazonaws.com/{self.tipo_dte}/{self.codGeneracion}.pdf"

    @property
    def enlace_json(self) -> str:
        return f"https://octopus-dtes.s3.amazonaws.com/{self.tipo_dte}/{self.codGeneracion}.json"


class DTESchemaTXT(BaseModel):
    codGeneracion: str
    selloRecibido: str | None
    estado: str
    documento: str
    fhProcesamiento: datetime | None
    observaciones: str | None
    tipo_dte: str
    enlace_pdf: str
    enlace_json: str
    enlace_rtf: str
    codigo_serie: str
