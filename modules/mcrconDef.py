from mcrcon import MCRcon
import os
import dotenv

dotenv.load_dotenv()
SERVER_ADDRESS = os.getenv("SERVER_ADDRESS")
SERVER_PASS = os.getenv("SERVER_PASS")
SERVER_PORT = os.getenv("SERVER_PORT")

def mc_getlist():
    with MCRcon(SERVER_ADDRESS, SERVER_PASS, SERVER_PORT) as mcr:
        log = mcr.command(list)
        return log
