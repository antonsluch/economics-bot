from pprint import pprint
import contracts



def handle_msg(arg):
    def decorator(func):
        def wrapper():
            print("start " + arg)
            func()
            print("end")
        return wrapper
    return decorator


@handle_msg("/hello")
def test():
    print("test")


# test()


class StatusError(Exception):
    def __init__(self):
        pass


class WrongStatusException(Exception):
    def __init__(self):
        pass


async def error(user_id, error_msg):
    print(error_msg, user_id)


ADMIN = {111, 222}
CREATOR = 333


def check_status(status):
    """
    Декоратор для проверки прав пользователя

    :param status: Статус пользователя для проверки (admin, creator)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            print(args, kwargs)
            if "msg" in kwargs and "user_id" in kwargs["msg"]:
                user_id = kwargs["msg"]["user_id"]
                if status == "admin":
                    if user_id in ADMIN or user_id == CREATOR:
                        return await func(*args, **kwargs)
                    else:
                        return await error(user_id, "У вас недостаточно прав для этого действия.")
                elif status == "creator":
                    if user_id == CREATOR:
                        return await func(*args, **kwargs)
                    else:
                        return await error(user_id, "У вас недостаточно прав для этого действия.")
                else:
                    raise WrongStatusException
            else:
                raise ValueError
        return wrapper
    return decorator


@check_status("creator")
async def start(msg):
    print(msg["user_id"])


@check_status("admin")
async def hello(msg):
    print("hello", msg)


commands = {
    "/start": start,
    "/hello": hello
}


async def on_message(msg):
    if msg["text"] in commands:
        await commands[msg["text"]](msg=msg)
    else:
        print("no command...")


# loop = asyncio.get_event_loop()
# loop.create_task(on_message(msg={"user_id": 222,
#                             "text": "/hello"}))
# loop.create_task(on_message(msg={"user_id": 333,
#                             "text": "/start"}))
# loop.create_task(on_message(msg={"user_id": 111,
#                             "text": "/start"}))
# loop.run_forever()



@contracts.contract
def test(a: 'int,>0', b: 'int,>0'):
    print(a * b)


@contracts.contract
def summm(arr):
    """

    :param arr: array
    :type arr: list[>0](int|float,<100)
    :return:
    """
    print(sum(arr))


@contracts.contract(arr='dict[>0]((int|float):(int,>0)|(float,<0))')
def xxx(arr):
    print(arr)


@contracts.contract
def factorize(x):
    """ Factorize integer positive and return its factors.
        :type x: int,>=0
        :rtype: tuple[N],N>0
    """
    pass


def decorator(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = "<bot_command>"
    return wrapper


class Test:
    def __init__(self):
        self.callback = []
        self.commands = []
        self._find_bot_functions()

    def _find_bot_functions(self):
        for attr_name in self.__dir__():
            attr = self.__getattribute__(attr_name)
            if attr:
                if attr.__doc__ == "<bot_callback>":
                    self.callback.append(attr_name)
                if attr.__doc__ == "<bot_command>":
                    self.commands.append(attr_name)

    @decorator
    def ttest(self):
        print(0)


t = Test()
print(t.callback, t.commands)


class ChatHandler:
    """
    Старые функции хэндлера
    """
    async def _error(self, error_msg: str="Такой команды нет..."):
        """
        Обрабатывает некорректый ввод пользователя
        или нарушение прав доступа
        """
        await self.sender.sendMessage(error_msg)


    async def help(self, msg):
        content_type, chat_type, chat_id = glance(msg)
        help_message = "Помощь..."
        if chat_id == CREATOR:
            help_message = await data.get_bot_setting("help")
            admin_help_message = await data.get_bot_setting("admin_help")
            help_message = help_message + "\n"*2 + admin_help_message
        elif chat_id in ADMIN:
            help_message = await data.get_bot_setting("help")
            admin_help_message = await data.get_bot_setting("admin_help")
            help_message = help_message + "\n"*2 + admin_help_message
        else:
            help_message = await data.get_bot_setting("help")
        await self.sender.sendMessage(help_message, parse_mode="HTML")

    async def tests(self, msg):
        """
        Отсылает пользователю все его доступные тесты
        :param msg: объект сообщения
        """
        # TODO
        pass

    async def all_tests(self, msg):
        """
        Отсылает пользователю все тесты бота
        :param msg: объект сообщения
        """
        # TODO
        pass

    async def graphics(self, msg):
        """
        TODO
        :param msg:
        :return:
        """
        content_type, chat_type, chat_id = glance(msg)
        await data.set_user_callback(chat_id, "get_graphic")
        await self.sender.sendMessage("Введите функуию графика:")

    async def get_graphic(self, msg):
        """
        TODO
        :param msg:
        :return:
        """
        content_type, chat_type, chat_id = glance(msg)
        try:
            res = await get_plot_link(msg["text"])
            if res == None:
                await self.sender.sendMessage("В формуле ошибка, повторите ввод:")
            else:
                await data.set_user_callback(chat_id, None)
                await self.sender.sendPhoto(res)
        except KeyError:
            await self.sender.sendMessage("Этот тип данных не поддерживается, повторите попытку:")

    @check_status(status="admin")
    async def edit_help(self, msg):
        """
        Позволяет администратору отредактировать сообщение,
        выдаваемое пользователям по команде /help
        :param msg: объект ообщения
        """
        content_type, chat_type, chat_id = glance(msg)
        await data.set_user_callback(chat_id, function_name="_edit_bot_setting",
                                     args=[], kwargs={"setting_name": "help"})
        await self.sender.sendMessage("Отправьте текст или файл с описанием функции /help")

    @check_status(status="creator")
    async def edit_admin_help(self, msg):
        """
        Позволяет создателю отредактировать сообщение,
        выдаваемое администраторам по команде /help
        :param msg: объект ообщения
        """
        content_type, chat_type, chat_id = glance(msg)
        await data.set_user_callback(chat_id, function_name="_edit_bot_setting",
                                     args=[], kwargs={"setting_name": "admin_help"})
        await self.sender.sendMessage("Отправьте текст или файл с описанием функции /help для администраторов:")

    async def _edit_bot_setting(self, msg: dict, setting_name: str):
        """
        Редактирует внутренние переменные бота.
        Способ вызова: свойство callback пользователя
        :param msg: сообщение, содержащее изменения
        :param setting_name: имя переменной для изменения
        """
        content_type, chat_type, chat_id = glance(msg)
        changing = {}
        if "text" in msg:
            changing = {"text": msg["text"]}
        elif content_type == "document":
            document = msg['document']
            mime_type = document["mime_type"]
            if mime_type == "text/html" or mime_type == "text/x-markdown":
                file = await self._api_request('getFile', params={
                    'file_id': document['file_id']})
                setting_text = await data.get_tg_document(self._token, file["file_path"])
                changing = {"text": setting_text}
        if changing:
            await data.edit_bot_settings(setting_name, changing)
            await data.set_user_callback(chat_id, None)
            await self.sender.sendMessage("Изменения сохранены")
        else:
            await self.sender.sendMessage("Данный тип файлов не поддерживается в этой функции. "
                                          "Повторите отправку:")

    @check_status(status="admin")
    async def edit_packages(self, msg):
        """
        Выдает меню для редактирования пакетов с тестами
        :param msg: сообщение
        """
        # Получаем список с названиями пакетов
        packages = await data.get_bot_packages()
        # Кнопки с названиями пакетов под сообщением
        inline_keyboard = [
            [InlineKeyboardButton(text=package,
                                  callback_data="ed_pkg?pkg={}".format(package)
                                  )] for package in packages
        ]
        # Кнопка "добавить пакет"
        inline_keyboard.append([InlineKeyboardButton(text='+ Добавить пакет +', callback_data='add_package')])
        # Кнопка выйти
        inline_keyboard.append([InlineKeyboardButton(text='Выйти', callback_data='exit')])
        packages_reply_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        message = ('Выберите пакет для редактирования '
                   'или нажмите кнопку "Добавить пакет":')
        await self.sender.sendMessage(message, reply_markup=packages_reply_markup)

    async def edit_package_setting(self, msg: dict, package: str, setting: str):
        # TODO: docks
        content_type, chat_type, chat_id = glance(msg)
        if "text" in msg:
            text = msg["text"]
            if setting == "name" and len(bytes(text, "utf-8")) > 30:
                await self.sender.sendMessage("Превышен максимальный размер имени, повторите:")
            else:
                new_pkg = package
                if setting == "name":
                    new_pkg = text
                r = await data.edit_bot_package(package, {setting: text})
                if r:
                    await data.set_user_callback(chat_id, None)
                    await self.sender.sendMessage("Изменения сохранены, продолжить?",
                                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                                      [InlineKeyboardButton(text="Да",
                                                                            callback_data=f"ed_pkg?pkg={new_pkg}"),
                                                       InlineKeyboardButton(text="Нет", callback_data="0")]
                                                  ]))
                else:
                    await self.sender.sendMessage("Что-то пошло не так, повторите ввод:")
        else:
            await self.sender.sendMessage("Что-то пошло не так, повторите ввод:")

    async def photo_handler(self, msg):
        print(msg)

    async def document_handler(self, msg):
        print(msg)

      # let Quizzer take over
