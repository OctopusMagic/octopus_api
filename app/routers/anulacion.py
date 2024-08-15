from io import StringIO

from fastapi import APIRouter, File, UploadFile, status, HTTPException
from loguru import logger
import pandas as pd

from app import schemas
from app.config.cfg import HACIENDA_ENV
from app.models.dte import DocumentoFirmado
from app.services.generar_dte import generate_anulacion
from app.services.pandas_to_dte import convert_df_to_anulacion
from app.services.recepcion_dte import anular_dte
from app.utils.signing import firmar_documento


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Anular un DTE en Hacienda")
async def create(anulacion: schemas.AnulacionAPI):
    """
    Genera una Anulación con el formato establecido por MH,
    lo firma y la envía a Recepción DTE para su posterior aprobación.
    """
    documento = await generate_anulacion(anulacion)
    documento_firmado: DocumentoFirmado = firmar_documento(documento)

    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await anular_dte(
        ambiente=HACIENDA_ENV,
        idEnvio=1,
        version=2,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=documento.model_dump_json()
    )

    return respuesta_hacienda


@router.post(
    "/txt/",
    status_code=status.HTTP_201_CREATED,
    summary="Anular un DTE en Hacienda desde un archivo TXT")
async def create_from_txt(file: UploadFile = File(...)):
    """
    Genera una Anulación con el formato establecido por MH,
    lo firma y la envía a Recepción DTE para su posterior aprobación.
    """
    content = await file.read()
    string_io = StringIO(content.decode("utf-8"))
    df = pd.read_csv(string_io, sep="|", header=None, dtype={0: str, 9: str, 11: str})
    try:
        anulacion = await convert_df_to_anulacion(df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al convertir el archivo TXT: {e}"
        )
    logger.info(anulacion.model_dump_json())
    documento_firmado = firmar_documento(anulacion)
    
    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await anular_dte(
        ambiente=HACIENDA_ENV,
        idEnvio=1,
        version=2,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=anulacion.model_dump_json()
    )

    return respuesta_hacienda
