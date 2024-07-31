from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app import schemas
from app.config.cfg import NIT
from app.models.dte import DocumentoFirmado
from app.models.orm import DTE
from app.schemas.contingencia import ItemContingenciaAPI, ResumenContingenciaAPI
from app.services.generar_dte import generate_contingencia
# from app.services.pandas_to_dte import convert_df_to_contingencia
from app.services.recepcion_dte import contingencia_dte
from app.utils.signing import firmar_documento
from datetime import timedelta


router = APIRouter()


@router.post(
    "/manual",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar DTE en Contingencia a Hacienda")
async def create(contingencia: schemas.ContingenciaAPI):
    """
    Genera un DTE en Contingencia con el formato establecido por MH,
    lo firma y lo envía a Recepción DTE para su posterior aprobación.
    """
    documento = await generate_contingencia(contingencia)
    documento_firmado: DocumentoFirmado = firmar_documento(documento)

    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await contingencia_dte(
        nit=NIT,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=documento.model_dump_json()
    )

    return respuesta_hacienda


@router.post(
    "/auto",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar DTE en Contingencia a Hacienda")
async def create_auto():
    """
    Revisa la base de datos de DTEs en Contingencia y envía los que
    no han sido enviados a Hacienda.
    """
    dtes_contingencia = await DTE.filter(
        estado="CONTINGENCIA",
    ).order_by("fhProcesamiento").all()

    if not dtes_contingencia:
        return JSONResponse(
            content={
                "status": "success",
                "message": "No hay DTES en Contingencia"
            },
            status_code=200
        )

    items_contingencia = []
    for dte in dtes_contingencia:
        items_contingencia.append(ItemContingenciaAPI(
            codigoGeneracion=dte.codGeneracion,
            tipoDoc=dte.tipo_dte,
        ))

    fInicio = dtes_contingencia[0].fhProcesamiento.strftime("%Y-%m-%d")
    fFin = dtes_contingencia[-1].fhProcesamiento.strftime("%Y-%m-%d")
    hInicio = (dtes_contingencia[0].fhProcesamiento - timedelta(minutes=5)).strftime("%H:%M:%S")
    hFin = (dtes_contingencia[-1].fhProcesamiento + timedelta(minutes=5)).strftime("%H:%M:%S")

    contingencia = schemas.ContingenciaAPI(
        detalleDTE=items_contingencia,
        motivo=ResumenContingenciaAPI(
            fInicio=fInicio,
            fFin=fFin,
            hInicio=hInicio,
            hFin=hFin,
            tipoContingencia=1,
            motivoContingencia="Ministerio de Hacienda no responde",
        )
    )

    documento = await generate_contingencia(contingencia)
    documento_firmado: DocumentoFirmado = firmar_documento(documento)

    if not documento_firmado.status == "OK":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=documento_firmado.body
        )

    respuesta_hacienda = await contingencia_dte(
        nit=NIT,
        documento_firmado=documento_firmado.body,
        documento_sin_firma=documento.model_dump_json()
    )

    return respuesta_hacienda
