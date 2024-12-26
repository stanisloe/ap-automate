import asyncio

import playwright._impl._errors

from browser import AdspowerPlaywright
from schemas import Profile


class MetamaskWalletManager:
    POSSIBLE_SEED_PHRASES_COUNT = [12, 15, 18, 21, 24]

    def __init__(self, adspower_uri: str, adspower_api_key: str, metamask_id: str, profile: Profile):
        self.adspower_api_key = adspower_api_key
        self.adspower_uri = adspower_uri
        self.profile = profile
        self.metamask_extension_uri = f"chrome-extension://{metamask_id}/home.html"

    async def __aenter__(self):
        self._pw = AdspowerPlaywright(self.adspower_uri, self.adspower_api_key, self.profile.id)
        self._browser = await self._pw.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pw.__aexit__(exc_type, exc_val, exc_tb)

    async def _open_new_page_close_others(self):
        self._context = self._browser.contexts[0]
        self._page = await self._context.new_page()
        await asyncio.sleep(5)
        for page_to_close in self._context.pages:
            if page_to_close != self._page:
                await page_to_close.close()

    async def _is_signed_in(self):
        try:
            await self._page.get_by_test_id("unlock-password").wait_for(timeout=5000, state="visible")
            return True
        except playwright._impl._errors.TimeoutError:
            return False

    async def create_wallet(self):
        await self._open_new_page_close_others()

        await self._page.goto(self.metamask_extension_uri, wait_until="domcontentloaded")

        if await self._is_signed_in():
            raise Exception(f"{self.profile.profile} already signed in")

        await self._page.locator("div.dropdown select").select_option(value="en")

        await self._page.get_by_test_id("onboarding-terms-checkbox").click()
        await self._page.get_by_test_id("onboarding-import-wallet").click()

        await self._page.get_by_test_id("metametrics-no-thanks").click()

        seed_phrases_list = self.profile.seed.split()
        seed_phrases_count = len(seed_phrases_list)
        if seed_phrases_count not in self.POSSIBLE_SEED_PHRASES_COUNT:
            raise Exception(f"{self.profile} invalid seed phrases count {seed_phrases_count}")

        await self._page.locator("div.dropdown.import-srp__number-of-words-dropdown select").select_option(value=f"{seed_phrases_count}")

        for i, seed_phrase in enumerate(seed_phrases_list):
            await self._page.get_by_test_id(f"import-srp__srp-word-{i}").fill(seed_phrase)
        await self._page.get_by_test_id("import-srp-confirm").click()

        await self._page.get_by_test_id("create-password-new").fill(self.profile.password)
        await self._page.get_by_test_id("create-password-confirm").fill(self.profile.password)

        await self._page.get_by_test_id("create-password-terms").click()
        await self._page.get_by_test_id("create-password-import").click()
        await self._page.get_by_test_id("onboarding-complete-done").click()

        await self._page.get_by_test_id("pin-extension-next").click()
        await self._page.get_by_test_id("pin-extension-done").click()

        await asyncio.sleep(5)