from typing import List

from app.models.dte import (
    ItemFE,
    ItemCCF,
    ResumenFE,
    ResumenCCF,
    Tributo,
)
from app.models.dte.Item import ItemCRE, ItemFEX, ItemFSE, ItemNC
from app.models.dte.Resumen import ResumenCRE, ResumenFEX, ResumenFSE, ResumenNC
from app.schemas.resumen_api import ResumenAPICCF, ResumenAPICRE, ResumenAPIFE, ResumenAPIFEX, ResumenAPIFSE
from app.utils.currency import total_en_letras


def generar_resumen_fe(
        items: List[ItemFE],
        resumen_api: ResumenAPIFE) -> ResumenFE:
    """ Genera el apartado "resumen" de una Factura Electrónica"""

    resumen_dict = {
        'totalNoSuj': 0,
        'totalExenta': 0,
        'totalGravada': 0,
        'subTotalVentas': 0,
        'totalDescu': 0,
        'totalNoGravado': 0,
        'totalIva': 0,
        'descuNoSuj': resumen_api.descuNoSuj,
        'descuExenta': resumen_api.descuExtenta,
        'descuGravada': resumen_api.descuGravada,
        'porcentajeDescuento': resumen_api.porcentajeDescuento,
        'ivaRete1': resumen_api.ivaRete1,
        'reteRenta': resumen_api.reteRenta,
        'saldoFavor': resumen_api.saldoFavor,
        'condicionOperacion': resumen_api.condicionOperacion,
        'tributos': None,
        'pagos': None,
        'numPagoElectronico': None,
    }

    subTotal = 0

    for item in items:
        resumen_dict['totalNoSuj'] += item.ventaNoSuj
        resumen_dict['totalExenta'] += item.ventaExenta
        resumen_dict['totalGravada'] += item.ventaGravada
        resumen_dict['subTotalVentas'] += (item.ventaNoSuj +
                                           item.ventaExenta +
                                           item.ventaGravada)
        resumen_dict['totalDescu'] += item.montoDescu
        resumen_dict['totalNoGravado'] += item.noGravado
        resumen_dict['totalIva'] += round(item.ivaItem, 2)

    subTotal = (resumen_dict['subTotalVentas'] -
                (resumen_dict['descuNoSuj'] +
                 resumen_dict['descuExenta'] +
                 resumen_dict['descuGravada']))

    resumen_dict['subTotal'] = subTotal

    resumen_dict['totalDescu'] += (resumen_dict['descuNoSuj'] +
                                   resumen_dict['descuExenta'] +
                                   resumen_dict['descuGravada'])

    resumen_dict['montoTotalOperacion'] = subTotal
    resumen_dict['totalPagar'] = (resumen_dict['montoTotalOperacion'] +
                                  resumen_dict['ivaRete1'] -
                                  resumen_dict['reteRenta'])

    resumen_dict['totalLetras'] = total_en_letras(resumen_dict['totalPagar'])

    resumen_dict['saldoFavor'] = resumen_api.saldoFavor
    resumen_dict['totalIva'] = round(resumen_dict['totalIva'], 2)

    resumen = ResumenFE(**resumen_dict)
    return resumen


def generar_resumen_ccf(
        items: List[ItemCCF],
        resumen_api: ResumenAPICCF) -> ResumenCCF:
    """
    Genera el apartado resumen de un Comprobante de Crédito Fiscal Electrónico
    """
    resumen_dict = {
        'totalNoSuj': 0,
        'totalExenta': 0,
        'totalGravada': 0,
        'subTotalVentas': 0,
        'totalDescu': 0,
        'totalNoGravado': 0,
        'descuNoSuj': resumen_api.descuNoSuj,
        'descuExenta': resumen_api.descuExtenta,
        'descuGravada': resumen_api.descuGravada,
        'porcentajeDescuento': resumen_api.porcentajeDescuento,
        'ivaRete1': resumen_api.ivaRete1,
        'ivaPerci1': resumen_api.ivaPerci1,
        'reteRenta': resumen_api.reteRenta,
        'saldoFavor': resumen_api.saldoFavor,
        'condicionOperacion': resumen_api.condicionOperacion,
        'pagos': None,
        'numPagoElectronico': None,
    }

    subTotal = 0

    for item in items:
        resumen_dict['totalNoSuj'] += item.ventaNoSuj
        resumen_dict['totalExenta'] += item.ventaExenta
        resumen_dict['totalGravada'] += item.ventaGravada
        resumen_dict['subTotalVentas'] += (item.ventaNoSuj +
                                           item.ventaExenta +
                                           item.ventaGravada)
        resumen_dict['totalDescu'] += item.montoDescu
        resumen_dict['totalNoGravado'] += item.noGravado

    subTotal = (resumen_dict['subTotalVentas'] -
                (resumen_dict['descuNoSuj'] +
                 resumen_dict['descuExenta'] +
                 resumen_dict['descuGravada']))

    resumen_dict['subTotal'] = subTotal

    resumen_dict['totalDescu'] += (resumen_dict['descuNoSuj'] +
                                   resumen_dict['descuExenta'] +
                                   resumen_dict['descuGravada'])

    iva = round((resumen_dict['subTotal'] * 0.13), 2)

    resumen_dict['montoTotalOperacion'] = subTotal + iva

    resumen_dict['totalPagar'] = (resumen_dict['montoTotalOperacion'] +
                                  resumen_dict['ivaRete1'] -
                                  resumen_dict['reteRenta'])

    resumen_dict['totalLetras'] = total_en_letras(resumen_dict['totalPagar'])

    resumen_dict['tributos'] = [Tributo(
        codigo="20",
        descripcion="Impuesto al Valor Agregado 13%",
        valor=iva
    )]

    return ResumenCCF(**resumen_dict)


