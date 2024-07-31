from typing import Optional

from pydantic import BaseModel


class DatosEmpresaBase(BaseModel):
    nombre: Optional[str]
    nit: Optional[str]
    nrc: Optional[str]
    codActividad: Optional[str]
    descActividad: Optional[str]
    nombreComercial: Optional[str]
    tipoEstablecimiento: Optional[str]
    departamento: Optional[str]
    municipio: Optional[str]
    complemento: Optional[str]
    telefono: Optional[str]
    correo: Optional[str]
    codEstableMH: Optional[str]
    codEstable: Optional[str]
    codPuntoVentaMH: Optional[str]
    codPuntoVenta: Optional[str]


class DatosEmpresaCreate(DatosEmpresaBase):
    nombre: str
    nit: str
    nrc: str
    codActividad: str
    descActividad: str
    nombreComercial: str
    tipoEstablecimiento: str
    departamento: str
    municipio: str
    complemento: str
    telefono: str
    correo: str
    codEstableMH: Optional[str]
    codEstable: str
    codPuntoVentaMH: Optional[str]
    codPuntoVenta: str


class DatosEmpresaUpdate(DatosEmpresaBase):
    pass


class DatosEmpresaInDB(DatosEmpresaBase):
    id: int

    class ConfigDict:
        from_attributes = True


class DatosEmpresa(DatosEmpresaInDB):
    pass
