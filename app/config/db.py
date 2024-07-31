from pydantic import Field

from app.config.base import BaseSettings
from app.config.cfg import DATABASE_URL, IS_TEST

DB_MODELS = ["app.models.orm"]
SQLITE_DB_URL = "sqlite://:memory:"
TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["app.models.orm", "aerich.models"],
            "default_connection": "default",
        },
    },
}


class MySQLSettings(BaseSettings):
    """MySQL Connection Settings"""
    user: str = Field(..., env="MYSQL_USER")
    password: str = Field(..., env="MYSQL_PASSWORD")
    db: str = Field(..., env="MYSQL_DATABASE")
    host: str = Field("localhost", env="MYSQL_HOST")
    port: str = Field("3306", env="MYSQL_PORT")


class TortoiseSettings(BaseSettings):
    """Tortoise ORM Settings"""

    db_url: str
    modules: dict
    generate_schemas: bool = False

    @classmethod
    def generate(cls):
        """Generate Tortoise-ORM settings (with sqlite if test)"""
        modules: dict = {"models": DB_MODELS}

        if IS_TEST:
            db_url: str = SQLITE_DB_URL
        else:
            if DATABASE_URL:
                db_url: str = DATABASE_URL
            else:
                mysql_settings = MySQLSettings()
                db_url: str = (
                    f"mysql://{mysql_settings.user}:",
                    f"{mysql_settings.password}@",
                    f"{mysql_settings.host}:",
                    f"{mysql_settings.port}/",
                    f"{mysql_settings.db}",
                )
                TORTOISE_ORM["connections"]["default"] = db_url
                del mysql_settings

        return TortoiseSettings(
            db_url=db_url,
            modules=modules,
            generate_schemas=True
        )
