from pydantic import BaseModel


class ItemApendice(BaseModel):
    campo: str
    etiqueta: str
    valor: str
