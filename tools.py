import argparse
import asyncio
import itertools
import os

import aiohttp
from dotenv import load_dotenv

from schemas import LaunchArgs

load_dotenv()
ADSPOWER_URI = os.getenv("ADSPOWER_URI")

async def map_profile_name_to_id():
    PAGE_SIZE = 100
    profiles = []
    result = {}

    for page in itertools.count(start=1):
        params = {"page_size": PAGE_SIZE, "page": page}
        async with aiohttp.request("GET", ADSPOWER_URI + "/api/v1/user/list", params=params) as response:
            response_json = await response.json()

        current_page = response_json["data"]["list"]

        profiles.extend(current_page)
        if len(current_page) < PAGE_SIZE:
            break
        await asyncio.sleep(1)
    for profile in profiles:
        result[profile["name"]] = profile["user_id"]
    return result

def get_launch_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profiles", type=str, help="Путь к csv файлу с аккаунтами. Default: profiles.csv")
    parser.add_argument("-r", "--rounds", type=int, help="Количество кругов. Default: 1")
    parser.add_argument("-t", "--threads", type=int, help="Максимальное количество одновременно работающих профилей. Default: 5")
    parser.add_argument("-e", "--extension", type=str, help="Выбор используемого расширения. Допустимые значения: metamask, phantom")
    parser.add_argument("--metamaskId", type=str, help="ID расширения metamask chrome-extension://{metamaskId}/home.html. Default: fbkaeljfgkiknokhhdiomplofllnoele")
    parser.add_argument("--phantomId", type=str, help="ID расширения phantom chrome-extension://{phantomId}/popup.html. Default: bfnaelmomeimhlpmgjnjophhpkkoljpa")

    args = parser.parse_args().__dict__
    args = {key: value for key, value in args.items() if value is not None}
    return LaunchArgs(**args)