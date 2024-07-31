import requests

from app.config.cfg import NIT, SIGNATURE_URL, SIGNATURE_PASSWORD
from app.models.dte import DocumentoFirmar, DocumentoFirmado


def firmar_documento(documento) -> DocumentoFirmado:
    """Request to the Local Signing API to sign a DTE."""
    data = DocumentoFirmar(
        contentType="application/JSON",
        nit=NIT,
        activo=True,
        passwordPri=SIGNATURE_PASSWORD,
        dteJson=documento.model_dump()
    )
    response = requests.post(SIGNATURE_URL, json=data.model_dump())
    return DocumentoFirmado(**response.json())


def firmar_documento_raw(documento) -> DocumentoFirmado:
    """Request to the Local Signing API to sign a DTE."""
    data = DocumentoFirmar(
        contentType="application/JSON",
        nit=NIT,
        activo=True,
        passwordPri=SIGNATURE_PASSWORD,
        dteJson=documento
    )
    response = requests.post(SIGNATURE_URL, json=data.model_dump())
    return DocumentoFirmado(**response.json())