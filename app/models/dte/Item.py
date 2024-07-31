from typing import List

from pydantic import BaseModel


class ItemBase(BaseModel):
    numItem: int
    tipoItem: int
    numeroDocumento: str | None = None
    cantidad: float
    codigo: str | None = None
    codTributo: str | None = None
    uniMedida: int
    descripcion: str
    precioUni: float
    montoDescu: float
    ventaNoSuj: float
    ventaExenta: float
    ventaGravada: float
    tributos: List[str] | None = None
    psv: float
    noGravado: float


class ItemFE(ItemBase):
    ivaItem: float


class ItemCCF(ItemBase):
    pass


class ItemFEX(BaseModel):
    numItem: int
    cantidad: float
    codigo: str | None = None
    uniMedida: int
    descripcion: str
    precioUni: float
    montoDescu: float
    ventaGravada: float
    tributos: List[str] | None = None
    noGravado: float


class ItemFSE(BaseModel):
    tipoItem: int
    numItem: int
    cantidad: float
    codigo: str | None = None
    uniMedida: int
    descripcion: str
    precioUni: float
    montoDescu: float
    compra: float


class ItemCRE(BaseModel):
    numItem: int
    tipoDte: str
    tipoDoc: int
    numDocumento: str
    fechaEmision: str
    montoSujetoGrav: float
    codigoRetencionMH: str
    ivaRetenido: float
    descripcion: str


class ItemNC(BaseModel):
    numItem: int
    tipoItem: int
    numeroDocumento: str
    cantidad: float
    codigo: str | None = None
    codTributo: str | None = None
    uniMedida: int
    descripcion: str
    precioUni: float
    montoDescu: float
    ventaNoSuj: float
    ventaExenta: float
    ventaGravada: float
    tributos: List[str] | None = None


class ItemContingencia(BaseModel):
    noItem: int
    codigoGeneracion: str
    tipoDoc: str
