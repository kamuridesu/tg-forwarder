from .src.bot import dispatcher
from .src.client import client
from .src.download import MessageData
from .src.database import Datasource


async def start():
    async with client:
        print("[!] Bot started!", flush=True)
        await dispatcher.start_polling()


__all__ = ("Downloader", "download_media", "Datasource", "MessageData")
