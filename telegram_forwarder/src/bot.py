from . import config
from .parsers import parse_message
from .handlers import forward

from aiogram import Bot, Dispatcher
from aiogram.bot.api import TelegramAPIServer
from aiogram.types import Message

if config.API_SERVER:
    bot = Bot(
        token=config.BOT_TOKEN, server=TelegramAPIServer.from_base(config.API_SERVER)
    )
else:
    print("WARNING: using Telegram's default bot API will limit your bot")
    print("Some of the limits are:")
    print("  20MB limit for downloading files")
    print("  50MB limit for uploading files")
    print("Please, consider running your own bot API server to avoid those limits.")
    bot = Bot(token=config.BOT_TOKEN)


dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands=["start", "help"])
async def send_help(message: Message):
    return await message.reply(
        f"""Send me a link for a public group and I'll forward all the messages to you.
"""
    )


@dispatcher.message_handler()
async def handle_all_messages(message: Message):
    message_data = await parse_message(message.text)
    if message_data["type"] == "error":
        return await message.reply(message_data["message"])
    elif message_data["type"] == "forward":
        await forward(message, message_data["origin"], message_data["target"])

