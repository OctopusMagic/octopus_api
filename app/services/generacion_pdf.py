from loguru import logger
import requests

from app.config.cfg import GENERATOR_URL


def generar_pdf(
        documento_sin_firma: str,
        selloRecibido: str,
        tipo_dte: str
        ) -> dict:
    """Genera un PDF a partir de un documento sin firmar."""
    try:
        response = requests.post(
            f"{GENERATOR_URL}?documento={tipo_dte}",
            json={"documento": documento_sin_firma, "selloRecibido": selloRecibido}
        )
        return response.json()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
        logger.error(f"Error al Generar el PDF: {e}")
        return {
            "pdfUrl": "",
            "jsonUrl": "",
            "rtfUrl": "",
        }
