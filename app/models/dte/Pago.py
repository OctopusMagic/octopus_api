from pydantic import BaseModel


class Pago(BaseModel):
    codigo: str
    montoPago: float
    referencia: str | None = None
    plazo: str | None = None
    periodo: float | None = None
