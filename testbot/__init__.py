import time

__version__ = "0.4.0"


def bot_command(func):
    """
    Декоратор-интерфейс для команд бота
    """
    if "_id" not in func.__code__.co_varnames:
        raise NameError(
            "Интерфейс функции не соотетствует bot_command функции")
    annotations = func.__annotations__
    if "_id" in annotations:
        if 'int' not in str(annotations["_id"]):
            raise NameError("аннотация не соответствует int*")
    else:
        raise NameError("нет аннотации для параметра _id")

    async def wrapped(self, _id, **kwargs):
        await func(self, _id, **kwargs)

    wrapped.__name__ = func.__name__
    wrapped.__doc__ = "<bot_command>"
    return wrapped


def bot_callback(func):
    """
    Декоратор-интерфейс для callback-функций бота
    """
    if "msg" not in func.__code__.co_varnames:
        raise NameError(
            "Интерфейс функции не соотетствует bot_callback функции")
    annotations = func.__annotations__
    if "msg" in annotations:
        if 'dict' not in str(annotations["msg"]):
            raise NameError("аннотация не соответствует dict*")
    else:
        raise NameError("нет аннотации для параметра msg")

    async def wrapped(self, msg, **kwargs):
        await func(self, msg, **kwargs)

    wrapped.__name__ = func.__name__
    wrapped.__doc__ = "<bot_callback>"
    return wrapped


def async_logger(file: str):
    def wrapper(func):
        async def wrapped(*args, **kwargs):
            with open(file, "a", encoding="utf-16") as f:
                f.write(time.ctime(time.time()) + "\n")
                f.write(func.__name__ + " ")
                f.write("args: " + str(args) + " kwargs: " + str(kwargs) + "\n")
                try:
                    r = await func(*args, **kwargs)
                    f.write(f"returned: {r}")
                    f.write("\nOk\n\n")
                except Exception as e:
                    f.write("exception: " + str(e))
                    f.write("\nFailed\n\n")
                    raise e
        wrapped.__name__ = func.__name__
        wrapped.__annotations__ = func.__annotations__
        wrapped.__doc__ = func.__doc__
        return wrapped
    return wrapper
