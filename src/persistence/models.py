from sqlalchemy.orm import declarative_base

base = declarative_base()


class Project(base):
    pass


class User(base):
    pass


class Task(base):
    pass


class Activity(base):
    pass
