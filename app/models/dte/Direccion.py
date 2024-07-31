from pydantic import BaseModel


class Direccion(BaseModel):
    departamento: str
    municipio: str
    complemento: str
