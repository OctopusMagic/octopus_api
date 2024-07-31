from pydantic import BaseModel


class ResumenAPIBase(BaseModel):
    descuNoSuj: float = 0
    descuExtenta: float = 0
    descuGravada: float = 0
    porcentajeDescuento: float = 0
    ivaRete1: float = 0
    reteRenta: float = 0
    saldoFavor: float = 0
    condicionOperacion: int = 1


class ResumenAPIFE(ResumenAPIBase):
    pass


class ResumenAPICCF(ResumenAPIBase):
    ivaPerci1: float = 0


class ResumenAPIFEX(BaseModel):
    porcentajeDescuento: float = 0
    condicionOperacion: int = 1
    codIncoterms: str | None = None
    descIncoterms: str | None = None
    flete: float = 0
    seguro: float = 0
    descuento: float = 0


class ResumenAPIFSE(BaseModel):
    totalCompra: float = 0
    descu: float
    totalDescu: float
    subTotal: float = 0
    ivaRete1: float
    reteRenta: float = 0
    totalPagar: float = 0
    condicionOperacion: int = 1
    pagos: list | None = None
    observaciones: str | None = None


class ResumenAPICRE(BaseModel):
    totalSujetoRetencion: float
    totalIVAretenido: float
