import asyncio

import playwright._impl._errors
from mnemonic import Mnemonic

from browser import AdspowerPlaywright
from schemas import Profile

mnemo = Mnemonic("english")


class WalletManager:
    METAMASK_EXTENSION_URI = "chrome-extension://fbkaeljfgkiknokhhdiomplofllnoele/home.html"
    POSSIBLE_SEED_PHRASES_COUNT = [12, 15, 18, 21, 24]

    def __init__(self, adspower_uri: str, adspower_api_key: str, profile: Profile):
        self.adspower_api_key = adspower_api_key
        self.adspower_uri = adspower_uri

        self.profile = profile

    async def __aenter__(self):
        self._pw = AdspowerPlaywright(self.adspower_uri, self.adspower_api_key, self.profile.id)
        self._browser = await self._pw.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pw.__aexit__(exc_type, exc_val, exc_tb)

    async def create_wallet(self):
        context = self._browser.contexts[0]
        page = await context.new_page()
        await asyncio.sleep(5)
        for page_to_close in context.pages:
            if page_to_close != page:
                await page_to_close.close()

        await page.goto(self.METAMASK_EXTENSION_URI, wait_until="domcontentloaded")

        try:
            await page.get_by_test_id("unlock-password").wait_for(timeout=5000, state="visible")
            raise Exception(f"{self.profile.profile} already signed in")
        except playwright._impl._errors.TimeoutError:
            pass


        await page.locator("div.dropdown select").select_option(value="en")

        await page.get_by_test_id("onboarding-terms-checkbox").click()
        await page.get_by_test_id("onboarding-import-wallet").click()

        await page.get_by_test_id("metametrics-no-thanks").click()

        seed_phrases_list = self.profile.seed.split()
        seed_phrases_count = len(seed_phrases_list)
        if seed_phrases_count not in self.POSSIBLE_SEED_PHRASES_COUNT:
            raise Exception(f"{self.profile} invalid seed phrases count {seed_phrases_count}")


        await page.locator("div.dropdown.import-srp__number-of-words-dropdown select").select_option(value=f"{seed_phrases_count}")

        for i, seed_phrase in enumerate(seed_phrases_list):
            await page.get_by_test_id(f"import-srp__srp-word-{i}").fill(seed_phrase)
        await page.get_by_test_id("import-srp-confirm").click()

        await page.get_by_test_id("create-password-new").fill(self.profile.password)
        await page.get_by_test_id("create-password-confirm").fill(self.profile.password)

        await page.get_by_test_id("create-password-terms").click()
        await page.get_by_test_id("create-password-import").click()
        await page.get_by_test_id("onboarding-complete-done").click()

        await page.get_by_test_id("pin-extension-next").click()
        await page.get_by_test_id("pin-extension-done").click()

        await asyncio.sleep(5)