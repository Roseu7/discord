import os
import dotenv
import socket
import logging
from mcrcon import MCRcon
import asyncio

dotenv.load_dotenv()
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PASS = os.getenv("SERVER_PASS")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

def sync_mc_getlist():
    try:
        with MCRcon(SERVER_ADDRESS, SERVER_PASS, SERVER_PORT) as mcr:
            log = mcr.command("list")
            return log
    except (socket.timeout, asyncio.TimeoutError):
        logging.error("接続がタイムアウト")
        return None
    except Exception as e:
        logging.error(f"エラー発生：{e}")
        return None

async def mc_getlist():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, sync_mc_getlist)