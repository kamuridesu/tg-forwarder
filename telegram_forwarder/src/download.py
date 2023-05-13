import asyncio
import os
from tempfile import NamedTemporaryFile
from typing import Any, Callable, Coroutine

from pyrogram.enums import MessageMediaType
from pyrogram.types import Message

from .client import client
from .database import Datasource
from .utils import Progress, handle_flood_wait


class MessageData:
    def __init__(self, message: Message, file_name: str):
        self.message = message
        self.file_name = file_name

    @handle_flood_wait
    async def download(self):
        await self.message.download(file_name=self.file_name)


class Downloader:
    def __init__(self, db: Datasource, chat_id: str, target_id: str):
        self.db = db
        self.chat_id = chat_id
        self.target_id = target_id

    @staticmethod
    def get_send_function_and_ext(
        message: Message,
    ) -> Callable[[str, Any, str], Coroutine[Any, Any, Message]]:
        funcs_map = {
            MessageMediaType.PHOTO: {
                "function": client.send_photo,
                "id": message.photo.file_id if message.photo else None,
                "type": "image/jpg",
            },
            MessageMediaType.VIDEO: {
                "function": client.send_video,
                "id": message.video.file_id if message.video else None,
                "type": message.video.mime_type if message.video else None,
                "filename": message.video.file_name if message.video else None,
            },
            MessageMediaType.ANIMATION: {
                "function": client.send_animation,
                "id": message.animation.file_id if message.animation else None,
                "type": message.animation.mime_type if message.animation else None,
            },
            MessageMediaType.DOCUMENT: {
                "function": client.send_document,
                "id": message.document.file_id if message.document else None,
                "type": message.document.mime_type if message.document else None,
                "filename": message.document.file_name if message.document else None,
            },
            MessageMediaType.STICKER: {
                "function": client.send_sticker,
                "id": message.sticker.file_id if message.sticker else None,
                "type": message.sticker.mime_type if message.sticker else None,
            },
        }
        for enum in funcs_map:
            if message.media == enum:
                return funcs_map[enum]

    async def start(self, callback: Progress):
        messages = self.db.get_media_messages(self.chat_id)
        download_tasks = []
        for index, message_id in enumerate(messages):
            if self.db.check_if_sent(self.chat_id, message_id):
                continue
            message = await client.get_messages(self.chat_id, message_id)
            data = self.get_send_function_and_ext(message)
            if data is None:
                continue
            function = data["function"]
            mime = data["type"]
            file_name = data.get("filename", "")
            print(mime)
            extension = mime.split("/")[1]
            with NamedTemporaryFile(
                suffix=f".{extension}", delete=False, prefix="tgbot-"
            ) as file:
                await callback.update(index, len(messages), "Forwarding...")
                message_data = MessageData(message, file.name)
                download_task = asyncio.ensure_future(message_data.download())  # Ensure future and await the coroutine
                download_tasks.append((message_id, message, function, file, file_name, download_task))
                if len(download_tasks) >= 16:
                    await self.process_download_tasks(download_tasks)
                    download_tasks = []

        if download_tasks:
            await self.process_download_tasks(download_tasks)

    async def process_download_tasks(self, download_tasks):
        await asyncio.gather(*[task[-1] for task in download_tasks])  # Wait for all download tasks to complete

        for task in download_tasks:
            message_id, message, function, file, file_name, _ = task
            await self.send_media(message_id, message, function, file, file_name)

    @handle_flood_wait
    async def send_media(self, message_id, message, function, file, filename=""):
        try:
            if filename:
                await function(self.target_id, file.name, message.text, file_name=filename)
            else:
                await function(self.target_id, file.name, message.text)
            self.db.mark_as_sent(self.chat_id, message_id)
        except ValueError:
            pass
        try:
            os.remove(file.name)
        except Exception:
            pass
