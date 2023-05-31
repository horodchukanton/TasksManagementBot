import re
from datetime import datetime

from sqlalchemy import and_, or_
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.util import quick_markup
import calendar

import odoo_tasks_management
from odoo_tasks_management.business_logic.base.operation import Operation, Prompt, PromptMessage
from odoo_tasks_management.business_logic.base.procedure import Procedure
from odoo_tasks_management.messenger.telegram import Bot
from odoo_tasks_management.odoo.client import OdooClient
from odoo_tasks_management.persistence.db import DB
from odoo_tasks_management.persistence.models import Project, Task, User


class CreateTaskMenu(Procedure):
    def __init__(self, router: 'Router', db: DB, bot: Bot, odoo_client: OdooClient):
        super().__init__(bot)
        self._db = db
        self._router = router
        self._odoo_client = odoo_client
        self._operation = Operation(
            bot=bot,
            prompts=[
                Prompt(
                    message=self.show_projects_list,
                    expects=["text"],
                    handler=self.project_chosen,
                ),
                Prompt(
                    message=PromptMessage(
                        text='Введіть заголовок задачі',
                    ),
                    expects=["text"],
                    handler=self.title_name,
                ),
                Prompt(
                    message=self.show_users_list,
                    expects=["text"],
                    handler=self.chosen_assignee_and_responsible,
                ),
                Prompt(
                    message=self.deadline_year,
                    expects=["text"],
                    handler=self.chosen_year,
                ),
                Prompt(
                    message=self.deadline_month,
                    expects=["text"],
                    handler=self.chosen_month,
                ),
                Prompt(
                    message=self.deadline_day,
                    expects=["text"],
                    handler=self.chosen_day,
                ),
                Prompt(
                    message=PromptMessage(
                        text='Введіть опис задачі',
                    ),
                    expects=["text"],
                    handler=self.description,
                ),
                Prompt(
                    message=PromptMessage(
                        text='Введіть кількість годин, необхідних для виконання задачі (виключно у вигляді цифр)',
                    ),
                    expects=["text"],
                    handler=self.terms,
                ),
            ],
            on_finish=self.task_saving
        )

        self._context = {}
        self.perfect_month_names = []

    def show_projects_list(self, operation, chat_id):
        bot = operation.bot
        projects = self._get_projects()
        bot.send_message(chat_id, text='Оберіть проект для майбутньої задачі️ 🔽')
        buttons = []
        button_row = []
        # формуємо markup для кожного словника, який поверне функція self._get_projects(),
        for project in projects:
            project_name = project
            project_id = projects[project]
            button = InlineKeyboardButton(text=project_name,
                                          callback_data=project_id)
            button_row.append(button)

            if len(button_row) == 2:
                buttons.append(button_row)
                button_row = []

        if len(button_row) > 0:
            buttons.append(button_row)
        markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        return
    def _get_projects(self):
        # знаходимо id проекту, отримуємо масив усіх проектів
        projects_id = self._db.session().query(Project.id).all()

        current_projects_id = []
        for id in projects_id:
            current_projects_id.append(id[0])

        # знаходимо проекти за якими людина керівник
        users_project_names_ids_d = self._db.session().query(
            Project.name, Project.id).filter_by(user_id=45).all()


        #знаходимо задачі в таблиці задач за id поточного користувача, які не скасовані та не виконані
        project_id_for_names_task = self._db.session().query(Task.project_id).filter(
            and_(
                Task.project_id.in_(current_projects_id),
                Task.status != "Виконано",
                Task.status != "Скасовано",
                or_(
                  Task.assignee == 45,
                  Task.responsible == 45,
                )
            )
        ).distinct().all()


        # отримуємо "чистий масив"
        task_projects_ids = []
        for id in project_id_for_names_task:
            task_projects_ids.append(id[0])

        # знаходимо по id проекту його назву в таблиці проектів, добавляємо в масив
        project_names_from_tasks = self._db.session().query(
            Project.name, Project.id
        ).filter(Project.id.in_(task_projects_ids)).all()

        merged_list = list(
            set(project_names_from_tasks + users_project_names_ids_d))

        inline_buttons = {}
        for value in merged_list:
            button_name = f"{value[0]}"
            inline_buttons[button_name] = value[1]
        return inline_buttons

    def project_chosen(self, chat_id, message):
        # завдяки колбеку у відповідній функції, ми отримуємо id з повідомлення
        project_id = message.text

        self._context['project_id'] = int(project_id)
        project_partner_id = self._db.session().query(Project.partner_id).filter_by(
            id=project_id).one()[0]
        if project_partner_id is None:
            project_partner_id = 0
        self._context['partner_id'] = project_partner_id

        # знаходимо в таблиці проектів ім'я проекту по іd
        current_project_name = self._db.session().query(Project.name).filter_by(
            id=project_id).one()[0]
        self._bot.send_message(chat_id,
                               f"Обраний проект: {current_project_name}")
        self._context['project'] = current_project_name

    def title_name(self, chat_id, message):
        title_task = message.text
        self._context['title'] = title_task
        self._bot.send_message(chat_id,
                               f"Заголовок задачі: {title_task}")

    def _get_users_for_assignee(self):
        users_id_name = self._db.session().query(User.name, User.id).all()
        inline_buttons = {}
        for value in users_id_name:
            button_name = f"{value[0]}"
            inline_buttons[button_name] = value[1]
        return inline_buttons

    def show_users_list(self, operation, chat_id):
        bot = operation.bot
        users = self._get_users_for_assignee()
        bot.send_message(chat_id, text='Оберіть виконавця для майбутньої задачі 🔽')

        buttons = []
        button_row = []
        # формуємо markup для кожного словника, який поверне функція self._get_users(),
        for user in users:
            user_name = user
            user_id = users[user]
            button = InlineKeyboardButton(text=user_name,
                                          callback_data=user_id)
            button_row.append(button)

            if len(button_row) == 2:
                buttons.append(button_row)
                button_row = []
        if len(button_row) > 0:
            buttons.append(button_row)

        markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        return

    def chosen_assignee_and_responsible(self, chat_id, message):
        id_assignee = message.text
        self._context['assignee_id'] = int(id_assignee)
        assignee = self._db.session().query(User.name).filter_by(
            id=id_assignee).one()[0]
        self._context['assignee'] = assignee
        responsible = self._db.session().query(User.name).filter_by(
            telegram_chat_id=chat_id).one()[0]
        self._context['responsible'] = responsible
        responsible_id = self._db.session().query(User.id).filter_by(
            telegram_chat_id=chat_id).one()[0]
        self._context['responsible_id'] = responsible_id
        self._bot.send_message(chat_id, f'Виконавець:{assignee}, '
                              f'Відповідальний: {responsible}')

    def deadline_year(self, operation, chat_id):
        bot = operation.bot
        bot.send_message(
            chat_id, text='Для формування дати дедлайну, оберіть рік'
        )
        current_year = datetime.now().year
        self._context['current_year'] = current_year
        next_year = current_year + 1
        self._context['next_year'] = next_year

        years = {f'{current_year}': current_year, f'{next_year}': next_year}

        for year in years:
            year_name = year
            year_id = years[year]
            markup = quick_markup(
                {year_name: {'callback_data': year_id}},
            )
            bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        return

    def chosen_year(self, chat_id, message):
        year = message.text
        self._context['year'] = year
        self._bot.send_message(chat_id,
                               f"Обраний рік: {year}")

    def deadline_month(self, operation, chat_id):
        bot = operation.bot
        bot.send_message(
            chat_id, text='Для формування дати дедлайну, оберіть місяць'
        )
        year = int(self._context['year'])
        current_year = self._context['current_year']
        next_year = self._context['next_year']
        current_month = datetime.now().month

        rest_of_month = {}
        self.perfect_month_names = [
            'Січень',
            'Лютий',
            'Березень',
            'Квітень',
            'Травень',
            'Червень',
            'Липень',
            'Серпень',
            'Вересень',
            'Жовтень',
            'Листопад',
            'Грудень',
        ]
        if year == current_year:
            for i in range(current_month, 13):
                month_name = datetime(current_year, i, 1).strftime(
                        '%B')
                perfect_name = self.perfect_month_names[i-1]
                rest_of_month[i] = perfect_name
        elif year == next_year:
            for i in range(1, 13):
                month_name = datetime(next_year, i, 1).strftime(
                    '%B')
                perfect_name = self.perfect_month_names[i-1]
                rest_of_month[i] = perfect_name

        buttons = []
        button_row = []

        for month in rest_of_month:
            month_id = month
            month_name = rest_of_month[month]
            button = InlineKeyboardButton(text=month_name,
                                          callback_data=month_id)
            button_row.append(button)
            if len(button_row) == 2:
                buttons.append(button_row)
                button_row = []
        if len(button_row) > 0:
            buttons.append(button_row)
        markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id, text='⇲️', reply_markup=markup)
        return

    def chosen_month(self, chat_id, message):
        month_id = message.text

        month_name = self.perfect_month_names[int(month_id)-1]
        self._context['month'] = month_id
        self._bot.send_message(chat_id,
                               f"Обраний місяць: {month_name}")

    def deadline_day(self, operation, chat_id):
        bot = operation.bot
        bot.send_message(
            chat_id, text='Для формування дати дедлайну, оберіть день'
        )
        year = int(self._context['year'])
        month = int(self._context['month'])

        num_days = calendar.monthrange(year, month)[1]

        month_days = []
        finish_days = {}
        for day in range(1, num_days + 1):
            month_days.append(day)

        for day in month_days:
            day_name = day
            finish_days[day_name] = day

        buttons = []
        button_row = []
        for day in finish_days:
            day_id = day
            days_name = str(finish_days[day])
            button = InlineKeyboardButton(text=days_name,
                                          callback_data=day_id)
            button_row.append(button)
            if len(button_row) == 5:
                buttons.append(button_row)
                button_row = []
        if len(button_row) > 0:
            buttons.append(button_row)
        markup = InlineKeyboardMarkup(buttons)
        bot.send_message(chat_id, text='⇲️', reply_markup=markup)

        return

    def chosen_day(self, chat_id, message):
        day_id = message.text
        month_id = self._context['month']
        year = int(self._context['year'])
        self._context['deadline'] = str(year) + '-' + str(month_id) + '-' + str(day_id)
        date_deadline = str(day_id) + '.' + str(month_id) + '.' + str(year)
        self._bot.send_message(chat_id,
                               f"Обрана дата : {date_deadline}"
                               )

    def description(self, chat_id, message):
        title_description = message.text
        self._context['description'] = title_description
        self._bot.send_message(chat_id,
                               f"Опис задачі: {title_description}")

    def terms(self, chat_id, message):
        hours_number = message.text
        if hours_number.isdigit():
            self._context['hours'] = hours_number
            self._bot.send_message(chat_id,
                                   f"Кількість годин для задачі: {hours_number}")
        else:
            self._bot.send_message(chat_id,
                                   f"Вкажіть, будь ласка, тільки цифри")
            return

    def task_saving(self, chat_id):
        bot = self._operation.bot

        self._odoo_client.create_task(
            self._context['project_id'],
            self._context['title'],
            self._context['description'],
            self._context['deadline'],
            self._context['responsible_id'],
            self._context['assignee_id'],
            self._context['hours'],
            self._context['partner_id']
        )

        project_name = self._context['project']
        task_name = self._context['title']
        description = self._context['description']
        deadline = self._context['deadline']
        responsible = self._context['responsible']
        assignee = self._context['assignee']
        planned_hours = self._context['hours']

        bot.send_message(
            chat_id,
            f"Задача збережена. Ось її деталі: "
            f"{project_name}, "
            f"{task_name}, "
            f"{description},"
            f"{deadline},"
            f"{responsible},"
            f"{assignee},"
            f"{planned_hours}"
        )

    def something(self, chat_id, message):
        hours_number = message.text
        if hours_number.isdigit():
            self._context['hours'] = hours_number
            self._bot.send_message(chat_id,
                                   f"Кількість годин для задачі: {hours_number}")
        else:
            self._bot.send_message(chat_id,
                                   f"Вкажіть, будь ласка, тільки цифри")
            return
