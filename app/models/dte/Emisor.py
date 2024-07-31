from pydantic import BaseModel, EmailStr

from app.models.dte.Direccion import Direccion


class Emisor(BaseModel):
    nit: str
    nrc: str
    nombre: str
    codActividad: str
    descActividad: str
    nombreComercial: str
    tipoEstablecimiento: str
    direccion: Direccion
    telefono: str
    correo: EmailStr
    codEstableMH: str | None = None
    codEstable: str | None = None
    codPuntoVentaMH: str | None = None
    codPuntoVenta: str | None = None


class EmisorFEX(Emisor):
    regimen: str
    recintoFiscal: str
    tipoItemExpor: int


class EmisorFSE(BaseModel):
    nit: str
    nrc: str
    nombre: str
    codActividad: str
    descActividad: str
    direccion: Direccion
    telefono: str
    correo: EmailStr
    codEstableMH: str | None = None
    codEstable: str | None = None
    codPuntoVentaMH: str | None = None
    codPuntoVenta: str | None = None


class EmisorCRE(BaseModel):
    nit: str
    nrc: str
    nombre: str
    codActividad: str
    descActividad: str
    nombreComercial: str
    tipoEstablecimiento: str
    direccion: Direccion
    telefono: str
    codigoMH: str | None = None
    codigo: str | None = None
    puntoVentaMH: str | None = None
    puntoVenta: str | None = None
    correo: EmailStr


class EmisorAnulacion(BaseModel):
    nit: str
    nombre: str
    tipoEstablecimiento: str
    nomEstablecimiento: str
    codEstableMH: str | None = None
    codEstable: str | None = None
    codPuntoVentaMH: str | None = None
    codPuntoVenta: str | None = None
    telefono: str
    correo: EmailStr


class EmisorNC(BaseModel):
    nit: str
    nrc: str
    nombre: str
    codActividad: str
    descActividad: str
    nombreComercial: str
    tipoEstablecimiento: str
    direccion: Direccion
    telefono: str
    correo: EmailStr


class EmisorContingencia(BaseModel):
    nit: str
    nombre: str
    nombreResponsable: str
    tipoDocResponsable: str
    numeroDocResponsable: str
    tipoEstablecimiento: str
    codEstableMH: str | None = None
    codPuntoVenta: str | None = None
    telefono: str
    correo: EmailStr
