import injector
from sqlalchemy.exc import IntegrityError

from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project, Task, User


class SynchronizeDatabase:
    @injector.inject
    def __init__(self, db: DB, odoo_client: OdooClient):
        self._db = db
        self._odoo_client = odoo_client

    def run(self):
        print("TODO: Should get information from Odoo and save it to local DB")
        self.sync_users()
        self.sync_projects()
        self.sync_tasks()

    def sync_users(self):
        # Get users from Odoo
        users = self._odoo_client.get_users()

        # Get users from Database
        session = self._db.session()
        existing_users = None  # session.query(User).all()

        if not existing_users:
            session.add_all(
                [
                    User(id=u["id"], login=u["login"])
                    for u in users
                ]
            )
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                if "UniqueViolation" not in str(e):
                    print(str(e))
            return

        # Compare the lists
        # TODO:

        # Apply the changes
        # TODO:

    def sync_projects(self):
        projects = self._odoo_client.get_all_projects()
        session = self._db.session()
        existing_projects = None  # session.query(Project).all()

        if not existing_projects:
            session.add_all(
                [
                    Project(
                        id=p["id"],
                        name=p["name"],
                        user_id=p["user_id"][0] if p["user_id"] else None
                            )
                    for p in projects
                ]
            )
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                if "UniqueViolation" not in str(e):
                    print(str(e))
            return

        # Compare the lists
        # TODO:

        # Apply the changes
        # TODO:

    def sync_tasks(self):
        tasks = self._odoo_client.get_all_tasks()
        session = self._db.session()
        existing_tasks = None  # session.query(Task).all()

        if not existing_tasks:
            for t in tasks:
                session.add(
                    Task(
                        id=t['id'],
                        project_id=t['project_id'][0] if t['project_id'] else None,
                        parent_task_id=t['parent_id'][0] if t['parent_id'] else None,
                        assignee=t['user_id'][0] if t['user_id'] else None,
                        responsible=t['create_uid'][0] if t['create_uid'] else None,
                        title=t['name'],
                        description=t['description'],
                        deadline=t['date_deadline'] if t['date_deadline'] else None,
                        status=t['stage_id'][1] if t['stage_id'] else None,
                        planned_hours=t['planned_hours'],
                    )
                )
                try:
                    session.flush()
                    session.commit()
                except IntegrityError as e:
                    session.rollback()
                    if "UniqueViolation" not in str(e):
                        print(str(e))

        # Compare the lists
        # TODO:

        # Apply the changes
        # TODO:
