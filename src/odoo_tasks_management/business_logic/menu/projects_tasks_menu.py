import re
from typing import Union

from sqlalchemy import and_, or_
from telebot import types
from telebot.util import quick_markup

from odoo_tasks_management.business_logic.base.operation import Operation, Prompt, PromptMessage
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project, Task


class ProjectsMenu(Procedure):
    def __init__(self, router: 'Router', db: DB, bot: Bot):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    message=self.show_projects_list,
                    expects=["text"],
                    handler=self.project_chosen,
                ),
                Prompt(
                    message=self.show_tasks_list,
                    expects=["text"],
                    handler=self.task_chosen,
                ),
                Prompt(
                    message=PromptMessage(
                        buttons=["Відмітити задачу, як виконану", "Головне меню"],
                        text='Що ви хочете зробити із задачею?',
                    ),
                    expects=["text"],
                    handler=self.chosen_process_with_tasks,
                ),
            ]
        )

        self._context = {}

    def show_projects_list(self, operation, chat_id):
        bot = operation.bot
        # виклик функції, яка поверне масив словників з назвою проекту та id доступних користувачу
        projects = self._get_projects()
        bot.send_message(chat_id, text='Оберіть проект️ 🔽')
        # формуємо markup для кожного словника, який поверне функція self._get_projects(),
        for project in projects:
            project_name = project
            project_id = projects[project]
            markup = quick_markup(
                {project_name: {'callback_data': project_id}},
            )
            bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        main_menu = types.ReplyKeyboardMarkup()
        row1 = 'Головне Меню'
        main_menu.row(row1)
        bot.send_message(
            chat_id,
            text='Щоб повернутись в Головне меню, натисніть на клавіатуру',
            reply_markup=main_menu
        )
        return

    def _get_projects(self):
        # знаходимо id проекту, отримуємо масив усіх проектів
        projects_id = self._db.session().query(Project.id).all()

        # отримуємо "чистий масив"
        current_projects_id = []
        for id in projects_id:
            current_projects_id.append(id[0])

        # зберігаємо current_projects_id для використання поза функцією
        self._context['current_projects_id'] = current_projects_id

        # знаходимо id проектів в таблиці Tasks за якими тільки актуальні задачі для користувача (рандомно виставлений id)
        project_id_for_names = self._db.session().query(Task.project_id).filter(
            and_(
                Task.project_id.in_(current_projects_id),
                Task.status != "Виконано",
                Task.status != "Скасовано",
                or_(
                    Task.assignee == 58,
                    Task.responsible == 58,
                )
            )
        ).distinct().all()

        #отримуємо "чистий масив"
        task_projects_ids = []
        for id in project_id_for_names:
            task_projects_ids.append(id[0])

        # знаходимо по id проекту його назву в таблиці проектів, добавляємо в масив
        project_names = self._db.session().query(
            Project.name, Project.id
        ).filter(Project.id.in_(task_projects_ids)).all()

        # формуємо словник з масивом словників, де ключ - назва проекту, значення - його id
        inline_buttons = {}
        for value in project_names:
            button_name = f"{value[0]}"
            inline_buttons[button_name] = value[1]
        return inline_buttons

    def project_chosen(self, chat_id, message):
        if message.text == "Головне Меню":
            self._router.goto_root_menu(chat_id, self._bot)
            self._operation.is_finished = True
            return
        # завдяки колбеку у відповідній функції, ми отримуємо id з повідомлення
        project_id = message.text

        self._context['project_id'] = project_id

        # знаходимо в таблиці проектів ім'я проекту по іd
        current_project_name = self._db.session().query(Project.name).filter(
            Project.id == project_id).one()[0]
        self._bot.send_message(chat_id,
                               f"Обраний проект: {current_project_name}")
        self._context['project'] = current_project_name

    def show_tasks_list(self, operation, chat_id):
        bot = operation.bot
        current_tasks = self._get_tasks(chat_id)
        bot.send_message(chat_id, text='Оберіть задачу️ 🔽')
        for task in current_tasks:
            task_id = current_tasks[task]
            task_name = task
            markup = quick_markup(
                {task_name: {'callback_data': task_id}},
            )
            bot.send_message(chat_id, text='⇲️', reply_markup=markup)

        main_menu = types.ReplyKeyboardMarkup()
        row2 = 'Головне Меню'
        main_menu.row(row2)
        bot.send_message(
            chat_id,
            text='Щоб повернутись в Головне меню, натисніть на клавіатуру',
            reply_markup=main_menu
        )
        return


    def _get_tasks(self, chat_id):
        project_id = self._context['project_id']

        # в таблиці задач знаходимо за id проекту заголовки,id усіх задач, виключення: задачі зі статусом Виконано та Скасовано.
        project_tasks = self._db.session().query(Task.title, Task.id).filter(
            (Task.project_id == project_id) & (
                Task.status != "Виконано") & (
                Task.status != "Скасовано")).all()

        # якщо пошук не дав нічого, зберігаємо в змінну для виведення повідомлення при опрацюванні
        if not project_tasks:
            self._bot.send_message(
                chat_id, f"За обраним проектом задач не найдено"
            )
            self._router.goto_root_menu(chat_id, self._bot)
            self._operation.is_finished = True
        # в іншому випадку
        else:
            # формуємо"красивий" масив задач та зберігаємо для використання поза функцією
            current_project_tasks = []
            for task in project_tasks:
                current_project_tasks.append(task[0])
            self._context['tasks'] = current_project_tasks

            # формуємо словник
            inline_tasks_buttons = {}
            for value in project_tasks:
                button_name = f"{value[0]}"
                inline_tasks_buttons[button_name] = value[1]
            self._context['buttons_tasks'] = inline_tasks_buttons

        return inline_tasks_buttons

    def task_chosen(self, chat_id, message):
        if message.text == "Головне Меню":
            self._router.goto_root_menu(chat_id, self._bot)
            self._operation.is_finished = True
            return

        task_id = message.text
        task_title = self._db.session().query(Task.title).filter(
                Task.id == task_id).one()[0]

        if task_title not in self._context['tasks']:
            self._bot.send_message(
                chat_id, "Введено неочікуваний текст"
            )
            self._router.goto_root_menu(chat_id, self._bot)

        current_project_id = self._context['project_id']
        task = self._db.session().query(Task).filter(
            and_(
                Task.title == task_title,
                Task.project_id == current_project_id
            )).one()

        task_assignee = task.assignee_user.login
        task_responsible = task.responsible_user.login
        task_deadline = task.deadline
        task_status = task.status
        task_description = self._clean_html_tags(task.description)
        task_planned_hours = task.planned_hours

        self._bot.send_message(
            chat_id,
            f"<b>Заголовок задачі</b>: {task_title}\n"
            f"<b>Виконавець задачі</b>: {task_assignee}\n"
            f"<b>Відповідальний за задачу</b>: {task_responsible}\n"
            f"<b>Кінцевий термін виконання задачі</b>: {task_deadline}\n"
            f"<b>Статус задачі</b>: {task_status}\n"
            f"<b>Опис задачі</b>: {task_description}\n"
            f"<b>Кількість годин для виконання задачі</b>: {task_planned_hours}",
            parse_mode='HTML'
        )
        self._context['task'] = task_title

    def chosen_process_with_tasks(self, chat_id: Union[int, str], message):
        if message.text == "Відмітити задачу, як виконану":
            task_title = self._context['task']
            session = self._db.session()
            task = session.query(Task).filter(
                and_(
                    Task.title == task_title,
                    Task.project_id == self._context['project_id']
                )).one()
            task.status = 'Виконано'
            session.flush()
            session.commit()
            self._bot.send_message(chat_id,
                                   f"<b>{task_title}</b> статус <b>Виконано</b>",
                                   parse_mode='HTML')

            self._router.goto_root_menu(chat_id, self._bot)

        elif message.text == "Головне меню":
            self._router.goto_root_menu(chat_id, self._bot)

    # def chosen_process_with_projects(self, chat_id):
    #     self._router.goto_root_menu(chat_id, self._bot)
    #     self._operation.is_finished = True

    # def start_create_tasks_menu(self, chat_id: Union[int, str]):
    #     self._router.goto_tasks_for_project_menu(
    #         chat_id,
    #         self._bot,
    #         self._context['project']
    #     )
    @staticmethod
    def _clean_html_tags(description):
        pattern = re.compile('<.*?>')
        return re.sub(pattern, '', description)
