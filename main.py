import asyncio
from bot.main_bot import start_bot, stop_bot

if __name__ == '__main__':
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        stop_bot()
