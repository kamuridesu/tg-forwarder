from datetime import datetime
from typing import AsyncGenerator, Coroutine, Any
from . import config
from pyrogram import Client
from pyrogram.types import Message
from pyrogram.utils import zero_datetime


client = Client(
    name=":memory:",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
    no_updates=True,
    takeout=True,
    sleep_threshold=700
)


async def retrieve_chat_history(
    chat_id: str, last_saved_message_id: int = 0
) -> AsyncGenerator[Message, None] | None:
    messages = client.get_chat_history(chat_id=chat_id, offset_id=last_saved_message_id)
    return messages


async def get_public_chat_id_from_name(chat_name: str) -> Coroutine[Any, Any, str]:
    client.get_chat(chat_name)
