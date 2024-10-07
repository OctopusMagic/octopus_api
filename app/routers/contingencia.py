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
from app.utils.contingencia import obtener_contingencia, activar_contingencia, desactivar_contingencia
from app.utils.signing import firmar_documento
from app.utils.dbf_writer import reconciliar_dbf
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


@router.get("/reconciliar")
async def reconciliar(fecha: str):
    fecha_inicio = fecha + " 00:00:00"
    fecha_fin = fecha + " 23:59:59"
    dtes = await DTE.filter(
        fhProcesamiento__gte=fecha_inicio,
        fhProcesamiento__lte=fecha_fin,
    ).all()
    reconciliar_dbf(dtes)
    return JSONResponse(
        content={
            "status": "success",
            "message": "DBF reconciliado"
        },
        status_code=200
    )


@router.get("/activar")
async def activar():
    activar_contingencia()
    return JSONResponse(
        content={
            "status": "success",
            "message": "Contingencia activada"
        },
        status_code=200
    )


@router.get("/desactivar")
async def desactivar():
    desactivar_contingencia()
    return JSONResponse(
        content={
            "status": "success",
            "message": "Contingencia desactivada"
        },
        status_code=200
    )


@router.get("/estado")
async def estado():
    return JSONResponse(
        content={
            "status": "success",
            "message": obtener_contingencia()
        },
        status_code=200
    )
