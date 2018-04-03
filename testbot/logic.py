# -*- coding: utf-8 -*-
import re
import asyncio
from pprint import pprint
import matplotlib.pyplot as plt
from testbot.settings import settings
import PIL
import numpy as np
from testbot.data import db


async def get_user_results(user_id: int):
    res = await db.users.find_one({"tg_id": user_id},
                                  projection=["tests.name", "tests.questions.points", "tests.questions.result"])
    tests = res["tests"]

    x = []
    y = []
    for test in tests:
        x.append(test["name"])
        questions = test["questions"]
        s = 0
        r = 0
        for question in questions:
            s += question["points"]
            if question["result"] is None:
                r += 0
            else:
                r += question["result"]
        y.append((r / s)*100)
    # fig, ax = plt.subplots(figsize=(5, 3))
    # ax.stackpbar(range(len(x)), y)

    xxx = plt
    xxx.bar(range(len(x)), y, bottom=None, hold=None, data=None)
    xxx.xticks(range(len(x)), x, rotation='vertical')
    # xxx.show()
    xxx.draw()
    fig = xxx.plot()
    pprint(fig)

    # fig.tight_layout()

    # pprint(tests)

    fig = plt.figure()
    fig.add_subplot()

    fig.canvas.draw()

    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    # print(data)

    # img = PIL.Image.fromarray(data)
    # with open("test.png", "wb+") as f:
    #     f.write(img._repr_png_())

    plt.close()




if __name__ == '__main__':
    async def test():
        await get_user_results(77513276)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())
