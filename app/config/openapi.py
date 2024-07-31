from app.config.base import BaseSettings


OPEN_API_NAME: str = "Octopus"
OPEN_API_VERSION: str = "1.0"
OPEN_API_DESCRIPTION: str = "API para la facturación electrónica"
OPEN_API_BASE_PATH: str = "/api/v1"


class OpenAPISettings(BaseSettings):

    name: str
    version: str
    description: str
    base_path: str

    @classmethod
    def generate(cls):
        return OpenAPISettings(
            name=OPEN_API_NAME,
            version=OPEN_API_VERSION,
            description=OPEN_API_DESCRIPTION,
            base_path=OPEN_API_BASE_PATH,
        )