def generar_resumen_fex(
        items: List[ItemFEX],
        resumen_api: ResumenAPIFEX) -> ResumenFEX:
    """
    Genera el apartado resumen de una Factura de Exportación Electrónica
    """

    resumen_dict = {
        'totalGravada': 0,
        'porcentajeDescuento': resumen_api.porcentajeDescuento,
        'totalDescu': 0,
        'montoTotalOperacion': 0,
        'totalNoGravado': 0,
        'totalPagar': 0,
        'totalLetras': None,
        'condicionOperacion': resumen_api.condicionOperacion,
        'pagos': None,
        'numPagoElectronico': None,
        'codIncoterms': resumen_api.codIncoterms,
        'descIncoterms': resumen_api.descIncoterms,
        'observaciones': None,
        'flete': resumen_api.flete,
        'seguro': resumen_api.seguro,
        'descuento': resumen_api.descuento,
    }

    for item in items:
        resumen_dict['totalGravada'] += item.ventaGravada
        resumen_dict['totalNoGravado'] += item.noGravado
        resumen_dict['totalDescu'] += item.montoDescu

    resumen_dict['totalDescu'] += resumen_dict['descuento']

    resumen_dict['montoTotalOperacion'] = (resumen_dict['totalGravada'] -
                                           resumen_dict['descuento'] -
                                           resumen_dict['totalNoGravado'] +
                                           resumen_dict['flete'] +
                                           resumen_dict['seguro'])
    resumen_dict['totalPagar'] = resumen_dict['montoTotalOperacion']
    resumen_dict['totalLetras'] = total_en_letras(resumen_dict['totalPagar'])

    return ResumenFEX(**resumen_dict)


def generar_resumen_fse(
        items: List[ItemFSE],
        resumen_api: ResumenAPIFSE) -> ResumenFSE:

    resumen_dict = {
        'totalCompra': 0,
        'descu': 0,
        'totalDescu': 0,
        'subTotal': 0,
        'ivaRete1': resumen_api.ivaRete1,
        'reteRenta': 0,
        'totalPagar': 0,
        'totalLetras': None,
        'condicionOperacion': resumen_api.condicionOperacion,
        'pagos': None,
        'observaciones': resumen_api.observaciones,
    }

    for item in items:
        resumen_dict['totalCompra'] += item.compra
        resumen_dict['descu'] += item.montoDescu
        
    resumen_dict['totalDescu'] = resumen_dict['descu']
    resumen_dict['subTotal'] = resumen_dict['totalCompra'] - resumen_dict['descu']
    resumen_dict['reteRenta'] = resumen_dict['subTotal'] * 0.1
    resumen_dict['totalPagar'] = resumen_dict['subTotal'] - resumen_dict['reteRenta']
    resumen_dict['totalLetras'] = total_en_letras(resumen_dict['totalPagar'])

    return ResumenFSE(**resumen_dict)


def generar_resumen_cre(
    items: List[ItemCRE],
    resumen_api: ResumenAPICRE) -> ResumenCRE:
    """ Genera el apartado resumen de un Comprobante de Retención Electrónico"""
    totalSujetoRetencion = 0
    totalIvaRetenido = 0
    
    for item in items:
        totalSujetoRetencion += item.montoSujetoGrav
        totalIvaRetenido += item.ivaRetenido
    
    return ResumenCRE(
        totalSujetoRetencion=totalSujetoRetencion,
        totalIVAretenido=totalIvaRetenido,
        totalIVAretenidoLetras=total_en_letras(totalIvaRetenido),
    )


def generar_resumen_nc(
    items: List[ItemNC],
    resumen_api: ResumenAPICCF) -> ResumenNC:
    """ Genera el apartado resumen de una Nota de Crédito Electrónica"""
    resumen_dict = {
        'totalNoSuj': 0,
        'totalExenta': 0,
        'totalGravada': 0,
        'subTotalVentas': 0,
        'descuNoSuj': resumen_api.descuNoSuj,
        'descuExenta': resumen_api.descuExtenta,
        'descuGravada': resumen_api.descuGravada,
        'totalDescu': 0,
        'tributos': None,
        'subTotal': 0,
        'ivaPerci1': 0,
        'ivaRete1': 0,
        'reteRenta': 0,
        'montoTotalOperacion': 0,
        'totalLetras': None,
        'condicionOperacion': resumen_api.condicionOperacion,
    }

    for item in items:
        resumen_dict['totalNoSuj'] += item.ventaNoSuj
        resumen_dict['totalExenta'] += item.ventaExenta
        resumen_dict['totalGravada'] += item.ventaGravada
        resumen_dict['subTotalVentas'] += (item.ventaNoSuj +
                                           item.ventaExenta +
                                           item.ventaGravada)
        resumen_dict['totalDescu'] += item.montoDescu
    resumen_dict['totalDescu'] += (resumen_dict['descuNoSuj'] +
                                   resumen_dict['descuExenta'] +
                                   resumen_dict['descuGravada'])
    resumen_dict['subTotal'] = (resumen_dict['subTotalVentas'] -
                                resumen_dict['totalDescu'])
    resumen_dict['montoTotalOperacion'] = resumen_dict['subTotal']
    resumen_dict['totalLetras'] = total_en_letras(resumen_dict['montoTotalOperacion'])

    return ResumenNC(**resumen_dict)
