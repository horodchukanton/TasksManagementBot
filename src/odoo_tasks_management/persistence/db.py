from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from odoo_tasks_management.persistence.models import Base
from odoo_tasks_management.settings import Settings


class DB:
    def __init__(self, settings: Settings):
        engine = create_engine(
            settings.DB_DSN, isolation_level="REPEATABLE READ"
        )

        Base.metadata.create_all(bind=engine)

        self.session_source = sessionmaker(
            autocommit=False, autoflush=True, bind=engine
        )

    def session(self) -> Session:
        with self.session_source() as session:
            return session
