from typing import List

from pydantic import BaseModel


class RespuestaHacienda(BaseModel):
    version: int | None = None
    ambiente: str | None = None
    versionApp: int | None = None
    estado: str | None = None
    codigoGeneracion: str | None = None
    selloRecibido: str | None = None
    fhProcesamiento: str | None = None
    clasificaMsg: str | None = None
    codigoMsg: str | None = None
    descripcionMsg: str | None = None
    observaciones: List[str] | None = None
