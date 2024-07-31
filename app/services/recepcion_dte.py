from datetime import datetime
import json

from fastapi.responses import JSONResponse
import requests

from fastapi import HTTPException, status

from app.models.enums import Dte
from app import schemas
from app.config.cfg import (
    ANULACION_URL,
    CONTINGENCIA_URL,
    HACIENDA_ENV,
    RECEPTION_URL,
    NIT,
    CONSULTAS_URL,
    DEFAULT_RECEIVER,
    DISABLE_EMAIL,
)
from app.models.dte import RespuestaHacienda
from app.models.orm import DTE
from app.services.generacion_pdf import generar_pdf
from app.services.mail_sender import send_mail
from app.utils.auth import get_token
from app.utils.signing import firmar_documento_raw
from app.utils.dte_date_parser import parse_dte_date
from app.utils.dbf_writer import update_records


async def recepcion_dte(
    codGeneracion: str,
    ambiente: str,
    idEnvio: int,
    version: int,
    tipoDte: str,
    documento_firmado: str,
    documento_sin_firma: str = None,
    actualizar_dte: bool = False
) -> schemas.DTESchema:
    """Request to the Recepción DTE API to send a DTE."""
    try:
        token = get_token()
        headers = {"Authorization": f"{token}"}
        data = {
            "ambiente": ambiente,
            "idEnvio": idEnvio,
            "version": version,
            "tipoDte": tipoDte,
            "documento": documento_firmado,
        }
        response = requests.post(RECEPTION_URL, json=data, headers=headers)

        if response.status_code == 200:
            respuesta_hacienda = RespuestaHacienda(**response.json())

            if actualizar_dte:
                dte = await DTE.filter(codGeneracion=codGeneracion).first()
                dte.selloRecibido = respuesta_hacienda.selloRecibido
                dte.estado = respuesta_hacienda.estado
                dte.fhProcesamiento = parse_dte_date(respuesta_hacienda.fhProcesamiento)
                dte.observaciones = str(respuesta_hacienda.observaciones)
                dte.documento = documento_sin_firma
            else:
                dte = DTE(
                    codGeneracion=codGeneracion,
                    selloRecibido=respuesta_hacienda.selloRecibido,
                    estado=respuesta_hacienda.estado,
                    documento=documento_sin_firma,
                    fhProcesamiento=parse_dte_date(respuesta_hacienda.fhProcesamiento),
                    observaciones=respuesta_hacienda.observaciones,
                    tipo_dte=tipoDte,
                )
            await dte.save()

            documentos = generar_pdf(
                documento_sin_firma, respuesta_hacienda.selloRecibido, tipoDte
            )

            documentoJson = json.loads(documento_sin_firma)
            if tipoDte == Dte.SUJETO_EXCLUIDO:
                receptor_mail = documentoJson.get("sujetoExcluido", {}).get(
                    "correo", None
                )
                nombre_receptor = documentoJson.get("sujetoExcluido", {}).get(
                    "nombre", "Cliente"
                )
            else:
                receptor_mail = documentoJson.get("receptor", {}).get("correo", None)
                nombre_receptor = documentoJson.get("receptor", {}).get("nombre", "Cliente")

            if not DISABLE_EMAIL:
                send_mail(
                    send_to=[receptor_mail or DEFAULT_RECEIVER],
                    subject="Documento Tributario Electrónico",
                    message=(f"Estimado(a) {nombre_receptor},\n\n"
                             "Adjunto encontrará su documento tributario electrónico:\n\n"
                             f"Código de Generación: {codGeneracion}\n"
                             f"Número de Control: {documentoJson['identificacion']['numeroControl']}\n"
                             f"Sello de Recepción: {dte.selloRecibido}\n"
                             f"Fecha de Procesamiento: {dte.fhProcesamiento}\n"
                             f"Estado: {dte.estado}\n"),
                    files=[
                        documentos["pdfUrl"],
                        documentos["jsonUrl"],
                    ],
                )
            else:
                print(f"Email disabled: {receptor_mail or DEFAULT_RECEIVER}")

            return schemas.DTESchema(
                codGeneracion=dte.codGeneracion,
                selloRecibido=dte.selloRecibido,
                estado=dte.estado,
                documento=dte.documento,
                fhProcesamiento=dte.fhProcesamiento,
                observaciones=dte.observaciones,
                tipo_dte=tipoDte,
                enlace_pdf=documentos["pdfUrl"],
                enlace_json=documentos["jsonUrl"],
                enlace_rtf=documentos["rtfUrl"],
            )

        else:
            respuesta = response.json()
            if actualizar_dte:
                dte = await DTE.filter(codGeneracion=codGeneracion).first()
                dte.selloRecibido = None
                dte.estado = "RECHAZADO"
                dte.fhProcesamiento = datetime.now(),
                dte.observaciones = f"{respuesta.get('descripcionMsg')} {respuesta.get('observaciones')}",
            else:
                dte = DTE(
                    codGeneracion=codGeneracion,
                    selloRecibido=None,
                    estado="RECHAZADO",
                    documento=documento_sin_firma,
                    fhProcesamiento=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    observaciones=f"{respuesta.get('descripcionMsg')} {respuesta.get('observaciones')}",
                    tipo_dte=tipoDte,
                )
            await dte.save()

            print(documento_sin_firma)
            print(respuesta)

            return schemas.DTESchema(
                codGeneracion=dte.codGeneracion,
                selloRecibido=dte.selloRecibido,
                estado=dte.estado,
                documento=dte.documento,
                fhProcesamiento=dte.fhProcesamiento,
                observaciones=dte.observaciones,
                tipo_dte=tipoDte,
                enlace_pdf="",
                enlace_json="",
                enlace_rtf="",
            )
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    except requests.exceptions.ConnectionError as e:
        print(f"ConnectionError: {e}")
        if actualizar_dte:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
        else:
            dte = DTE(
                codGeneracion=codGeneracion,
                selloRecibido=None,
                estado="CONTINGENCIA",
                documento=documento_sin_firma,
                fhProcesamiento=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                observaciones="Error de conexión con el servidor de Hacienda",
                tipo_dte=tipoDte,
            )
            await dte.save()

        documentos = generar_pdf(documento_sin_firma, "CONTINGENCIA", tipoDte)

        return schemas.DTESchema(
            codGeneracion=dte.codGeneracion,
            selloRecibido=dte.selloRecibido,
            estado=dte.estado,
            documento=dte.documento,
            fhProcesamiento=dte.fhProcesamiento,
            observaciones=dte.observaciones,
            tipo_dte=tipoDte,
            enlace_pdf=documentos["pdfUrl"],
            enlace_json=documentos["jsonUrl"],
            enlace_rtf=documentos["rtfUrl"],
        )

    except requests.exceptions.Timeout as e:
        print(f"Timeout: {e}")
        if actualizar_dte:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
        else:
            dte = DTE(
                codGeneracion=codGeneracion,
                selloRecibido=None,
                estado="CONTINGENCIA",
                documento=documento_sin_firma,
                fhProcesamiento=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                observaciones="Tiempo de espera agotado con el servidor de Hacienda",
                tipo_dte=tipoDte,
            )
            await dte.save()

        documentos = generar_pdf(documento_sin_firma, "CONTINGENCIA", tipoDte)

        return schemas.DTESchema(
            codGeneracion=dte.codGeneracion,
            selloRecibido=dte.selloRecibido,
            estado=dte.estado,
            documento=dte.documento,
            fhProcesamiento=dte.fhProcesamiento,
            observaciones=dte.observaciones,
            tipo_dte=tipoDte,
            enlace_pdf=documentos["pdfUrl"],
            enlace_json=documentos["jsonUrl"],
            enlace_rtf=documentos["rtfUrl"],
        )

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def factura_raw(documento_firmado: str):
    """Request to the Recepción DTE API to send a DTE."""
    try:
        token = get_token()
        headers = {"Authorization": f"{token}"}
        data = {
            "ambiente": "00",
            "idEnvio": 1,
            "version": 1,
            "tipoDte": "01",
            "documento": documento_firmado,
        }
        response = requests.post(RECEPTION_URL, json=data, headers=headers)

        return response.json()

    except Exception as e:
        # Handle other exceptions here
        print(f"Exception: {e}")


