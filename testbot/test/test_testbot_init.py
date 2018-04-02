import asyncio
from testbot import bot_command, bot_callback


class Test:
    @bot_callback
    async def test_bot_callback(self, msg: dict):
        print(msg)

    @bot_command
    async def test_bot_command(self, _id: int):
        print(_id)


t = Test()
loop = asyncio.get_event_loop()
loop.run_until_complete(t.test_bot_callback(dict()))
loop.run_until_complete(t.test_bot_command(10))