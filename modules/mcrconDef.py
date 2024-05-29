from mcrcon import MCRcon
import os
import dotenv
import logging
import timeout_decorator

dotenv.load_dotenv()
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PASS = os.getenv("SERVER_PASS")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
mcr = MCRcon(SERVER_ADDRESS, SERVER_PASS)

@timeout_decorator.timeout(5)
def mc_getlist():
    try:
        mcr.connect()
        res = mcr.command("list")
        mcr.disconnect()
        return res
    except Exception as e:
        logging.error(f"エラー発生：{e}")
        return None