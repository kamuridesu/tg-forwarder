import asyncio
import telegram_forwarder


def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(telegram_forwarder.start())
    loop.run_until_complete(asyncio.gather(task))
    loop.run_forever()


if __name__ == "__main__":
    main()
