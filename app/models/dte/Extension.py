from pydantic import BaseModel


class Extension(BaseModel):

    nombEntrega: str | None = None
    docuEntrega: str | None = None
    nombRecibe: str | None = None
    docuRecibe: str | None = None
    observaciones: str | None = None
    placaVehiculo: str | None = None
