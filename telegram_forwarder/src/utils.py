"""Functions and classes that may be util in the project"""
import asyncio
import time
import typing
from .database import Datasource
from aiogram.types import Message
from pyrogram.errors.exceptions.flood_420 import FloodWait


class Progress:
    """Updates the message with the percentage downloaded"""

    def __init__(self, message: Message):
        self.message = message
        self.enabled = True
        self.message_to_send = "Downloading... "
        self.start_time = time.perf_counter()
        self.__last_message = ""

    async def update(self, count: int | float, total: int | float, message: str = ""):
        if message == "":
            message = self.message_to_send
        """Updates the message with the download percentage every 10 seconds"""
        total_time = time.perf_counter() - self.start_time
        if total_time > 10 or total_time < 1:
            if total_time > 10:
                self.start_time = time.perf_counter()
            percents = round(100 * count / float(total), 1)
            message = f"{message} {percents}%"
            if message != self.__last_message:
                await self.message.edit_text(message)
                self.__last_message = message


async def aenumerate(asequence: typing.AsyncIterable, start: int = 0):
    """Asynchronously enumerate an async iterator from a given start value"""
    n = start
    async for elem in asequence:
        yield n, elem
        n += 1


def redo_pulling(db: Datasource) -> bool:
    last_time = db.get_last_date()
    return time.time() - last_time >= 86400


def handle_flood_wait(func):
    async def wrapper(*args, **kwargs):
        while True:
            try:
                return await func(*args, **kwargs)
            except FloodWait as e:
                sleep_time = int(str(e).split("A wait of ")[1].split(" ")[0])
                await asyncio.sleep(sleep_time)
    return wrapper
