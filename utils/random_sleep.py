import random
import asyncio

async def short_sleep(time):
    random.seed()
    sleep_time = round(random.uniform(time, time + 10), 2)
    await asyncio.sleep(sleep_time)

async def long_sleep(time):
    random.seed()
    sleep_time = round(random.uniform(time + 2, time + 40), 2)
    await asyncio.sleep(sleep_time)