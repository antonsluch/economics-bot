import asyncio
import xml.etree.ElementTree as ET
import aiohttp

from testbot.settings import settings

APP_ID = settings["wolfram_alpha"]["id"]


@asyncio.coroutine
def wolfram_xml2dict(xml_string: str):
    """
    Преобразует xml-строку, полученную от API wolfram alpha в словарь
    :param xml_string: xml-строка
    :return: преобразованный словарь
    """
    root = ET.fromstring(xml_string)
    res = root.attrib
    res["pods"] = []
    for pod in root:
        res["pods"].append({pod.tag: pod.attrib})
        res["pods"][-1][pod.tag]["subpod"] = []
        for subpod in pod:
            res["pods"][-1][pod.tag]["subpod"] = subpod.attrib
            for child in subpod:
                res["pods"][-1][pod.tag]["subpod"][child.tag] = child.attrib
    return res


async def get_plot_link(query_string: str):
    """
    Получает график функции с помощью wolfram alpha API
    :param query_string: строка, содержащая функцию
    :return: ссылка на график
    """
    app_id = "V9K3LJ-Y3WJHTRWYL"
    link = f"http://api.wolframalpha.com/v2/query?input={query_string}&appid={APP_ID}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                text = await resp.text()
                data = await wolfram_xml2dict(text)
    except aiohttp.client_exceptions.ClientConnectorError as e:
        return None
    if "pods" in data:
        for pod in data["pods"]:
            if "pod" in pod and "title" in pod["pod"] and (pod["pod"]["title"] == "Plot" or
                                                           pod["pod"]["title"] == "Plots" or
                                                           pod["pod"]["title"] == "Implicit plot"):

                try:
                    return pod["pod"]["subpod"]["img"]["src"]
                except KeyError:
                    return None
    return None


if __name__ == "__main__":
    async def test():
        print(await get_plot_link("y=x^3"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())