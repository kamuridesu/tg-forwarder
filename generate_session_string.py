import asyncio
import os
from pyrogram import Client


async def main():
    client = Client(
        name=":memory:",
        api_id=os.getenv("TELEGRAM_API_ID"),
        api_hash=os.getenv("TELEGRAM_API_HASH"),
    )
    async with client:
        print(await client.export_session_string())


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    loop.run_until_complete(asyncio.gather(task))
    loop.run_forever()
