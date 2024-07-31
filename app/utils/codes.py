import time
import uuid


def generate_uuid():
    """Generate UUID version 4 with all letters uppercase."""
    return str(uuid.uuid4()).upper()


def generate_numero_control(tipo_documento: str, correlativo: int):
    """Generate numero de control for DTE."""
    timestamp = str(int(time.time()))[-8:]

    str_correlativo = str(correlativo).zfill(15)
    return f"DTE-{tipo_documento}-{timestamp}-{str_correlativo}"
