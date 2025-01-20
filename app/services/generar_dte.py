from datetime import datetime
import json

from fastapi import HTTPException, status

from app.config.cfg import HACIENDA_ENV
from app.models.dte import (
    Contingencia,
    FacturaElectronica,
    ComprobanteRetencion,
    CreditoFiscal,
    FacturaExportacion,
    Identificacion,
    IdentificacionAnulacion,
    IdentificacionContingencia,
    IdentificacionFEX,
    NotaCredito
)
from app.models import enums
from app.models.dte.Anulacion import Anulacion, DocumentoAnulacion, MotivoAnulacion
from app.models.dte.Emisor import EmisorAnulacion, EmisorContingencia, EmisorNC
from app.models.dte.Item import ItemContingencia
from app.models.dte.Resumen import ResumenContingencia
from app.models.dte.SujetoExcluido import FacturaSujetoExcluido
from app.models.orm import DTE
from app.schemas import (
    FacturaElectronicaAPI,
    CreditoFiscalAPI
)
from app.schemas.anulacion import AnulacionAPI
from app.schemas.contingencia import ContingenciaAPI
from app.schemas.factura_exportacion import FacturaExportacionAPI
from app.schemas.nota_credito import NotaCreditoAPI
from app.schemas.sujeto_excluido import FacturaSujetoExcluidoAPI
from app.schemas.comprobante_retencion import ComprobanteRetencionAPI
from app.services.converters import (
    convert_itemapi_to_itemcre,
    convert_itemapi_to_itemfe,
    convert_itemapi_to_itemccf,
    convert_itemapi_to_itemfex,
    convert_itemapi_to_itemfse
)
from app.services.datos_emisor import get_datos_emisor, get_datos_emisor_cre, get_datos_emisor_fse
from app.services.generar_resumen import (
    generar_resumen_fe,
    generar_resumen_ccf,
    generar_resumen_fex,
    generar_resumen_fse,
    generar_resumen_cre,
    generar_resumen_nc
)
from app.utils.codes import generate_uuid, generate_numero_control