async def consultar_dte(codigo_generacion: str, tdte: str = "01") -> dict:
    """Request to the Recepción DTE API to consult a DTE."""
    token = get_token()
    headers = {"Authorization": f"{token}"}
    data = {
        "nitEmisor": NIT,
        "tdte": tdte,
        "codigoGeneracion": codigo_generacion,
    }
    response = requests.post(CONSULTAS_URL, json=data, headers=headers)

    return response.json()


async def anular_dte(
    ambiente: str,
    idEnvio: int,
    version: int,
    documento_firmado: str,
    documento_sin_firma: str = None,
) -> dict:
    """Request to the Recepción DTE API to cancel a DTE."""

    dte_json = json.loads(documento_sin_firma)
    # Buscar el código de generación en el documento
    codgeneracion = dte_json["documento"]["codigoGeneracion"]

    # Buscar el DTE en la base de datos
    dte = await DTE.filter(codGeneracion=codgeneracion).first()

    if not dte:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DTE no encontrado en la base de datos",
        )

    if dte.estado == "ANULADO":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El DTE ya ha sido anulado"
        )

    try:
        token = get_token()
        headers = {"Authorization": f"{token}"}
        data = {
            "ambiente": ambiente,
            "idEnvio": idEnvio,
            "version": version,
            "documento": documento_firmado,
        }
        response = requests.post(ANULACION_URL, json=data, headers=headers)

        respuesta_hacienda = response.json()
        if respuesta_hacienda.get("estado") == "PROCESADO":
            dte.estado = "ANULADO"
            await dte.save()
            
            documentoJson = json.loads(dte.documento)
            codGeneracion = dte.codGeneracion

            if dte.tipo_dte == Dte.SUJETO_EXCLUIDO:
                receptor_mail = documentoJson.get("sujetoExcluido", {}).get(
                    "correo", None
                )
            else:
                receptor_mail = documentoJson.get("receptor", {}).get("correo", None)

            if not DISABLE_EMAIL:
                send_mail(
                    send_to=[receptor_mail or DEFAULT_RECEIVER],
                    subject="Anulación Documento Tributario Electrónico",
                    message=f"Se ha anulado un DTE con Código de Generación: {codGeneracion}",
                    files=[],
                )
            else:
                print(f"Email disabled: {receptor_mail or DEFAULT_RECEIVER}")

            return respuesta_hacienda
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=respuesta_hacienda
            )

    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    except requests.exceptions.ConnectionError as e:
        print(f"ConnectionError: {e}")
        return {
            "status": "Error",
            "message": "Error de conexión con el servidor de Hacienda",
        }

    except requests.exceptions.Timeout as e:
        print(f"Timeout: {e}")
        return {
            "status": "Error",
            "message": "Tiempo de espera agotado con el servidor de Hacienda",
        }

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)


