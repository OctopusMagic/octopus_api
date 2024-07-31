from pydantic import BaseModel, EmailStr

from app.models.enums import DocumentoReceptor, TipoPersona
from app.models.dte.Direccion import Direccion


class ReceptorBase(BaseModel):
    nrc: str | None = None
    nombre: str | None = None
    codActividad: str | None = None
    descActividad: str | None = None
    direccion: Direccion | None = None
    telefono: str | None = None
    correo: EmailStr | None = None


class ReceptorFE(ReceptorBase):
    tipoDocumento: DocumentoReceptor | None = DocumentoReceptor.DUI
    numDocumento: str | None = None


class ReceptorCCF(ReceptorBase):
    nit: str
    nrc: str
    nombreComercial: str | None = None


class ReceptorFEX(BaseModel):
    tipoDocumento: DocumentoReceptor = DocumentoReceptor.OTRO
    numDocumento: str
    nombre: str
    descActividad: str
    codPais: str
    nombrePais: str
    complemento: str
    nombreComercial: str
    tipoPersona: TipoPersona = TipoPersona.NATURAL
    telefono: str
    correo: EmailStr


class ReceptorFSE(BaseModel):
    tipoDocumento: DocumentoReceptor = DocumentoReceptor.DUI
    numDocumento: str
    nombre: str
    codActividad: str | None = None
    descActividad: str | None = None
    direccion: Direccion
    telefono: str
    correo: EmailStr


class ReceptorCRE(BaseModel):
    tipoDocumento: DocumentoReceptor = DocumentoReceptor.DUI
    numDocumento: str
    nrc: str | None = None
    nombre: str
    nombreComercial: str | None = None
    codActividad: str | None = None
    descActividad: str | None = None
    direccion: Direccion
    telefono: str | None = None
    correo: EmailStr