import aiohttp
import asyncio

from settings import settings

"""
Подробная документация:
https://tech.yandex.ru/disk/api/concepts/about-docpage/
"""

ACCESS_TOKEN = settings["yandex_disk"]["access"][0]["access_token"]
ID =  settings["yandex_disk"]["app"]["ID"]
SECRET =  settings["yandex_disk"]["app"]["password"]


async def _api_request(url: str, http_method="get", headers={}, params={}, data=None):
    """
    Выполняет запрос к API Яндекс диска
    :param url: URL метода API
    :param http_method: метод передачи данных (get, post, put и т.д.)
    :param headers: заголовки запроса
    :param params: параметры запроса
    :param data: данные запроса (для post и put запросов)
    :return: JSON-коллекция ответа
    """
    http_method = http_method.lower()
    headers["Authorization"] = "OAuth {token}".format(token=ACCESS_TOKEN)
    async with aiohttp.ClientSession(headers=headers) as session:
        if http_method == "post":
            async with session.post(url, params=params, data=data) as resp:
                return await resp.json()
        elif http_method == "put":
            async with session.put(url, params=params, data=data) as resp:
                return await resp.json()
        else:
            async with session.get(url, params=params, data=data) as resp:
                return await resp.json()


async def get_download_url(path: str):
    """
    Получает ссылку для скачивания файла с Яндекс диска
    :param path: путь к файлу на Яндекс диске
    :return: ссылка на скачивание файла
    """
    resp_json = await _api_request(
        "https://cloud-api.yandex.net/v1/disk/resources/download",
        http_method="get",
        params={"path": path}
    )
    return resp_json["href"]


async def get_upload_url(path: str, overwrite="true"):
    """
    Получает ссылку для загрузки файла на Яндекс диск
    :param path: путь к файлу на Яндекс диске
    :param overwrite: перезаписывать файл или нет
    :return: ссылка для загрузки файла
    """
    resp_json = await _api_request(
        "https://cloud-api.yandex.net/v1/disk/resources/upload",
        http_method="get",
        params={"path": path, "overwrite": overwrite}
    )
    return resp_json["href"]


async def upload_file(path: str, data: bytes=None, overwrite=True):
    """
    Загружает файл на Яндекс диск
    :param path: путь к файлу на Яндекс диске
    :param data: файл в байтовом представлении
    :param overwrite: перезаписывать файл или нет
    :return: статус операции
    """
    overwrite = "true" if overwrite else "false"
    upload_url = await get_upload_url(path, overwrite)
    async with aiohttp.ClientSession() as session:
        async with session.put(upload_url, data=data) as resp:
            return resp.status


async def publish_file(path: str):
    """
    Публикует файл с Яндекс диска по ссылке
    :param path: путь к файлу на Яндекс диске
    :return: ссылка на метаданные о файле
    """
    resp_json = await _api_request(
        "https://cloud-api.yandex.net/v1/disk/resources/publish",
        http_method="put",
        params={"path": path}
    )
    return resp_json["href"]


async def get_access_token(code: int):
    """
    Получает токен авторизации конкретного пользователя
    по коду, который был дан по ссылке
    https://oauth.yandex.ru/authorize?response_type=code&client_id=ID
    :param code: код подтверждения
    :return: JSON объект с настройками конкретного пользователя
    """
    # TODO
    # Данная функция не тестироваласть, поскольку
    # в первый раз токен был получен в ручную
    url = "https://oauth.yandex.ru/token"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": ID,
            "client_secret": SECRET
        }) as resp:
            return await resp.json()


if __name__ == "__main__":
    from pprint import pprint
    async def test():
        pprint(await get_download_url("app:/test.txt"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())