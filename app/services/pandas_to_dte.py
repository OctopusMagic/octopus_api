from datetime import datetime
import json
from fastapi import HTTPException, status
import pandas as pd
from app.config.cfg import HACIENDA_ENV
from app.models import enums
from app.models.dte import (
    Anulacion,
    ComprobanteRetencion,
    CreditoFiscal,
    Direccion,
    DocumentoRelacionado,
    FacturaElectronica,
    FacturaExportacion,
    Identificacion,
    IdentificacionFEX,
    IdentificacionAnulacion,
    ItemApendice,
    NotaCredito,
    Tributo,
)
from app.models.dte.Anulacion import DocumentoAnulacion, MotivoAnulacion
from app.models.dte.Emisor import EmisorAnulacion, EmisorNC
from app.models.dte.Item import ItemCCF, ItemCRE, ItemFE, ItemFEX, ItemFSE, ItemNC
from app.models.dte.Receptor import (
    ReceptorCCF,
    ReceptorCRE,
    ReceptorFE,
    ReceptorFEX,
    ReceptorFSE,
)
from app.models.dte.Resumen import (
    ResumenCCF,
    ResumenCRE,
    ResumenFE,
    ResumenFEX,
    ResumenFSE,
    ResumenNC,
)
from app.models.dte.SujetoExcluido import FacturaSujetoExcluido
from app.models.orm import DTE
from app.schemas.factura_exportacion import EmisorFEXAPI
from app.services.datos_emisor import (
    get_datos_emisor,
    get_datos_emisor_cre,
    get_datos_emisor_fse,
)
from app.utils.codes import generate_numero_control, generate_uuid

from app.utils.currency import total_en_letras
from app.services.recepcion_dte import consultar_dte


