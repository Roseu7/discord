from mcrcon import MCRcon
import os
import dotenv
import socket
import logging

dotenv.load_dotenv()
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PASS = os.getenv("SERVER_PASS")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

def mc_getlist():
    try:
        with MCRcon(SERVER_ADDRESS, SERVER_PASS, SERVER_PORT) as mcr:
            log = mcr.command("list")
            return log
    except socket.timeout:
        logging.error("接続がタイムアウト")
    except Exception as e:
        logging.error(f"エラー発生：{e}")
        return None