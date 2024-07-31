from pydantic import BaseModel


class Tributo(BaseModel):
    codigo: str
    descripcion: str
    valor: float
