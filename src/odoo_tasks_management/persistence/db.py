from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from odoo_tasks_management.persistence.models import Base
from odoo_tasks_management.settings import Settings


class DB:
    def __init__(self, settings: Settings):
        # This method is the constructor for the database class.
        # It creates a new SQLAlchemy engine and binds it to the specified database URL in the
        # settings.
        # It then creates all the tables in the database based on the defined model classes.
        # Finally, it creates a new session source that will be used to create new sessions.

        # The 'settings' parameter is an instance of the 'Settings' class that contains
        # configuration options for the database.
        # It is used to get the database URL and other options needed to configure the engine and
        # session source.

        engine = create_engine(settings.DB_DSN, isolation_level="REPEATABLE READ")

        Base.metadata.create_all(bind=engine)

        self.session_source = sessionmaker(
            autocommit=False, autoflush=True, bind=engine
        )

    def session(self) -> Session:
        # This method returns a new SQLAlchemy session from the session source created in the
        # constructor.
        # The session has autocommit and autoflush set to False and True, respectively,
        # which provides the desired behavior
        # for most database interactions.

        with self.session_source() as session:
            return session