async def convert_df_to_fe(df: pd.DataFrame) -> tuple[FacturaElectronica, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]
    tributos_resumen = []

    for index, row in df.iterrows():
        correlativo = row[0].strip()
        tributos = []
        tributo1 = str(row[15]).strip() or None
        tributo2 = str(row[16]).strip() or None

        if tributo1 is not None:
            tributos.append(tributo1)
        if tributo2 is not None:
            tributos.append(tributo2)

        if tributos == []:
            tributos = None

        item_cuerpo = ItemFE(
            numItem=row[4],
            tipoItem=row[5],
            cantidad=row[6],
            codigo=str(row[7]),
            uniMedida=row[8],
            descripcion=row[9].strip(),
            precioUni=row[10],
            montoDescu=row[11],
            ventaNoSuj=row[12],
            ventaExenta=row[13],
            ventaGravada=row[14],
            tributos=tributos,
            psv=row[17],
            noGravado=row[18],
            ivaItem=row[19],
        )
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

        tributos_fila = [
            Tributo(
                codigo=str(row[index]),
                descripcion=row[index + 1],
                valor=row[index + 2],
            )
            for index in [29, 32]  # Assuming structure for codigo, descripcion, valor
            if str(row[index]).strip() != ""
        ]

        # Agregar tributos de la fila al resumen si no existen ya
        for tributo in tributos_fila:
            if tributo not in tributos_resumen:
                tributos_resumen.append(tributo)

    if current_row[46].strip() != "":
        direccion = Direccion(
            departamento=enums.get_departamento_by_name(current_row[47].strip())[
                "codigo"
            ]
            if current_row[47].strip() != ""
            else "06",
            municipio="01",
            complemento=current_row[46].strip(),
        )
    else:
        direccion = None

    raw_documento = str(current_row[45]).strip()
    if raw_documento != "":
        if len(raw_documento) == 9:
            tipoDocumento = "13"
            numeroDocumento = raw_documento[:-1] + "-" + raw_documento[-1]
        else:
            tipoDocumento = "37"
            numeroDocumento = raw_documento
    else:
        tipoDocumento = None
        numeroDocumento = None
        
    telefono = current_row.get(48, None)
    telefono = None if (str(telefono).strip() == "-") else str(telefono).strip()
    correo = None if (str(current_row.get(49, None)).strip() == "") else str(current_row.get(49, None)).strip()

    return FacturaElectronica(
        identificacion=Identificacion(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.FACTURA,
            numeroControl=generate_numero_control("01", correlativo),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=None,
        emisor=await get_datos_emisor(),
        receptor=ReceptorFE(
            tipoDocumento=tipoDocumento,
            numDocumento=numeroDocumento,
            nombre=current_row[44].strip(),
            telefono=telefono if telefono != "" else None,
            correo=correo,
            direccion=direccion,
        ),
        otrosDocumentos=None,
        ventaTercero=None,
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenFE(
            totalNoSuj=current_row[20],
            totalExenta=current_row[21],
            totalGravada=current_row[22],
            subTotalVentas=current_row[23],
            descuNoSuj=current_row[24],
            descuExenta=current_row[25],
            descuGravada=current_row[26],
            porcentajeDescuento=current_row[27],
            totalDescu=current_row[28],
            tributos=tributos_resumen or None,
            subTotal=current_row[35],
            ivaRete1=current_row[36] or 0,
            reteRenta=current_row[37],
            montoTotalOperacion=current_row[38],
            totalNoGravado=0.0,
            totalPagar=current_row[39],
            totalLetras=total_en_letras(current_row[39]),
            totalIva=current_row[41],
            saldoFavor=current_row[42],
            condicionOperacion=current_row[43],
        ),
        extension=None,
        apendice=[
            ItemApendice(
                campo="Vale(s) desde",
                etiqueta="Vale(s) desde",
                valor=str(current_row[50]) if len(current_row) > 50 else "",
            ),
            ItemApendice(
                campo="Hasta",
                etiqueta="Hasta",
                valor=str(current_row[51]) if len(current_row) > 51 else "",
            ),
            ItemApendice(
                campo="Observaciones",
                etiqueta="Observaciones",
                valor=str(current_row[52]).strip() if len(current_row) > 52 else "",
            ),
        ]
        if len(current_row) > 50
        else None,
    ), str(correlativo)


async def convert_df_to_ccf(df: pd.DataFrame) -> tuple[CreditoFiscal, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]
    tributos_resumen = []

    for index, row in df.iterrows():
        correlativo = row[0].strip()
        tributos = []
        tributo1 = str(row[26]).strip() or None
        tributo2 = row[27].strip() or None
        tributo3 = row[28].strip() or None

        if tributo1 is not None:
            tributos.append(tributo1)
        if tributo2 is not None:
            tributos.append(tributo2)
        if tributo3 is not None:
            tributos.append(tributo3)

        if tributos == []:
            tributos = None

        item_cuerpo = ItemCCF(
            numItem=row[15],
            tipoItem=row[16],
            descripcion=row[17].strip(),
            cantidad=row[18],
            codigo=row[19],
            uniMedida=row[20],
            precioUni=row[21],
            montoDescu=row[22],
            ventaNoSuj=row[23],
            ventaExenta=row[24],
            ventaGravada=row[25],
            tributos=tributos,
            psv=row[29],
            noGravado=row[30],
        )
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

    tributos_fila = [
        Tributo(
            codigo=str(current_row[index]),
            descripcion=current_row[index + 1],
            valor=current_row[index + 2],
        )
        for index in [40, 43, 46]  # Assuming structure for codigo, descripcion, valor
        if str(current_row[index]).strip() != ""
    ]

    for tributo in tributos_fila:
        if tributo not in tributos_resumen:
            tributos_resumen.append(tributo)

    if len(str(current_row[4])) >= 9 and len(str(current_row[4])) < 14:
        nit = str(current_row[4]).strip().zfill(14)
    else:
        nit = str(current_row[4]).strip()

    return CreditoFiscal(
        identificacion=Identificacion(
            version=3,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.CREDITO_FISCAL,
            numeroControl=generate_numero_control("03", correlativo),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=None,
        emisor=await get_datos_emisor(),
        receptor=ReceptorCCF(
            nit=nit,
            nrc=str(current_row[5]),
            nombre=current_row[6].strip(),
            codActividad=str(current_row[7]).strip(),
            descActividad=current_row[8].strip(),
            nombreComercial=current_row[9].strip(),
            direccion=Direccion(
                departamento=str(current_row[10]).zfill(2),
                municipio=current_row[11].strip()
                if int(current_row[11]) < 99
                else "14",
                complemento=current_row[12].strip(),
            ),
            telefono=str(current_row[13]),
            correo=current_row[14].strip(),
        ),
        otrosDocumentos=None,
        ventaTercero=None,
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenCCF(
            totalNoSuj=current_row[31],
            totalExenta=current_row[32],
            totalGravada=current_row[33],
            subTotalVentas=current_row[34],
            descuNoSuj=current_row[35],
            descuExenta=current_row[36],
            descuGravada=current_row[37],
            porcentajeDescuento=current_row[38],
            totalDescu=current_row[39],
            tributos=tributos_resumen or None,
            subTotal=current_row[49],
            ivaPerci1=current_row[50],
            ivaRete1=current_row[51],
            reteRenta=current_row[52],
            montoTotalOperacion=current_row[53],
            totalNoGravado=current_row[54],
            saldoFavor=current_row[55],
            totalPagar=current_row[56],
            totalLetras=total_en_letras(current_row[56]),
            condicionOperacion=current_row[58],
        ),
        apendice=[
            ItemApendice(
                campo="Vale(s) desde",
                etiqueta="Vale(s) desde",
                valor=str(current_row[59]) if len(current_row) > 59 else "",
            ),
            ItemApendice(
                campo="Hasta",
                etiqueta="Hasta",
                valor=str(current_row[60]) if len(current_row) > 60 else "",
            ),
            ItemApendice(
                campo="Observaciones",
                etiqueta="Observaciones",
                valor=str(current_row[61]).strip()
                if len(current_row) > 61
                else "",
            ),
        ]
        if len(current_row) > 59
        else None,
    ), str(correlativo)


async def convert_df_to_fse(df: pd.DataFrame) -> tuple[FacturaSujetoExcluido, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]

    for index, row in df.iterrows():
        correlativo = row[0].strip()
        item_cuerpo = ItemFSE(
            numItem=row[12],
            tipoItem=row[13],
            cantidad=row[14],
            uniMedida=row[15],
            descripcion=row[16].strip(),
            precioUni=row[17],
            montoDescu=row[18],
            compra=row[19],
        )
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

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
        sujetoExcluido=ReceptorFSE(
            tipoDocumento=str(current_row[4]).strip(),
            numDocumento=str(current_row[5]).strip(),
            nombre=current_row[6].strip(),
            direccion=Direccion(
                departamento=str(current_row[7]).zfill(2),
                municipio="01",
                complemento=current_row[9].strip(),
            ),
            telefono=str(current_row[10]),
            correo=current_row[11].strip(),
        ),
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenFSE(
            totalCompra=current_row[20],
            descu=current_row[21],
            totalDescu=current_row[22],
            subTotal=current_row[23],
            ivaRete1=current_row[24],
            reteRenta=current_row[25],
            totalPagar=current_row[26],
            totalLetras=total_en_letras(current_row[26]),
            condicionOperacion=current_row[28],
        ),
    ), str(correlativo)


async def convert_df_to_cre(df: pd.DataFrame) -> tuple[ComprobanteRetencion, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]
    totalIVAretenido = 0
    totalSujetoRetencion = 0

    for index, row in df.iterrows():
        tipoDte = str(row[14]).zfill(2)
        numDocumento = str(row[16])

        dte_existente = await consultar_dte(numDocumento, tipoDte)
        if dte_existente.get("codigoMsg") == "999":
            tipoDoc = 1
            numDocumento = numDocumento[:20]
        else:
            tipoDoc = 2

        fechaEmision = datetime.strptime(row[17], "%Y/%m/%d")

        correlativo = row[0].strip()
        item_cuerpo = ItemCRE(
            numItem=index + 1,
            tipoDte=tipoDte,
            tipoDoc=tipoDoc,
            numDocumento=numDocumento,
            fechaEmision=fechaEmision.strftime("%Y-%m-%d"),
            montoSujetoGrav=float(row[18]),
            ivaRetenido=float(row[19]),
            descripcion=row[20].strip(),
            codigoRetencionMH=str(row[21]),
        )
        totalIVAretenido += float(row[19])
        totalSujetoRetencion += float(row[18])
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

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
        receptor=ReceptorCRE(
            tipoDocumento=str(current_row[4]),
            numDocumento=str(current_row[5]),
            nrc=str(current_row[6]),
            nombre=current_row[7].strip(),
            nombreComercial=current_row[8].strip(),
            codActividad=str(current_row[9]).strip(),
            descActividad=str(current_row[9]).strip(),
            direccion=Direccion(
                departamento=str(current_row[11]).zfill(2),
                municipio="01",
                complemento=current_row[13].strip(),
            ),
            telefono=None,
            correo=current_row[10].strip(),
        ),
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenCRE(
            totalSujetoRetencion=totalSujetoRetencion,
            totalIVAretenido=totalIVAretenido,
            totalIVAretenidoLetras=total_en_letras(totalIVAretenido),
        ),
    ), str(correlativo)


