from asyncio import sleep
from aiogram.types import Message as TMessage
from pyrogram.errors.exceptions.bad_request_400 import UserAlreadyParticipant, InviteHashInvalid, InviteHashEmpty, InviteHashExpired, UserBannedInChannel
from .client import client, retrieve_chat_history
from .database import Datasource
from .utils import Progress, aenumerate, redo_pulling, handle_flood_wait
from .download import Downloader

db = Datasource()
progresses: dict[str, Progress] = {}


@handle_flood_wait
async def join_chat(chat_invite: str, message: TMessage) -> bool:
    try:
        await client.join_chat(chat_invite)
        return True
    except (UserAlreadyParticipant):
        return True
    except (InviteHashInvalid, InviteHashEmpty, InviteHashExpired, UserBannedInChannel) as e:
        await message.reply(f"Error! Could not join chat! Reason: {e.__class__}")
        return False


@handle_flood_wait
async def list_messages(chat_id: str):
    db_data = db.get_media_messages(chat_id)
    last_id = 0
    if db_data:
        last_id = min(db_data)
    chat_history = await retrieve_chat_history(chat_id, last_id)
    total = await client.get_chat_history_count(chat_id)
    async for index, message in aenumerate(chat_history):
        if message.media or message.document:
            db.insert_chat(chat_id, message.id)
        await progresses[chat_id].update(
            index + 1, total, "Loading all media files from chat..."
        )
    await progresses[chat_id].message.edit_text(
        "All messages loaded! Starting download..."
    )


@handle_flood_wait
async def forward(original_message: TMessage, origin: dict, target: dict):
    if origin["private"]:
        if not (await join_chat(origin["hash"], original_message)):
            return
    if not (await join_chat(target["hash"], original_message)):
        return
    origin_id = (await client.get_chat(origin["hash"])).id
    target_id = (await client.get_chat(target["hash"])).id
    message = await original_message.reply("Loading all media files from chat...")
    progress = Progress(message)
    progresses[origin_id] = progress
    await list_messages(origin_id)
    downloader = Downloader(db, origin_id, target_id)
    await downloader.start(progress)
    await progress.message.edit_text("All messages forwarded!")
    del progresses[origin["hash"]]
