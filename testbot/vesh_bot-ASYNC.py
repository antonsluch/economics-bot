# -*- coding: utf-8 -*-
import sys
import asyncio
import random
from telepot.aio import api
from telepot import glance
import telepot.aio
import telepot.aio.helper
# from telepot.helper import Sender
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import (InlineKeyboardMarkup, InlineKeyboardButton,
                                ReplyKeyboardMarkup, KeyboardButton,
                                ReplyKeyboardRemove)
from telepot.aio.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

from pprint import pprint
import os
import requests

# from mail import Mail
import testbot.data as data
import testbot.logic as logic
from testbot.saver import get_src, save_to_img
from testbot.wolfram_alpha import get_plot_link
from testbot import bot_callback, bot_command, async_logger
from testbot.model import *
from testbot.settings import settings

TOKEN = settings["bots"]["test_azzzaza_bot"]
CREATOR = settings["rules"]["creator"]
ADMIN = settings["rules"]["admin"]


class TelegramBot(telepot.aio.Bot):
    """
    Описывает основные функции и кнопки интерфейса бота
    """
    def __init__(self, *args, **kwargs):
        self._token = TOKEN

        self.callback = []  # Список доступных callback функций
        self.commands = []  # Список всех доступных комманд бота
        self._find_bot_functions()

        # Модифицированные команды:
        self.modified_commands = {
            "Все тесты ✍": "all_tests",
            "Результаты 🏆": "results",
            "Помощь ❕": "help",
            "Продолжить тест 👉": "continue_test",
            "Мои тесты ✍": "my_tests",
            "Построить график функции": "graphics"
        }

        # Главная клавиатура бота
        self.main_keyboard = ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text="Все тесты ✍"),
                KeyboardButton(text="Мои тесты ✍")
            ],
            [
                KeyboardButton(text="Помощь ❕"),
                KeyboardButton(text="Результаты 🏆")
            ],
            [
                KeyboardButton(text="Продолжить тест 👉")
            ],
            [
                KeyboardButton(text="Построить график функции")
            ],
        ])

    def _find_bot_functions(self):
        """
        Выполняет поиск команд и колбэк-функций бота
        """
        # TODO: Сделать поиск по наследникам
        for attr_name in self.__dir__():
            try:
                attr = self.__getattribute__(attr_name)
            except AttributeError:
                continue
            if attr:
                if attr.__doc__ == "<bot_callback>":
                    self.callback.append(attr_name)
                if attr.__doc__ == "<bot_command>":
                    self.commands.append(attr_name)

    async def error_handler(self, _id, error_msg: str=None):
        """
        Отсылает пользователю сообщение об ошибке,
        дополняя его подписью разработчика
        :param _id: id пользователя Телеграм
        :param error_msg: сообщение об ошибке
        """
        standard_message = "Данная команда находится в процессе разработки."
        sign = f'\n\nСвязаться с <a href="tg://user?id={CREATOR[1]}">разработчиком</a>'
        if error_msg:
            await self.sendMessage(_id, error_msg + sign, parse_mode="HTML")
        else:
            await self.sendMessage(_id, standard_message + sign, parse_mode="HTML")

    async def show_package(self, _id: int, pkg_obj: dict, edit_mode: bool=False):
        # FIXME case: edit_mode = False
        inline_keyboard = [
            [InlineKeyboardButton(text="🖊 Название",
                                  callback_data="package.name"),
             InlineKeyboardButton(text="🖊 Описание",
                                  callback_data="package.description")],
            [InlineKeyboardButton(text="🖊 Цена",
                                  callback_data="package.price"),
             InlineKeyboardButton(text="🖊 Кр. описание",
                                  callback_data="package.short_description")]
        ]

        # Добавляем тесты в клавиатуру
        tests = pkg_obj["tests"]
        for test in tests:
            test_name = test["name"]
            inline_keyboard.append([InlineKeyboardButton(
                text=test_name, callback_data=f"test={test_name}")])

        # Кнопка "добавить тест"
        inline_keyboard.append([InlineKeyboardButton(text='+ Добавить тест +', callback_data='test=new test')])
        # Кнопка "выйти"
        inline_keyboard.append([InlineKeyboardButton(text='Выйти', callback_data='close_edit_mode')])
        package_reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        text = (f"Вы редактируете пакет <b>{pkg_obj['name']}</b>. Текущие значения параметров:\n"
                f"Краткое описание: <i>{pkg_obj['short_description']}</i>\n"
                f"Описание: <i>{pkg_obj['description']}</i>\n"
                f"Цена: <b>{pkg_obj['price']}</b>\n")
        try:
            await self.sendMessage(_id, text, reply_markup=package_reply_markup, parse_mode="HTML")
        except telepot.exception.TelegramError as e:
            print(e)

    async def show_test(self, _id: int, test_obj: dict, edit_mode: bool=False):
        # FIXME case: edit_mode = False
        # pprint(test_obj)
        inline_keyboard = [
            [InlineKeyboardButton(text="🖊 Название",
                                  callback_data="test.name"),
             InlineKeyboardButton(text="🖊 Цена",
                                  callback_data="test.price")]]

        # Добавляем вопросы в клавиатуру
        questions = test_obj["questions"]
        for q_id in range(len(questions)):
            inline_keyboard.append([InlineKeyboardButton(
                text=q_id+1, callback_data=f"question={q_id}")])

        # Кнопка "добавить вопрос"
        inline_keyboard.append([InlineKeyboardButton(text='+ Добавить вопрос +', callback_data='question=-1')])
        # Кнопка "выйти"
        inline_keyboard.append([InlineKeyboardButton(text='Выйти', callback_data='close_edit_mode')])

        test_reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        # TODO: Дополнить text
        text = (f"Вы редактируете тест <b>{test_obj['name']}</b>. Текущие значения параметров:\n"
                f"Цена: <b>{test_obj['price']}</b>\n")
        try:
            await self.sendMessage(_id, text, reply_markup=test_reply_markup, parse_mode="HTML")
        except telepot.exception.TelegramError as e:
            print(e)

    async def show_question(self, _id: int, question_obj: dict, edit_mode: bool=False):
        # pprint(question_obj)
        # FIXME: case: edit_mode = False
        inline_keyboard = [
            [InlineKeyboardButton(text="🖊 Баллы",
                                  callback_data="question.points"),
             InlineKeyboardButton(text="🖊 Картинка",
                                  callback_data="question.img")],
            [InlineKeyboardButton(text="🖊 Ответ",
                                  callback_data="question.answer"),
             InlineKeyboardButton(text="🖊 Варианты ответов",
                                  callback_data="question.answer_variants")],
            [InlineKeyboardButton(text="🖊 Текст вопроса",
                                  callback_data="question.text")],
            [InlineKeyboardButton(text='Выйти',
                                  callback_data='close_edit_mode')]
        ]
        question_reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        text = (f"Вы редактируете вопрос. Текущие значения параметров:\n"
                f"Баллы: <b>{question_obj['points']}</b>\n"
                f"Ответ: <b>{question_obj['answer']}</b>\n"
                f"Варианты ответов: <b>{question_obj['answer_variants']} "
                f"(при редактировании вводить через \";\" без ковычек)</b>\n"
                f"Текст вопроса: <b>{question_obj['text']}</b>\n"
                f"<a href=\"{question_obj['img']}\">Картинка</a>")
        try:
            await self.sendMessage(_id, text, reply_markup=question_reply_markup, parse_mode="HTML")
        except telepot.exception.TelegramError as e:
            print(e)

    @bot_callback
    async def edit_package(self, msg: dict, text_awaited: bool=False,
                           pkg: dict=None, setting_key: str=None,
                           test_index: int=None, question_index: int=None):
        # ToDo: Проверка на тип сообщения
        is_query = ("id" in msg) and ("chat_instance" in msg)
        if is_query:
            # print("qqqery...")
            query_id, from_id, query_data = glance(msg, flavor='callback_query')
            if not text_awaited:
                if '=' in query_data:
                    # Тут возвращаем менюшки
                    setting, name = query_data.split('=')
                    print(setting, name)
                    if setting == "package":
                        package = await data.get_bot_package(name)
                        print(package)
                        if package:
                            pkg_obj = dict(Package(package))
                        else:
                            await data.add_bot_package(name)
                            pkg_obj = dict(Package(name=name))
                        await data.set_user_callback(
                            from_id, "edit_package", kwargs=dict(pkg=pkg_obj))
                        await self.show_package(_id=from_id, pkg_obj=pkg_obj, edit_mode=True)
                    elif setting == "test":
                        tests = pkg["tests"]
                        test_obj = dict()
                        for test in tests:
                            if test["name"] == name:
                                test_obj = test
                                break
                        if not test_obj:
                            test_obj = dict(Test(name=name))
                            pkg["tests"].append(test_obj)
                        test_index = pkg["tests"].index(test_obj)
                        await data.set_user_callback(
                            from_id, "edit_package", kwargs=dict(pkg=pkg, test_index=test_index))
                        await self.show_test(_id=from_id, test_obj=test_obj, edit_mode=True)
                    elif setting == "question":
                        question_index = int(name)
                        if question_index == -1:
                            question_obj = dict(Question())
                            pkg["tests"][test_index]["questions"].append(question_obj)
                        else:
                            question_obj = pkg["tests"][test_index]["questions"][question_index]
                        await data.set_user_callback(
                            from_id, "edit_package", kwargs=dict(pkg=pkg, test_index=test_index,
                                                                 question_index=question_index))
                        await self.show_question(_id=from_id, question_obj=question_obj, edit_mode=True)
                    else:
                        await self.error_handler(
                            from_id, "Неверный формат (callback) запроса!")
                elif '.' in query_data:
                    # Тут устанавливаем колбэк в режим ожидания текста
                    setting, name = query_data.split('.')
                    print(setting, name)
                    await data.set_user_callback(from_id, "edit_package",
                                                 kwargs=dict(pkg=pkg, text_awaited=True, setting_key=query_data,
                                                             test_index=test_index, question_index=question_index))
                    if name == "img":
                        await self.sendMessage(from_id, "Загрузите изображение, как документ:")
                    else:
                        await self.sendMessage(from_id, "Введите текст:")
                elif query_data == "close_edit_mode":
                    # Тут выходим из режима редактирования
                    if pkg:
                        print(pkg["name"])
                        r = await data.edit_bot_package(pkg["name"], pkg)
                        if r:
                            print(test_index, question_index)
                            if question_index is not None:
                                await data.set_user_callback(from_id, "edit_package",
                                                             kwargs=dict(pkg=pkg, test_index=test_index))
                                await self.show_test(from_id, pkg["tests"][test_index], edit_mode=True)
                            elif test_index is not None:
                                await data.set_user_callback(from_id, "edit_package", kwargs=dict(pkg=pkg))
                                await self.show_package(from_id, pkg, edit_mode=True)
                            else:
                                await data.set_user_callback(from_id, None)
                                await self.sendMessage(from_id, "Изменения сохранены")
                        else:
                            await self.sendMessage(from_id, "Что-то пошло не так. Введите /start для продолжения.")
                    else:
                        await data.set_user_callback(from_id, None)
                        await self.sendMessage(from_id, "Изменений не было")
                else:
                    await self.error_handler(
                        from_id, "Неверный формат (callback) запроса!")
            else:
                await self.error_handler(
                    from_id, "<b>Введите сообщение, не тыкайте просто так кнопки!</b>")
        else:
            content_type, chat_type, chat_id = glance(msg)
            if text_awaited:
                # Тут принимаем изменения
                setting, name = setting_key.split('.')
                if setting == "package":
                    if content_type == "text":
                        setting_data = msg["text"]
                        error_flag = False
                        if name == "name":
                            error_flag = ('.' in setting_data) or ('=' in setting_data)
                        elif name == "price":
                            price = 0.0
                            try:
                                price = float(setting_data)
                            except ValueError:
                                error_flag = True
                        if error_flag:
                            await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                        else:
                            if name == "name":
                                # Избегаем конфликта при изменении имени пакета
                                await data.edit_bot_package(pkg["name"], {"name": setting_data})
                                pkg[name] = setting_data
                            elif name == "price":
                                pkg["price"] = float(setting_data)
                            else:
                                pkg[name] = setting_data
                            await data.set_user_callback(chat_id, "edit_package", kwargs=dict(pkg=pkg))
                            await self.show_package(_id=chat_id, pkg_obj=pkg, edit_mode=True)
                    else:
                        await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                elif setting == "test":
                    # TODO
                    if content_type == "text":
                        setting_data = msg["text"]
                        error_flag = False
                        if name == "name":
                            error_flag = ('.' in setting_data) or ('=' in setting_data)
                        elif name == "price":
                            price = 0.0
                            try:
                                price = float(setting_data)
                            except ValueError:
                                error_flag = True
                        else:
                            raise ValueError("ЧТО-ТО ПОШЛО НЕ ТАК!")
                        if error_flag:
                            await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                        else:
                            if name == "name":
                                pkg["tests"][test_index]["name"] = setting_data
                            elif name == "price":
                                pkg["tests"][test_index]["price"] = float(setting_data)
                            await data.set_user_callback(chat_id, "edit_package",
                                                         kwargs=dict(pkg=pkg, test_index=test_index))
                            await self.show_test(
                                _id=chat_id, test_obj=pkg["tests"][test_index], edit_mode=True)
                    else:
                        await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                elif setting == "question":
                    # TODO
                    if content_type == "text":
                        setting_data = msg["text"]
                        error_flag = False
                        if name == "points":
                            try:
                                int(setting_data)
                            except ValueError:
                                error_flag = True
                        if error_flag:
                            await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                        else:
                            if name == "points":
                                pkg["tests"][test_index]["questions"][question_index]["points"] = int(setting_data)
                            elif name == "answer_variants":
                                answer_variants = [ans.strip() for ans in setting_data.split(";")]
                                pkg["tests"][test_index]["questions"][question_index]["answer_variants"] = \
                                    answer_variants
                            else:
                                pkg["tests"][test_index]["questions"][question_index][name] = setting_data
                            await data.set_user_callback(
                                chat_id, "edit_package", kwargs=dict(pkg=pkg, test_index=test_index,
                                                                     question_index=question_index))
                            await self.show_question(_id=chat_id,
                                                     question_obj=pkg["tests"][test_index]["questions"][question_index],
                                                     edit_mode=True)
                    elif content_type == "document" and "image" in msg["document"]["mime_type"]:
                        pass
                    else:
                        await self.sendMessage(chat_id, "Неверный формат, повторите ввод:")
                else:
                    await self.error_handler(
                        chat_id, "Неверный формат (callback) запроса!")
            else:
                await self.error_handler(
                    chat_id, "<b>Выберите действие на клавиатуре под сообщением!</b>")

        # pprint(msg)


