from typing import List

from pydantic import BaseModel

from app.models.dte import (
    ItemApendice,
    ReceptorFSE,
)

from app.schemas.item_api import ItemAPIFSE
from app.schemas.resumen_api import ResumenAPIFSE


class FacturaSujetoExcluidoAPI(BaseModel):
    sujetoExcluido: ReceptorFSE
    cuerpoDocumento: List[ItemAPIFSE]
    resumen: ResumenAPIFSE | None = None
    apendice: List[ItemApendice] | None = None