async def contingencia_dte(
    nit: str,
    documento_firmado: str,
    documento_sin_firma: str = None
) -> dict:
    """ Request to the Recepción DTE API to receive DTEs as Contingencia"""
    try:
        token = get_token()
        headers = {
            "Authorization": f"{token}"
        }
        data = {
            "nit": nit,
            "documento": documento_firmado
        }
        response = requests.post(CONTINGENCIA_URL, json=data, headers=headers)
        
        dtes_enviados = []
        respuesta_hacienda = response.json()
        if respuesta_hacienda.get('estado') == "RECIBIDO":
            documento = json.loads(documento_sin_firma)
            motivo = documento["motivo"]
            dtes = documento['detalleDTE']
            for dte in dtes:
                dte_db = await DTE.filter(codGeneracion=dte["codigoGeneracion"]).first()
                documento_db = json.loads(dte_db.documento)
                documento_db["identificacion"]["tipoContingencia"] = motivo["tipoContingencia"]
                documento_db["identificacion"]["tipoOperacion"] = 2
                documento_db["identificacion"]["tipoModelo"] = 2
                documento_db_firmado = firmar_documento_raw(documento_db)
                if not documento_db_firmado.status == "OK":
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=documento_db_firmado.body
                    )
                respuesta_hacienda = await recepcion_dte(
                    codGeneracion=dte_db.codGeneracion,
                    ambiente=HACIENDA_ENV,
                    idEnvio=1,
                    version=documento_db["identificacion"]["version"],
                    tipoDte=documento_db["identificacion"]["tipoDte"],
                    documento_firmado=documento_db_firmado.body,
                    documento_sin_firma=json.dumps(documento_db, ensure_ascii=False),
                    actualizar_dte=True
                )
                dtes_enviados.append({
                    "codGeneracion": respuesta_hacienda.codGeneracion,
                    "selloRecibido": respuesta_hacienda.selloRecibido,
                    "estado": respuesta_hacienda.estado
                })
                update_records(dtes_enviados)

            return JSONResponse(
                content=dtes_enviados,
                status_code=status.HTTP_200_OK
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=respuesta_hacienda
            )
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
    except requests.exceptions.ConnectionError as e:
        print(f"ConnectionError: {e}")
        return {
            "status": "error",
            "message": "Error de conexión con el servidor de Hacienda",
        }

    except requests.exceptions.Timeout as e:
        print(f"Timeout: {e}")
        return {
            "status": "error",
            "message": "Tiempo de espera agotado con el servidor de Hacienda",
        }

    except requests.exceptions.RequestException as e:
        print(f"RequestException: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e)