async def convert_df_to_anulacion(df: pd.DataFrame) -> Anulacion:
    current_row = df.iloc[0]
    emisor = await get_datos_emisor()
    dteAnular = await DTE.filter(codGeneracion=str(current_row[1])).first()
    if not dteAnular:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="DTE no encontrado"
        )
    documento = json.loads(dteAnular.documento)

    if documento["identificacion"]["tipoDte"] == "01":
        tipoDocumento = documento["receptor"]["tipoDocumento"] or None
        numDocumento = documento["receptor"]["numDocumento"] or None
        nombre = documento["receptor"]["nombre"] or None
        telefono = documento["receptor"]["telefono"] or None
        correo = documento["receptor"]["correo"] or None
    elif documento["identificacion"]["tipoDte"] == "14":
        tipoDocumento = documento["sujetoExcluido"]["tipoDocumento"] or None
        numDocumento = documento["sujetoExcluido"]["numDocumento"] or None
        nombre = documento["sujetoExcluido"]["nombre"] or None
        telefono = documento["sujetoExcluido"]["telefono"] or None
        correo = documento["sujetoExcluido"]["correo"] or None
    elif documento["identificacion"]["tipoDte"] == "03" or documento["identificacion"]["tipoDte"] == "05":
        tipoDocumento = "36"
        numDocumento = documento["receptor"]["nit"]
        nombre = documento["receptor"]["nombre"] or None
        telefono = documento["receptor"]["telefono"] or None
        correo = documento["receptor"]["correo"] or None
    else:
        tipoDocumento = documento["receptor"]["tipoDocumento"] or None
        numDocumento = documento["receptor"]["numDocumento"] or None
        nombre = documento["receptor"]["nombre"] or None
        telefono = documento["receptor"]["telefono"] or None
        correo = documento["receptor"]["correo"] or None

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
            correo=emisor.correo,
        ),
        documento=DocumentoAnulacion(
            tipoDte=dteAnular.tipo_dte,
            codigoGeneracion=dteAnular.codGeneracion,
            selloRecibido=dteAnular.selloRecibido,
            numeroControl=documento["identificacion"]["numeroControl"],
            fecEmi=documento["identificacion"]["fecEmi"],
            montoIva=None,
            codigoGeneracionR=str(current_row[5]).strip()
            if current_row[5].strip() != ""
            else None,
            tipoDocumento=tipoDocumento,
            numDocumento=numDocumento,
            nombre=nombre,
            telefono=telefono,
            correo=correo,
        ),
        motivo=MotivoAnulacion(
            tipoAnulacion=current_row[4],
            motivoAnulacion=current_row[6],
            nombreResponsable=emisor.nombre,
            tipDocResponsable="36",
            numDocResponsable=emisor.nit,
            nombreSolicita=emisor.nombre,
            tipDocSolicita="36",
            numDocSolicita=emisor.nit,
        ),
    )


