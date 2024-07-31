from fastapi import HTTPException, status
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
    except requests.exceptions.HTTPError as e:
        print(f"HTTPError: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {response.text}"
        )
    except requests.exceptions.ConnectionError as e:
        print(f"ConnectionError: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de conexión con el servidor de generación de PDF"
        )
    except requests.exceptions.Timeout as e:
        print(f"Timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tiempo de espera agotado con el servidor de generación de PDF"
        )
    except Exception as e:
        print(f"Exception: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar el PDF: {response.text}"
        )