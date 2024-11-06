from io import StringIO
import time

from fastapi import APIRouter, File, UploadFile, status, HTTPException
import pandas as pd

from app import schemas
from app.config.cfg import HACIENDA_ENV
from app.models.enums import Dte
from app.models.dte import DocumentoFirmado
from app.services.generar_dte import generate_factura_exportacion
from app.services.pandas_to_dte import convert_df_to_fex
from app.services.recepcion_dte import recepcion_dte
from app.utils.signing import firmar_documento


router = APIRouter()


@router.post(
    "/",
    response_model=schemas.DTESchema,
    status_code=status.HTTP_201_CREATED,
    summary="Generar Factura de Exportación y enviar a Hacienda")
async def create(factura: schemas.FacturaExportacionAPI):
    """
    Genera una Factura de Exportación con el formato establecido por MH,
    la firma y la envía a Recepción DTE para su posterior aprobación.
    """
    documento = await generate_factura_exportacion(
        factura,
        int(time.time())
    )
    documento_firmado: DocumentoFirmado = firmar_documento(documento)

    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await recepcion_dte(
        codGeneracion=documento.identificacion.codigoGeneracion,
        ambiente=HACIENDA_ENV,
        idEnvio=1,
        version=1,
        tipoDte=Dte.EXPORTACION,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=documento.model_dump_json()
    )

    return respuesta_hacienda


@router.post(
    "/txt/",
    response_model=schemas.DTESchemaTXT,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar Factura de Exportación a Hacienda desde un archivo TXT"
    )
async def create_from_txt(file: UploadFile = File(...)):
    content = await file.read()
    string_io = StringIO(content.decode("utf-8", errors="ignore"))
    df = pd.read_csv(string_io, sep="|", header=None, dtype={0: str, 2: str, 23: str, 30: str})
    try:
        fex, correlativo = await convert_df_to_fex(df)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al convertir el archivo TXT: {e}"
        )
    documento_firmado: DocumentoFirmado = firmar_documento(fex)

    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await recepcion_dte(
        codGeneracion=fex.identificacion.codigoGeneracion,
        ambiente=HACIENDA_ENV,
        idEnvio=1,
        version=1,
        tipoDte=Dte.EXPORTACION,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=fex.model_dump_json()
    )

    respuesta = schemas.DTESchemaTXT(
        codGeneracion=respuesta_hacienda.codGeneracion,
        selloRecibido=respuesta_hacienda.selloRecibido,
        estado=respuesta_hacienda.estado,
        documento=respuesta_hacienda.documento,
        fhProcesamiento=respuesta_hacienda.fhProcesamiento,
        observaciones=respuesta_hacienda.observaciones,
        tipo_dte=respuesta_hacienda.tipo_dte,
        enlace_pdf=respuesta_hacienda.enlace_pdf,
        enlace_json=respuesta_hacienda.enlace_json,
        enlace_rtf=respuesta_hacienda.enlace_rtf,
        codigo_serie=correlativo
    )

    return respuesta