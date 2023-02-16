from pydantic import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN = ''
    ODOO_URL = ''
    ODOO_API_KEY = ''

    class Config:
        case_sensitive = True
        env_file = 'config.env'
        env_file_encoding = 'utf-8'