async def convert_df_to_nc(df: pd.DataFrame) -> tuple[NotaCredito, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]
    tributos_resumen = []

    for index, row in df.iterrows():
        correlativo = row[0].strip()
        tributos = []
        tributo1 = str(row[26]).strip() or None
        tributo2 = str(row[27]).strip() or None
        tributo3 = str(row[28]).strip() or None

        if tributo1 is not None:
            tributos.append(tributo1)
        if tributo2 is not None:
            tributos.append(tributo2)
        if tributo3 is not None:
            tributos.append(tributo3)
        if tributos == []:
            tributos = None

        item_cuerpo = ItemNC(
            numItem=row[15],
            tipoItem=row[16],
            numeroDocumento=str(row[54]),
            descripcion=row[17].strip(),
            cantidad=row[18] if row[18] > 0 else 1,
            codigo=row[19],
            uniMedida=int(row[20]) if str(row[20]).strip() != "" else 99,
            precioUni=row[21],
            montoDescu=row[22],
            ventaNoSuj=row[23],
            ventaExenta=row[24],
            ventaGravada=row[25],
            tributos=tributos,
        )
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

    tributos_fila = [
        Tributo(
            codigo=str(current_row[index]),
            descripcion=current_row[index + 1],
            valor=current_row[index + 2],
        )
        for index in [37, 40, 43]  # Assuming structure for codigo, descripcion, valor
        if str(current_row[index]).strip() != ""
    ]

    for tributo in tributos_fila:
        if tributo not in tributos_resumen:
            tributos_resumen.append(tributo)

    emisor = await get_datos_emisor()

    totalNoSuj = sum([item.ventaNoSuj for item in cuerpoDocumento])
    totalExenta = sum([item.ventaExenta for item in cuerpoDocumento])
    totalGravada = sum([item.ventaGravada for item in cuerpoDocumento])
    subTotalVentas = totalNoSuj + totalExenta + totalGravada

    return NotaCredito(
        identificacion=Identificacion(
            version=3,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.NOTA_CREDITO,
            numeroControl=generate_numero_control(enums.Dte.NOTA_CREDITO, correlativo),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContin=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        documentoRelacionado=[
            DocumentoRelacionado(
                tipoDocumento=str(current_row[52]),
                tipoGeneracion=current_row[53],
                numeroDocumento=str(current_row[54]),
                fechaEmision=current_row[55].replace("/", "-"),
            )
        ],
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
            correo=emisor.correo,
        ),
        receptor=ReceptorCCF(
            nit=str(current_row[4]).strip(),
            nrc=str(current_row[5]),
            nombre=current_row[6].strip(),
            codActividad=str(current_row[7]).strip(),
            descActividad=current_row[8].strip(),
            nombreComercial=current_row[9].strip(),
            direccion=Direccion(
                departamento=str(current_row[10]).zfill(2),
                municipio="01",
                complemento=current_row[12].strip(),
            ),
            telefono=str(current_row[13]),
            correo=current_row[14].strip(),
        ),
        ventaTercero=None,
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenNC(
            totalNoSuj=totalNoSuj,
            totalExenta=totalExenta,
            totalGravada=totalGravada,
            subTotalVentas=subTotalVentas,
            descuNoSuj=current_row[35],
            descuExenta=current_row[36],
            descuGravada=current_row[46],
            totalDescu=current_row[48],
            tributos=tributos_resumen or None,
            subTotal=subTotalVentas,
            ivaPerci1=0,
            ivaRete1=current_row[56] if str(current_row[56]).strip() != "" else 0,
            reteRenta=0,
            montoTotalOperacion=current_row[49],
            totalLetras=total_en_letras(current_row[49]),
            condicionOperacion=current_row[51],
        ),
    ), str(correlativo)


