from pydantic import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN = ""

    ODOO_URL = ""
    ODOO_DATABASE = ""
    ODOO_API_KEY = ""
    ODOO_API_LOGIN = ""

    DB_DSN: str

    class Config:
        case_sensitive = True
        env_file = "config.env"
        env_file_encoding = "utf-8"
