from typing import List

from pydantic import BaseModel

from app.models.dte import (
    Extension,
    ItemApendice,
    ReceptorCRE,
)
from app.schemas.item_api import ItemAPICRE
from app.schemas.resumen_api import ResumenAPICRE

class ComprobanteRetencionAPI(BaseModel):
    receptor: ReceptorCRE
    cuerpoDocumento: List[ItemAPICRE]
    resumen: ResumenAPICRE
    extension: Extension | None = None
    apendice: List[ItemApendice] | None = None