async def generate_factura_electronica(
        factura: FacturaElectronicaAPI,
        correlativo: int) -> FacturaElectronica:
    """Convierte una FacturaElectronicaAPI a FacturaElectronica."""

    items = [
        convert_itemapi_to_itemfe(item, numero)
        for numero, item in enumerate(factura.cuerpoDocumento, start=1)
    ]

    return FacturaElectronica(
        identificacion=Identificacion(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.FACTURA,
            numeroControl=generate_numero_control(
                enums.Dte.FACTURA, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=factura.documentoRelacionado,
        emisor=await get_datos_emisor(),
        receptor=factura.receptor,
        otrosDocumentos=factura.otrosDocumentos,
        ventaTercero=factura.ventaTercero,
        cuerpoDocumento=items,
        resumen=generar_resumen_fe(items, factura.resumen),
        extension=factura.extension,
        apendice=factura.apendice
    )


async def generate_credito_fiscal(
        credito_fiscal: CreditoFiscalAPI,
        correlativo: int) -> CreditoFiscal:
    """Convierte un CreditoFiscalAPI a CreditoFiscal."""
    items = [
        convert_itemapi_to_itemccf(item, numero)
        for numero, item in enumerate(credito_fiscal.cuerpoDocumento, start=1)
    ]

    return CreditoFiscal(
        identificacion=Identificacion(
            version=3,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.CREDITO_FISCAL,
            numeroControl=generate_numero_control(
                enums.Dte.CREDITO_FISCAL, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=credito_fiscal.documentoRelacionado,
        emisor=await get_datos_emisor(),
        receptor=credito_fiscal.receptor,
        otrosDocumentos=credito_fiscal.otrosDocumentos,
        ventaTercero=credito_fiscal.ventaTercero,
        cuerpoDocumento=items,
        resumen=generar_resumen_ccf(items, credito_fiscal.resumen),
        extension=credito_fiscal.extension,
        apendice=credito_fiscal.apendice
    )


async def generate_factura_exportacion(
        factura: FacturaExportacionAPI,
        correlativo: int) -> FacturaExportacion:
    """Convierte una FacturaExportacionAPI a FacturaExportacion."""

    items = [
        convert_itemapi_to_itemfex(item, numero)
        for numero, item in enumerate(factura.cuerpoDocumento, start=1)
    ]

    return FacturaExportacion(
        identificacion=IdentificacionFEX(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.EXPORTACION,
            numeroControl=generate_numero_control(
                enums.Dte.EXPORTACION, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContigencia=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        emisor=await get_datos_emisor(factura.emisor),
        receptor=factura.receptor,
        otrosDocumentos=factura.otrosDocumentos,
        ventaTercero=factura.ventaTercero,
        cuerpoDocumento=items,
        resumen=generar_resumen_fex(items, factura.resumen),
        apendice=factura.apendice
    )


async def generate_factura_sujeto_excluido(
    factura: FacturaSujetoExcluidoAPI,
    correlativo: int) -> FacturaSujetoExcluido:

    items = [
        convert_itemapi_to_itemfse(item, numero)
        for numero, item in enumerate(factura.cuerpoDocumento, start=1)
    ]

    return FacturaSujetoExcluido(
        identificacion=Identificacion(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.SUJETO_EXCLUIDO,
            numeroControl=generate_numero_control(
                enums.Dte.SUJETO_EXCLUIDO, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        emisor=await get_datos_emisor_fse(),
        sujetoExcluido=factura.sujetoExcluido,
        cuerpoDocumento=items,
        resumen=generar_resumen_fse(items, factura.resumen),
        apendice=factura.apendice
    )


async def generate_comprobante_retencion(
    comprobante_retencion: ComprobanteRetencionAPI,
    correlativo: int) -> ComprobanteRetencion:
    """ Convierte un ComprobanteRetencionAPI a ComprobanteRetencion. """
    items = [
        convert_itemapi_to_itemcre(item, numero)
        for numero, item in enumerate(comprobante_retencion.cuerpoDocumento, start=1)
    ]

    return ComprobanteRetencion(
        identificacion=Identificacion(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.COMPROBANTE_RETENCION,
            numeroControl=generate_numero_control(
                enums.Dte.COMPROBANTE_RETENCION, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        emisor=await get_datos_emisor_cre(),
        receptor=comprobante_retencion.receptor,
        cuerpoDocumento=items,
        resumen=generar_resumen_cre(comprobante_retencion.resumen),
        extension=comprobante_retencion.extension,
        apendice=comprobante_retencion.apendice
    )


async def generate_anulacion(anulacion: AnulacionAPI) -> Anulacion:
    emisor = await get_datos_emisor()
    dteAnular = await DTE.filter(codGeneracion=anulacion.documento.codigoGeneracion).first()
    if not dteAnular:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTE no encontrado"
        )
    documento = json.loads(dteAnular.documento)
    
    if documento["identificacion"]["tipoDte"] == "01":
        tipoDocumento = documento["receptor"]["tipoDocumento"] or None
        numDocumento = documento["receptor"]["numDocumento"] or None
    elif documento["identificacion"]["tipoDte"] == "14":
        tipoDocumento = documento["sujetoExcluido"]["tipoDocumento"] or None
        numDocumento = documento["sujetoExcluido"]["numDocumento"] or None
    elif documento["identificacion"]["tipoDte"] == "03":
        tipoDocumento = "36"
        numDocumento = documento["receptor"]["nit"]
    else:
        tipoDocumento = None
        numDocumento = None

    
    return Anulacion(
        identificacion=IdentificacionAnulacion(
            version=2,
            ambiente=HACIENDA_ENV,
            codigoGeneracion=generate_uuid(),
            fecAnula=datetime.now().strftime("%Y-%m-%d"),
            horAnula=datetime.now().strftime("%H:%M:%S"),
        ),
        emisor=EmisorAnulacion(
            nit=emisor.nit,
            nombre=emisor.nombre,
            tipoEstablecimiento=emisor.tipoEstablecimiento,
            nomEstablecimiento=emisor.nombreComercial,
            codEstableMH=emisor.codEstableMH,
            codEstable=emisor.codEstable,
            codPuntoVentaMH=emisor.codPuntoVentaMH,
            codPuntoVenta=emisor.codPuntoVenta,
            telefono=emisor.telefono,
            correo=emisor.correo
        ),
        documento=DocumentoAnulacion(
            tipoDte=dteAnular.tipo_dte,
            codigoGeneracion=dteAnular.codGeneracion,
            selloRecibido=dteAnular.selloRecibido,
            numeroControl=documento["identificacion"]["numeroControl"],
            fecEmi=documento["identificacion"]["fecEmi"],
            montoIva=None,
            codigoGeneracionR=anulacion.documento.codigoGeneracionR,
            tipoDocumento=tipoDocumento,
            numDocumento=numDocumento,
            nombre=documento["receptor"]["nombre"] or None,
            telefono=documento["receptor"]["telefono"] or None,
            correo=documento["receptor"]["correo"] or None,
        ),
        motivo=MotivoAnulacion(
            tipoAnulacion=anulacion.motivo.tipoAnulacion,
            motivoAnulacion=anulacion.motivo.motivoAnulacion,
            nombreResponsable=anulacion.motivo.nombreResponsable,
            tipDocResponsable=anulacion.motivo.tipoDocResponsable,
            numDocResponsable=anulacion.motivo.numDocResponsable,
            nombreSolicita=anulacion.motivo.nombreSolicita,
            tipDocSolicita=anulacion.motivo.tipoDocSolicita,
            numDocSolicita=anulacion.motivo.numDocSolicita
        )
    )


async def generate_nota_credito(
    nota_credito: NotaCreditoAPI,
    correlativo: int) -> NotaCredito:
    """Convierte una NotaCreditoAPI a NotaCredito."""
    emisor = await get_datos_emisor()
    return NotaCredito(
        identificacion=Identificacion(
            version=3,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.NOTA_CREDITO,
            numeroControl=generate_numero_control(
                enums.Dte.NOTA_CREDITO, correlativo
            ),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=nota_credito.documentoRelacionado,
        emisor=EmisorNC(
            nit=emisor.nit,
            nrc=emisor.nrc,
            nombre=emisor.nombre,
            codActividad=emisor.codActividad,
            descActividad=emisor.descActividad,
            nombreComercial=emisor.nombreComercial,
            tipoEstablecimiento=emisor.tipoEstablecimiento,
            direccion=emisor.direccion,
            telefono=emisor.telefono,
            correo=emisor.correo
        ),
        receptor=nota_credito.receptor,
        ventaTercero=nota_credito.ventaTercero,
        cuerpoDocumento=nota_credito.cuerpoDocumento,
        resumen=generar_resumen_nc(nota_credito.cuerpoDocumento, nota_credito.resumen),
        extension=nota_credito.extension,
        apendice=nota_credito.apendice
    )


async def generate_contingencia(contingencia: ContingenciaAPI) -> Contingencia:
    emisor = await get_datos_emisor()
    dtes_contingencia = []

    noItem = 1
    for dte in contingencia.detalleDTE:
        dteContingencia = await DTE.filter(codGeneracion=dte.codigoGeneracion).first()
        if not dteContingencia:
            continue
        if dteContingencia.estado == "PROCESADO":
            continue

        dtes_contingencia.append(ItemContingencia(
            noItem=noItem,
            tipoDoc=dteContingencia.tipo_dte,
            codigoGeneracion=dte.codigoGeneracion,
        ))
        noItem += 1

    return Contingencia(
        identificacion=IdentificacionContingencia(
            version=3,
            ambiente=HACIENDA_ENV,
            codigoGeneracion=generate_uuid(),
            fTransmision=datetime.now().strftime("%Y-%m-%d"),
            hTransmision=datetime.now().strftime("%H:%M:%S"),
        ),
        emisor=EmisorContingencia(
            nit=emisor.nit,
            nombre=emisor.nombre,
            nombreResponsable=emisor.nombre,
            tipoDocResponsable="37",
            numeroDocResponsable=emisor.nit,
            tipoEstablecimiento=emisor.tipoEstablecimiento,
            codEstableMH=emisor.codEstableMH,
            codPuntoVenta=emisor.codPuntoVenta,
            telefono=emisor.telefono,
            correo=emisor.correo
        ),
        detalleDTE=dtes_contingencia,
        motivo=ResumenContingencia(
            fInicio=contingencia.motivo.fInicio,
            fFin=contingencia.motivo.fFin,
            hInicio=contingencia.motivo.hInicio,
            hFin=contingencia.motivo.hFin,
            tipoContingencia=contingencia.motivo.tipoContingencia,
            motivoContingencia=contingencia.motivo.motivoContingencia
        )
    )
