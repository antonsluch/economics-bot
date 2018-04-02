# -*- coding: utf-8 -*-
import re
import asyncio
from pprint import pprint
from random import randint

from testbot.settings import settings
from testbot.data import db


async def get_user_results(user_id: int):
    res = await db.users.find_one({"tg_id": user_id}, projection=["tests"])
    tests = res["tests"]
    pprint(tests)


if __name__ == '__main__':
    async def test():
        await get_user_results(77513276)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