async def convert_df_to_fex(df: pd.DataFrame) -> tuple[FacturaExportacion, str]:
    cuerpoDocumento = []
    correlativo = 1
    current_row = df.iloc[0]

    for index, row in df.iterrows():
        correlativo = row[0].strip()
        item_cuerpo = ItemFEX(
            numItem=index + 1,
            cantidad=row[14],
            codigo=row[15],
            uniMedida=row[16],
            descripcion=row[17].strip(),
            precioUni=row[18],
            montoDescu=row[19],
            ventaGravada=row[20],
            tributos=None,
            noGravado=0.0,
        )
        cuerpoDocumento.append(item_cuerpo)
        current_row = row

    emisor = await get_datos_emisor(
        EmisorFEXAPI(
            regimen=current_row[1],
            recintoFiscal=str(current_row[2]),
            tipoItemExpor=current_row[3],
        )
    )

    apendice = []
    if len(current_row) > 28:
        apendice.append(ItemApendice(campo="No. Pedido", etiqueta="No. Pedido", valor=str(current_row[28])))
    if len(current_row) > 29:
        apendice.append(ItemApendice(campo="Transporte", etiqueta="Transporte", valor=str(current_row[29])))
    if len(current_row) > 30:
        apendice.append(ItemApendice(campo="Documento", etiqueta="Documento", valor=str(current_row[30])))
    if len(current_row) > 31:
        apendice.append(ItemApendice(campo="Bultos", etiqueta="Bultos", valor=str(current_row[31])))

    if apendice == []:
        apendice = None

    totalGravada = sum([item.ventaGravada for item in cuerpoDocumento])
    totalNoGravada = sum([item.noGravado for item in cuerpoDocumento])
    totalDescu = sum([item.montoDescu for item in cuerpoDocumento])
    flete = current_row[25]
    seguro = current_row[26]
    total_operacion = totalGravada - totalDescu + totalNoGravada + flete + seguro

    return FacturaExportacion(
        identificacion=IdentificacionFEX(
            version=1,
            ambiente=HACIENDA_ENV,
            tipoDte=enums.Dte.EXPORTACION,
            numeroControl=generate_numero_control(enums.Dte.EXPORTACION, correlativo),
            codigoGeneracion=generate_uuid(),
            tipoModelo=enums.ModeloFacturacion.PREVIO,
            tipoOperacion=enums.TipoTransmision.NORMAL,
            tipoContingencia=None,
            motivoContigencia=None,
            fecEmi=datetime.now().strftime("%Y-%m-%d"),
            horEmi=datetime.now().strftime("%H:%M:%S"),
            tipoMoneda="USD",
        ),
        emisor=emisor,
        receptor=ReceptorFEX(
            tipoDocumento=str(current_row[4]),
            numDocumento=str(current_row[5]),
            nombre=current_row[6].strip(),
            descActividad=current_row[7].strip(),
            codPais=str(current_row[8]).strip(),
            nombrePais=current_row[9].strip(),
            complemento=current_row[10].strip(),
            nombreComercial=current_row[6].strip(),
            tipoPersona=current_row[11] if current_row[11] <= 2 else 1,
            telefono=str(current_row[12]),
            correo=current_row[13].strip(),
        ),
        otrosDocumentos=None,
        ventaTercero=None,
        cuerpoDocumento=cuerpoDocumento,
        resumen=ResumenFEX(
            totalGravada=round(totalGravada, 2),
            descuento=current_row[27],
            porcentajeDescuento=current_row[21],
            totalDescu=round(totalDescu, 2),
            montoTotalOperacion=round(total_operacion, 2),
            totalNoGravado=round(totalNoGravada, 2),
            totalPagar=round(total_operacion, 2),
            totalLetras=total_en_letras(total_operacion),
            condicionOperacion=current_row[22],
            pagos=None,
            numPagoElectronico=None,
            codIncoterms=str(current_row[23]),
            descIncoterms=current_row[24],
            flete=round(flete, 2),
            seguro=round(seguro, 2),
        ),
        apendice=apendice,
    ), str(correlativo)
