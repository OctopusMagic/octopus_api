from typing import List

from fastapi import APIRouter, status, Response

from app.models.orm import DatosEmpresa
from app import schemas


router = APIRouter()


@router.get(
    "/",
    response_model=List[schemas.DatosEmpresa],
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las empresas")
async def read_all():
    return await DatosEmpresa.all()


@router.get("/{id}", response_model=schemas.DatosEmpresa)
async def read_one(id: int):
    empresa = await DatosEmpresa.get(id=id).first()
    if not empresa:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return empresa


@router.post(
    "/",
    response_model=schemas.DatosEmpresa,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una empresa")
async def create(empresa: schemas.DatosEmpresaCreate):
    empresa_in_db = await DatosEmpresa.filter(nombre=empresa.nombre).first()
    if empresa_in_db:
        return Response(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "Ya existe una empresa con ese nombre"},
        )
    empresa = await DatosEmpresa.create(**empresa.model_dump())
    return empresa


@router.put(
    "/{id}",
    response_model=schemas.DatosEmpresa,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una empresa")
async def update(id: int, empresa: schemas.DatosEmpresaUpdate):
    empresa_in_db = await DatosEmpresa.get(id=id).first()
    if not empresa_in_db:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    await empresa_in_db.update_from_dict(empresa.model_dump()).save()
    return empresa_in_db
