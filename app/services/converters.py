from app.models.dte import ItemFE, ItemCCF, ItemFEX
from app.models.dte.Item import ItemCRE, ItemFSE
from app.schemas import ItemAPIFE, ItemAPIFEX, ItemAPICCF
from app.schemas.item_api import ItemAPICRE, ItemAPIFSE


def convert_itemapi_to_itemfe(
        item: ItemAPIFE,
        numero: int,
        tributos: list = None) -> ItemFE:
    """ Convierte un ItemAPI a ItemFE."""
    return ItemFE(
        numItem=numero,
        tipoItem=item.tipoItem,
        cantidad=item.cantidad,
        codigo=item.codigo,
        uniMedida=item.uniMedida,
        descripcion=item.descripcion,
        precioUni=item.precioUni,
        montoDescu=item.montoDescu,
        ventaNoSuj=item.ventaNoSuj,
        ventaExenta=item.ventaExenta,
        ventaGravada=item.ventaGravada,
        noGravado=item.noGravado,
        ivaItem=item.ivaItem,
        tributos=tributos,
        psv=0.0,
    )


def convert_itemapi_to_itemccf(
        item: ItemAPICCF,
        numero: int,
        tributos: list = None) -> ItemCCF:
    """ Convierte un ItemAPI a ItemCCF."""
    tributos = tributos or []
    tributos.append("20")

    return ItemCCF(
        numItem=numero,
        tipoItem=item.tipoItem,
        cantidad=item.cantidad,
        codigo=item.codigo,
        uniMedida=item.uniMedida,
        descripcion=item.descripcion,
        precioUni=item.precioUni,
        montoDescu=item.montoDescu,
        ventaNoSuj=item.ventaNoSuj,
        ventaExenta=item.ventaExenta,
        ventaGravada=item.ventaGravada,
        noGravado=item.noGravado,
        tributos=tributos,
        psv=0.0,
    )


def convert_itemapi_to_itemfex(
        item: ItemAPIFEX,
        numero: int,
        tributos: list = None) -> ItemFEX:
    """ Convierte un ItemAPI a ItemFEX."""
    tributos = tributos or []
    tributos.append("C3")

    return ItemFEX(
        numItem=numero,
        cantidad=item.cantidad,
        codigo=item.codigo,
        uniMedida=item.uniMedida,
        descripcion=item.descripcion,
        precioUni=item.precioUni,
        montoDescu=item.montoDescu,
        ventaGravada=item.ventaGravada,
        tributos=tributos,
        noGravado=item.noGravado,
    )


def convert_itemapi_to_itemfse(
        item: ItemAPIFSE,
        numero: int) -> ItemFSE:
    """ Convierte un ItemAPI a ItemFSE."""
    return ItemFSE(
        numItem=numero,
        tipoItem=item.tipoItem,
        cantidad=item.cantidad,
        codigo=item.codigo,
        uniMedida=item.uniMedida,
        descripcion=item.descripcion,
        precioUni=item.precioUni,
        montoDescu=item.montoDescu,
        compra=item.compra,
    )


def convert_itemapi_to_itemcre(
    item: ItemAPICRE,
    numero:int) -> ItemCRE:
    """ Convierte un ItemAPI a ItemCRE."""
    return ItemCRE(
        numItem=numero,
        tipoDte=item.tipoDte,
        tipoDoc=item.tipoDoc,
        numDocumento=item.numDocumento,
        fechaEmision=item.fechaEmision,
        montoSujetoGrav=item.montoSujetoGrav,
        codigoRetencionMH=item.codigoRetencionMH,
        ivaRetenido=item.ivaRetenido,
        descripcion=item.descripcion
    )
