import asyncio
import io
import os
from getpass import getpass

import pandas as pd
from dotenv import load_dotenv

from cryptor import decrypt
from schemas import Profile, Extensions
from tools import map_profile_name_to_id, get_launch_args
from wallet_manager.metamask_wallet_manager import MetamaskWalletManager
from wallet_manager.phantom_wallet_manager import PhantomWalletManager

load_dotenv()

ADSPOWER_URI = os.getenv("ADSPOWER_URI")
ADSPOWER_API_KEY = os.getenv("ADSPOWER_API_KEY")


async def launch_profile(wallet_manager, extension_id: str, profile: Profile, semaphore: asyncio.Semaphore):
    async with semaphore:
        try:
            async with wallet_manager(ADSPOWER_URI, ADSPOWER_API_KEY, extension_id, profile) as wallet_manager:
                await wallet_manager.create_wallet()
            print(profile.profile, "success")
        except Exception as e:
            print(e)


async def main():
    launch_args = get_launch_args()

    if not os.path.exists(launch_args.file) or not os.path.isfile(launch_args.file):
        raise Exception("Couldn't find input file ", launch_args.file)

    file_ext = os.path.splitext(launch_args.file)[-1]

    if file_ext == ".bin":
        password = getpass("Enter password:")
        decrypted_file_contents = decrypt(password, launch_args.file)
        userdata_df = pd.read_csv(io.BytesIO(decrypted_file_contents))
    else:
        userdata_df = pd.read_csv(launch_args.file)

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

        profiles.append(
            Profile(profile=profile_name, id=profile_id, seed=row.get("seed"), password=row.get("password")))

    semaphore = asyncio.Semaphore(launch_args.threads)
    for _ in range(launch_args.rounds):
        if launch_args.extension == Extensions.metamask.value:
            wallet_manager = MetamaskWalletManager
        elif launch_args.extension == Extensions.phantom.value:
            wallet_manager = PhantomWalletManager
        else:
            raise Exception("Unsupported extension")
        extension_id = launch_args.ext_id

        tasks = []
        for profile in profiles:
            tasks.append(asyncio.create_task(launch_profile(wallet_manager, extension_id, profile, semaphore)))
            await asyncio.sleep(1)

        for task in tasks:
            await task


if __name__ == "__main__":
    asyncio.run(main())
