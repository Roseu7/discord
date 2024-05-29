from mcrcon import MCRcon
import os
import dotenv
import socket
import logging
import asyncio

dotenv.load_dotenv()
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PASS = os.getenv("SERVER_PASS")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
mcr = MCRcon(SERVER_ADDRESS, SERVER_PASS)

def mc_getlist():
    try:
        mcr.connect()
        res = mcr.command("list")
        mcr.disconnect()
        return res
    except (socket.timeout, asyncio.TimeoutError):
        logging.error("接続がタイムアウト")
        return "接続がタイムアウトしました"
    except Exception as e:
        logging.error(f"エラー発生：{e}")
        return f"エラー発生：{e}"