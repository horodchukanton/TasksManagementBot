import injector

from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import User


class SynchronizeDatabase:
    @injector.inject
    def __init__(self, db: DB, odoo_client: OdooClient):
        self._db = db
        self._odoo_client = odoo_client

    def run(self):
        print("TODO: Should get information from Odoo and save it to local DB")
        self.sync_users()

    def sync_users(self):
        # Get users from Odoo
        users = self._odoo_client.get_users()

        # Get users from Database
        session = self._db.session()
        existing_users = session.query(User).all()

        if not existing_users:
            session.add_all(
                [
                    User(
                        id=u["id"],
                        login=u["login"],
                    )
                    for u in users
                ]
            )
            session.commit()
            return

        # Compare the lists
        # TODO:

        # Apply the changes
        # TODO:
