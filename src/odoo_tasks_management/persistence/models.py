from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "weba_telegram_bot_projects"

    id = Column(Integer, primary_key=True)
    name = Column(String)


class User(Base):
    __tablename__ = "weba_telegram_bot_users"

    id = Column(Integer, primary_key=True)
    partner_id = Column(Integer)
    login = Column(String)
    email = Column(String)
    name = Column(String)
    telegram_chat_id = Column(Integer)
    access_level = Column(Integer)


class Task(Base):
    __tablename__ = "weba_telegram_bot_tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("weba_telegram_bot_projects.id"))
    parent_task_id = Column(Integer, ForeignKey("weba_telegram_bot_tasks.id"))
    assignee = Column(Integer, ForeignKey("weba_telegram_bot_users.id"))
    responsible = Column(Integer, ForeignKey("weba_telegram_bot_users.id"))
    title = Column(String)
    description = Column(String)
    deadline = Column(DateTime)
    status = Column(String)
    planned_hours = Column(Integer)

    # parent_project = relationship("Project", foreign_keys=[id])
    parent_task = relationship("Task", remote_side=[id])
    assignee_user = relationship("User", foreign_keys=[assignee])
    responsible_user = relationship("User", foreign_keys=[responsible])


#
# class Notification(Base):
#     __tablename__ = 'weba_telegram_bot_notifications'
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('weba_telegram_bot_users.id'))
#     task_id = Column(Integer, ForeignKey('weba_telegram_bot_tasks.id'))
#     message = Column(String)
#
#     user = relationship('User')
#     task = relationship('Task')
