from pydantic import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str

    ODOO_URL: str
    ODOO_DATABASE: str
    ODOO_API_KEY: str
    ODOO_API_LOGIN: str

    DB_DSN: str

    SCHEDULE_DEADLINE_NOTIFICATIONS: int = 60  # minutes == 1 hour
    SCHEDULE_DB_SYNC: int = 180  # minutes == 3 hours

    class Config:
        case_sensitive = True
        env_file = "config.env"
        env_file_encoding = "utf-8"
