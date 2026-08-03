import asyncio
from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
import logging

load_dotenv()

dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("BOT_TOKEN is not set in the environment variables.")
    bot = Bot(token=token)

    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
