from odoo_tasks_management.settings import Settings


class DB:
    def __init__(self, settings: Settings):
        # TODO: initialize connection to database
        self.engine = ...
        self.session_source = (
            ...
        )  # sessionmaker(autocommit=False, autoflush=True,
        # bind=self.engine)

    def session(self):
        return self.session_source()
