import argparse
import asyncio
import io
import itertools
import os
from getpass import getpass

import aiohttp
import pandas as pd
from dotenv import load_dotenv

from crypt_manager import decrypt
from schemas import Profile, LaunchArgs
from wallet_manager import WalletManager

load_dotenv()

ADSPOWER_URI = os.getenv("ADSPOWER_URI")
ADSPOWER_API_KEY = os.getenv("ADSPOWER_API_KEY")


async def launch_profile(metamask_id: str, profile: Profile, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            async with WalletManager(ADSPOWER_URI, ADSPOWER_API_KEY, metamask_id, profile) as wallet_manager:
                await wallet_manager.create_wallet()
                await asyncio.sleep(5)
        except Exception as e:
            print(e)

def get_launch_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--profiles", type=str, help="Путь к csv файлу с аккаунтами. Default: profiles.csv", default="profiles.csv")
    parser.add_argument("-r", "--rounds", type=int, help="Количество кругов. Default: 1", default=1)
    parser.add_argument("-t", "--threads", type=int, help="Максимальное количество одновременно работающих профилей. Default: 5", default=5)
    parser.add_argument("-m", "--metamaskId", type=str, help="ID расширения metamask chrome-extension://{metamaskId}/home.html. Default: fbkaeljfgkiknokhhdiomplofllnoele", default="fbkaeljfgkiknokhhdiomplofllnoele")

    args = parser.parse_args()

    return LaunchArgs(profiles_path=args.profiles, rounds_count=args.rounds, threads_count=args.threads, metamask_id=args.metamaskId)

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
    for profile in profiles:
        result[profile["name"]] = profile["user_id"]
    return result


async def main():
    launch_args = get_launch_args()

    if not os.path.exists(launch_args.profiles_path) or not os.path.isfile(launch_args.profiles_path):
        raise Exception("Couldn't find input file ", launch_args.profiles_path)

    file_ext = os.path.splitext(launch_args.profiles_path)[-1]

    if file_ext == ".bin":
        encryption_key = getpass("Enter encryption key:")
        decrypted_file_contents = decrypt(encryption_key, launch_args.profiles_path)
        userdata_df = pd.read_csv(io.BytesIO(decrypted_file_contents))
    else:
        userdata_df = pd.read_csv(launch_args.profiles_path)

    profile_ids_map = await map_profile_name_to_id()

    profiles = []

    for _, row in userdata_df.iterrows():
        profile_name = row.get("profile")

        if profile_name is None:
            raise Exception("Invalid profile", row)

        profile_name = str(profile_name)
        profile_id = profile_ids_map.get(profile_name)

        if profile_id is None:
            raise Exception("Profile not found ", row)

        profiles.append(Profile(profile=profile_name, id=profile_id, seed = row.get("seed"), password=row.get("password")))

    semaphore = asyncio.Semaphore(launch_args.threads_count)
    for _ in range(launch_args.rounds_count):
        tasks = []
        for profile in profiles:
            tasks.append(asyncio.create_task(launch_profile(launch_args.metamask_id, profile, semaphore)))

        for task in tasks:
            await task

if __name__ == "__main__":
    asyncio.run(main())