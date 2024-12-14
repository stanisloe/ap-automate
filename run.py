import asyncio
import os
from dotenv import load_dotenv
import argparse

import pandas as pd

from wallet_manager import WalletManager
from open_profiles import map_profile_name_to_id
from schemas import Profile

load_dotenv()

ADSPOWER_URI = os.getenv("ADSPOWER_URI")
ADSPOWER_API_KEY = os.getenv("ADSPOWER_API_KEY")


async def launch(profile: Profile, semaphore: asyncio.Semaphore):
    async with semaphore:
        async with WalletManager(ADSPOWER_URI, ADSPOWER_API_KEY, profile) as wallet_manager:
            await wallet_manager.create_wallet()
            await asyncio.sleep(5)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", type=str, help="Путь к csv файлу с аккаунтами")
    parser.add_argument("--rounds", type=int, help="Количество кругов")
    parser.add_argument("--threads", type=int, help="Максимальное количество одновременно работающих профилей")

    args = parser.parse_args()

    profiles_path = "profiles.csv"
    if args.profiles is not None:
        profiles_path = args.profiles

    rounds = 1
    if args.rounds is not None:
        rounds = args.rounds

    threads = 3
    if args.threads is not None:
        threads = args.threads
    semaphore = asyncio.Semaphore(threads)

    if not os.path.exists(profiles_path) or not os.path.isfile(profiles_path):
        raise Exception("Couldn't find input file ", profiles_path)

    userdata_df = pd.read_csv(profiles_path)

    profile_ids_map = map_profile_name_to_id()
    profiles = []
    for _, row in userdata_df.iterrows():
        profile_name = row.get("profile")
        if profile_name is None:
            raise Exception("Invalid profile", row)
        profile_name = str(profile_name)
        profile_id = profile_ids_map.get(profile_name)
        if profile_id is None:
            raise Exception("Profile number not found")
        profiles.append(Profile(profile=profile_name, id=profile_id, seed = row.get("seed"), password=row.get("password")))

    for _ in range(rounds):
        tasks = []
        for profile in profiles:
            tasks.append(asyncio.create_task(launch(profile, semaphore)))

        for task in tasks:
            try:
                await task
            except Exception as e:
                print(e)

if __name__ == "__main__":
    asyncio.run(main())