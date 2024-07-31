from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class DocumentoRelacionado(BaseModel):
    tipoDocumento: str
    tipoGeneracion: int
    numeroDocumento: str
    fechaEmision: str
