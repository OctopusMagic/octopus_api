from app.routers.datos_empresa import router as datos_empresa_router
from app.routers.comprobante_retencion import router as comprobante_retencion_router
from app.routers.credito_fiscal import router as credito_fiscal_router
from app.routers.factura_electronica import router as factura_electronica_router  # noqa: E501
from app.routers.factura_exportacion import router as factura_exportacion_router  # noqa: E501
from app.routers.sujeto_excluido import router as sujeto_excluido_router
from app.routers.anulacion import router as anulacion_router
from app.routers.nota_credito import router as nota_credito_router
from app.routers.dtes import router as dtes_router
from app.routers.contingencia import router as contingencia_router

from app.routers.mailer import router as mailer_router

from app.utils.api.router import TypedAPIRouter

datos_empresa_router = TypedAPIRouter(
    router=datos_empresa_router,
    prefix="/datos_empresa",
    tags=["Datos de la Empresa"])
factura_electronica_router = TypedAPIRouter(
    router=factura_electronica_router,
    prefix="/factura",
    tags=["Factura Electrónica"])
credito_fiscal_router = TypedAPIRouter(
    router=credito_fiscal_router,
    prefix="/credito_fiscal",
    tags=["Comprobante de Crédito Fiscal"])
factura_exportacion_router = TypedAPIRouter(
    router=factura_exportacion_router,
    prefix="/factura_exportacion",
    tags=["Factura de Exportación"])
dtes_router = TypedAPIRouter(
    router=dtes_router,
    prefix="/dtes",
    tags=["Consulta de DTEs"])
sujeto_excluido_router = TypedAPIRouter(
    router=sujeto_excluido_router,
    prefix="/sujeto_excluido",
    tags=["Factura Sujeto Excluido"])
mailer_router = TypedAPIRouter(
    router=mailer_router,
    prefix="/mailer",
    tags=["Correo Electrónico"])
comprobante_retencion_router = TypedAPIRouter(
    router=comprobante_retencion_router,
    prefix="/comprobante_retencion",
    tags=["Comprobante de Retención"])
anulacion_router = TypedAPIRouter(
    router=anulacion_router,
    prefix="/anulacion",
    tags=["Anulación de DTEs"])
nota_credito_router = TypedAPIRouter(
    router=nota_credito_router,
    prefix="/nota_credito",
    tags=["Nota de Crédito"])
contingencia_router = TypedAPIRouter(
    router=contingencia_router,
    prefix="/contingencia",
    tags=["Contingencia"])