class MyChatHandler(telepot.aio.helper.ChatHandler, TelegramBot):
    """
    Представляет обработчик сообщений в обычном режиме
    """
    def __init__(self, *args, **kwargs):
        super(MyChatHandler, self).__init__(*args, **kwargs)

        # Находим все функции бота
        self._find_bot_functions()

    @async_logger("log/on_msg.log")
    async def on_chat_message(self, msg):
        # pprint(msg)
        content_type, chat_type, chat_id = glance(msg)
        print(chat_id)
        # print(content_type)
        # for debug
        # if msg["text"] == "/start":
        #     await data.set_user_callback(chat_id, None)
        callback = await data.get_user_callback(chat_id)
        # print(callback)
        if callback and callback["function"] in self.callback:
            try:
                await self.__getattribute__(callback["function"])(
                    *callback["args"], msg=msg, **callback["kwargs"])
            except AttributeError:
                await self.error_handler(chat_id)
            except Exception as e:
                print(e)
                pprint(callback)
                await data.set_user_callback(chat_id, None)
                await self.sender.sendMessage("Что-то пошло не так")
        else:
            if "text" in msg:
                # print(self.commands)
                text = msg["text"]
                if text[0] == "/" and msg["text"][1:] in self.commands:
                    await self.__getattribute__(msg["text"][1:])(_id=chat_id)
                elif text in self.modified_commands:
                    await self.__getattribute__(self.modified_commands[text])(_id=chat_id)
                else:
                    await self.error_handler(chat_id, "Такой команды нет...")
            else:
                await self.sender.sendMessage("Этот тип данных не поддерживается...")
        self.close()

    @async_logger("log/start.log")
    @bot_command
    async def start(self, _id: int):
        """
        Выполняется при начале работы с ботом
        (или при выполнении команды /start)
        """
        member = await self.getChatMember(_id, _id)
        first_name = member["user"]["first_name"]
        last_name = member["user"]["last_name"]
        await data.add_new_user(_id, first_name, last_name)
        await self.sendMessage(_id, 'Добро пожаловать!',
                               reply_markup=self.main_keyboard)
        await self.help(_id)

    @bot_command
    async def help(self, _id: int):
        """
        Отображает подсказку пользователю
        :param _id: id пользователя
        """
        if _id in CREATOR:
            help_message = await data.get_bot_setting("help")
            admin_help_message = await data.get_bot_setting("admin_help")
            creator_help = ("<b>Помощь для создателей:</b>\n"
                            "Доступные команды:\n"
                            "/edit_admin_help - редактирование команды /admin_help\n"
                            "/add_admin - добавление админа")
            help_message += f"\n\n{admin_help_message}\n\n{creator_help}"
        elif _id in ADMIN:
            help_message = await data.get_bot_setting("help")
            admin_help_message = await data.get_bot_setting("admin_help")
            help_message = help_message + "\n"*2 + admin_help_message
        else:
            help_message = await data.get_bot_setting("help")
        await self.sender.sendMessage(help_message, parse_mode="HTML")

    @bot_command
    async def admin_help(self, _id: int):
        """
        Отображает подсказку админу
        :param _id: id пользователя в Телеграм
        """
        if _id in ADMIN:
            help_message = await data.get_bot_setting("admin_help")
            await self.sender.sendMessage(help_message, parse_mode="HTML")
        else:
            await self.sendMessage(_id, "У вас недостаточно прав.")

    @bot_command
    async def graphics(self, _id: int):
        """
        Позволяет пользователю ввести уравнение
        для построения его грайика
        :param _id: id пользователя
        """
        await data.set_user_callback(_id, "get_graphic")
        await self.sender.sendMessage("Введите функуию графика:")

    @bot_command
    async def all_tests(self, _id: int):
        # FixMe
        text = ('Выберите пакет тестов или тест, чтобы '
                'добавить в свои тесты. Чтобы выйти из '
                'режима добавления тестов нажмите "exit".\n\n')
        packages = await data.get_bot_packages()
        p_index = 1
        for name in packages:
            text += f"<b>{name}</b>\n"
            package = await data.get_bot_package(name)
            text += f"<i>{package['description']}</i>\n"
            text += f"Добавить все тесты пакета: /add_package_{p_index}\n"
            text += "Добавить тесты отдельно:\n"
            t_index = 1
            for test in package["tests"]:
                text += f"&gt;&gt;  <b>{test['name']}</b> -> /add_test_{t_index}_pkg_{p_index}\n"
            text += "\n"
            p_index += 1
        inline_keyboard = [[InlineKeyboardButton(text='Выйти', callback_data='exit')]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        await data.set_user_callback(_id, "add_tests")
        await self.sendMessage(_id, text, parse_mode="HTML", reply_markup=reply_markup)

    @bot_command
    async def my_tests(self, _id: int):
        # FixMe
        await self.error_handler(_id)

    @bot_command
    async def results(self, _id: int):
        # FixMe
        await self.error_handler(_id)

    @bot_command
    async def continue_test(self, _id: int):
        # FixMe
        await self.error_handler(_id)

    @bot_command
    async def edit_help(self, _id: int):
        """
        Позволяет админам изменять результат команды /help
        :param _id: id пользователя
        """
        if _id in ADMIN:
            await data.set_user_callback(_id, "edit_bot_setting", kwargs={"setting": "help"})
            await self.sendMessage(_id, "Отправьте текст или файл с описанием функции /help:")
        else:
            await self.sendMessage(_id, "У вас недостаточно прав.")

    @bot_command
    async def edit_admin_help(self, _id: int):
        """
        Позволяет создателям изменять результат команды /admin_help
        :param _id: id пользователя
        """
        if _id in CREATOR:
            await data.set_user_callback(_id, "edit_bot_setting", kwargs={"setting": "admin_help"})
            await self.sendMessage(_id, "Отправьте текст или файл с описанием функции /admin_help:")
        else:
            await self.sendMessage(_id, "У вас недостаточно прав.")

    @bot_command
    async def edit_packages(self, _id: int):
        """
        Выдает меню для редактирования пакетов с тестами
        :param _id: id пользователя в Телеграм
        """
        # Получаем список с названиями пакетов
        packages = await data.get_bot_packages()
        # Кнопки с названиями пакетов под сообщением
        inline_keyboard = [
            [InlineKeyboardButton(text=package,
                                  callback_data=f"package={package}"
                                  )] for package in packages
        ]
        # Кнопка "добавить пакет"
        inline_keyboard.append([InlineKeyboardButton(text='+ Добавить пакет +', callback_data='package=new package')])
        # Кнопка выйти
        inline_keyboard.append([InlineKeyboardButton(text='Выйти', callback_data='close_edit_mode')])
        packages_reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        message = ('Выберите пакет для редактирования '
                   'или нажмите кнопку "Добавить пакет":')
        await data.set_user_callback(_id, "edit_package")
        await self.sendMessage(_id, message, reply_markup=packages_reply_markup)

    @bot_command
    async def add_admin(self, _id: int):
        # FIXME
        if _id in CREATOR:
            await data.set_user_callback(_id, "add_admin_handler")
            await self.sendMessage(_id, "Пришлете мне его контакт:")
        else:
            await self.error_handler(_id, "У вас недостаточно прав.")

    @bot_callback
    async def add_tests(self, msg: dict):
        # FIXME
        content_type, chat_type, chat_id = glance(msg)
        if content_type == "text":
            text = msg["text"]
            if "/add_package_" in text and text[:13] == "/add_package_":
                if text[13:].isdigit():
                    # TODO: тут добавляем сет тестов пользователю
                    await data.set_user_callback(chat_id, None)
                    await self.sendMessage(chat_id, "Принято, не добавлено.")
                else:
                    await self.sendMessage(chat_id, "Чет не то... Повторите ввод:")
            elif "/add_test_" in text and text[:10] == "/add_test_" and "_pkg_" in text:
                # TODO: тут добавляем отдельный тест пользователю
                await data.set_user_callback(chat_id, None)
                await self.sendMessage(chat_id, "Принято, не добавлено.")
            else:
                await self.sendMessage(chat_id, ('Вы находитель в режиме выбора тестов. '
                                                 'Для выхода нажмите "exit" под предидущим сообщением'))
        else:
            await self.sendMessage(chat_id, "Этот тип данных не поддерживается, повторите:")

    @bot_callback
    async def add_admin_handler(self, msg: dict):
        # FixMe
        content_type, chat_type, chat_id = glance(msg)
        if content_type == "contact":
            admin_id = msg["contact"]["user_id"]
            settings.rules["admin"].append(admin_id)
            settings.save()
            await self.sendMessage(chat_id, "Админ добавлен!")
            await data.set_user_callback(chat_id, None)
        else:
            await self.sendMessage(chat_id, "Это не контакт, повторите:")

    @bot_callback
    async def edit_bot_setting(self, msg: dict, setting: str):
        """
        Изменяет один из внутренних параметров бота,
        считывая введенное сообщение
        :param msg: объект сообщения
        :param setting: имя параметра бота
        """
        content_type, chat_type, chat_id = glance(msg)
        if content_type == "text":
            await data.edit_bot_settings(setting, {"text": msg["text"]})
            await data.set_user_callback(chat_id, None)
            await self.sendMessage(chat_id, "Изменения сохранены!")
        elif content_type == "document":
            document = msg['document']
            mime_type = document["mime_type"]
            if mime_type == "text/html" or mime_type == "text/plain":
                file = await self._api_request('getFile', params={
                    'file_id': document['file_id']})
                setting_text = await data.get_tg_document(self._token, file["file_path"])
                await data.edit_bot_settings(setting, {"text": setting_text})
                await data.set_user_callback(chat_id, None)
                await self.sendMessage(chat_id, "Изменения сохранены!")
            else:
                await self.sendMessage(
                    chat_id, f"Тип файлов {mime_type} не поддерживается. Повторите ввод:")
        else:
            await self.sendMessage(chat_id, "Что-то пошло не так, повторите ввод:")

    @bot_callback
    async def get_graphic(self, msg: dict):
        """
        Присылает график функции, введенной в сообщении
        :param msg: объект сообщения
        """
        content_type, chat_type, chat_id = glance(msg)
        try:
            res = await get_plot_link(msg["text"])
            if res is None:
                await self.sender.sendMessage("В формуле ошибка, повторите ввод:")
            else:
                await data.set_user_callback(chat_id, None)
                await self.sender.sendPhoto(res)
        except KeyError:
            await self.sender.sendMessage("Этот тип данных не поддерживается, повторите попытку:")


class MyCallbackQueryHandler(telepot.aio.helper.CallbackQueryOriginHandler, TelegramBot):
    def __init__(self, *args, **kwargs):
        super(MyCallbackQueryHandler, self).__init__(*args, **kwargs)

        # Находим все функции бота
        self._find_bot_functions()

    async def on_callback_query(self, msg):
        """
        Новый метод для орбрабтки нажатий на кнопки
        :param msg:
        :return:
        """
        # pprint(msg)
        message_id = msg["message"]["message_id"]
        query_id, from_id, query_data = glance(msg, flavor='callback_query')
        print(query_id)
        # Удаляем ненужную встроенную клавиатуру
        await self._api_request("editMessageReplyMarkup", params={"chat_id": from_id, "message_id": message_id})
        await self.answerCallbackQuery(query_id, "got it")
        callback = await data.get_user_callback(from_id)
        print("CALLBACK: ", callback)
        if callback:
            try:
                await self.__getattribute__(callback["function"])(
                    *callback["args"], msg, **callback["kwargs"])
            except AttributeError:
                if query_data in self.commands:
                    await self.__getattribute__(query_data)(from_id, message_id=message_id)
                else:
                    print("что-то явно тут не так...")
            except Exception as e:
                print(e)
        else:
            if query_data in self.commands:
                await self.__getattribute__(query_data)(from_id, message_id=message_id)
            else:
                print("что-то явно тут не так...")
        # func_name, kwargs = split_query(query_data)
        # print(func_name, kwargs)
        # try:
        #     await self.queries[func_name](from_id, **kwargs)
        # except Exception as e:
        #     print(e)
        #     await self.sendMessage(from_id, "Что-то пошло не так...")

    @bot_command
    async def exit(self, _id: int, message_id: int):
        """
        Производит выход из режима ожидания какой-либо функции,
        удаляет сообщение, под которым была кнопка exit
        :param _id: id пользователя Телеграм
        :param message_id: id сообщения (чтобы его можно было удалить)
        """
        await self._api_request("deleteMessage", params={"chat_id": _id, "message_id": message_id})
        await data.set_user_callback(_id, None)
        await self.sendMessage(_id, "Вы вышли. Если не знаете, что делать дальше, нажмите /help")

    async def on__idle(self, event):
        await asyncio.sleep(5)
        # await self.editor.deleteMessage()
        self.close()


class AlarmSetter(TelegramBot):
    def __init__(self, *args, **kwargs):
        super(AlarmSetter, self).__init__(*args, **kwargs)

        # 1. Customize the routing table:
        #      On seeing an event of flavor `_alarm`, call `self.on__alarm`.
        # To prevent flavors from colliding with those of Telegram messages,
        # events are given flavors prefixed with `_` by convention. Also by
        # convention is that the event-handling function is named `on_`
        # followed by flavor, leading to the double underscore.
        self.router.routing_table['_alarm'] = self.on__alarm
        # self.router.routing_table['_test_end'] = self.on__test_end

    # 2. Define event-handling function
    async def on__alarm(self, event):
        print(event)  # see what the event object actually looks like
        await self.sender.sendMessage('Beep beep, time to wake up!')

    async def on_chat_message(self, msg):
        try:
            delay = float(msg['text'])

            # 3. Schedule event
            #      The second argument is the event spec: a 2-tuple of (flavor, dict).
            # Put any custom data in the dict. Retrieve them in the event-handling function.
            self.scheduler.event_later(delay, ('_alarm', {'payload': delay}))
            await self.sender.sendMessage('Got it. Alarm is set at %.1f seconds from now.' % delay)
        except ValueError:
            await self.sender.sendMessage('Not a number. No alarm set.')


if __name__ == "__main__":
    bot = telepot.aio.DelegatorBot(TOKEN, [
        pave_event_space()(
            per_chat_id(), create_open, MyChatHandler, timeout=3),
        pave_event_space()(
            per_callback_query_origin(), create_open,
            MyCallbackQueryHandler, timeout=10),
    ])

    # Тестирую события и отложенные уведомления:
    # bot = telepot.aio.DelegatorBot(TOKEN, [
    #     pave_event_space()(
    #         per_chat_id(), create_open, AlarmSetter, timeout=10),
    # ])

    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    print('Listening ...')

    loop.run_forever()
