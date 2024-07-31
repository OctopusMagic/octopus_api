import json

from typing import List
from fastapi import APIRouter, status, HTTPException

from app.models.orm import DTE
from app import schemas


router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.DTE],
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los DTEs")
async def read_all(fecha_inicio: str = None, fecha_fin: str = None):
    if fecha_inicio and fecha_fin:
        return await DTE.filter(fhProcesamiento__gte=fecha_inicio, fhProcesamiento__lte=fecha_fin)
    return await DTE.all().order_by("-fhProcesamiento")


@router.get(
    "/{dte_id}",
    status_code=status.HTTP_200_OK,
    summary="Obtener un DTE por su código de generación")
async def read_one(dte_id: str):
    dte = await DTE.filter(codGeneracion=dte_id).first()
    if not dte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTE no encontrado"
        )
    return dte



@router.get(
    "/statistics/",
    status_code=status.HTTP_200_OK,
    summary="Obtener estadísticas de los DTEs")
async def read_statistics(fecha: str = None):
    if fecha:
        # Convert fecha to datetime 00:00:00 and 23:59:59
        fecha_inicio = f"{fecha} 00:00:00"
        fecha_fin = f"{fecha} 23:59:59"
        dtes = await DTE.filter(fhProcesamiento__gte=fecha_inicio, fhProcesamiento__lte=fecha_fin)
    else:
        dtes = await DTE.all()

    total = len(dtes)
    approved = len([dte for dte in dtes if dte.estado == "PROCESADO"])
    contingencia = len([dte for dte in dtes if dte.estado == "CONTINGENCIA"])
    anulado = len([dte for dte in dtes if dte.estado == "ANULADO"])
    rechazado = len([dte for dte in dtes if dte.estado == "RECHAZADO"])
    total_facturado = 0
    for dte in dtes:
        if dte.estado == "PROCESADO":
            documento = json.loads(dte.documento)
            total_facturado += documento['resumen'].get("totalPagar", 0)
    
    return {
        "total": total,
        "approved": approved,
        "rejected": rechazado,
        "anulado": anulado,
        "contingencia": contingencia,
        "total_facturado": total_facturado,
    }
