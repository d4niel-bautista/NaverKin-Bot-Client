import random
import asyncio

async def short_sleep(time):
    random.seed()
    await asyncio.sleep(round(random.uniform(time, time + 10), 2))

async def long_sleep(time):
    random.seed()
    await asyncio.sleep(round(random.uniform(time + 2, time + 40), 2))