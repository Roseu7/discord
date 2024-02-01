from ossapi import Ossapi
import dotenv
import os
from decimal import Decimal, ROUND_HALF_UP

dotenv.load_dotenv()
OSU_ID = os.getenv("OSU_ID")
OSU_SECRET = os.getenv("OSU_SECRET")
api = Ossapi(OSU_ID, OSU_SECRET)

def osu_id_convert(name):
    try:
        id = api.user(name).id
    except:
        return None
    return id

def osu_name_convert(id):
    try:
        name = api.user(id).username
    except:
        return None
    return name

def osu_now_pp(id):
    return Decimal(str(api.user(id).statistics.pp)).quantize(Decimal('0'), ROUND_HALF_UP)