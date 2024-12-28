import asyncio

import playwright._impl._errors

from browser import AdspowerPlaywright
from schemas import Profile


class PhantomWalletManager:
    POSSIBLE_SEED_PHRASES_COUNT = [12, 24]

    def __init__(self, adspower_uri: str, adspower_api_key: str, extension_id: str, profile: Profile):
        self.adspower_api_key = adspower_api_key
        self.adspower_uri = adspower_uri
        self.profile = profile
        self.extension_uri = f"chrome-extension://{extension_id}"
        self.popup_uri = f"{self.extension_uri}/popup.html"
        self.onboarding_uri = f"{self.extension_uri}/onboarding.html"

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
        await self._page.goto(self.popup_uri, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        self._page = self._context.pages[0]
        try:
            await self._page.wait_for_url(self.onboarding_uri, timeout=2)
            return False
        except playwright._impl._errors.TimeoutError:
            return True


    async def create_wallet(self):
        await self._open_new_page_close_others()
        if await self._is_signed_in():
            raise Exception(f"{self.profile.profile} already signed in")
        await self._page.get_by_text("I already have a wallet").first.click(timeout=10000)

        await self._page.get_by_text("Import Secret Recovery Phrase").first.click(timeout=10000)

        seed_phrases_list = self.profile.seed.split()
        seed_phrases_count = len(seed_phrases_list)
        if seed_phrases_count not in self.POSSIBLE_SEED_PHRASES_COUNT:
            raise Exception(f"{self.profile.profile} invalid seed phrases count {seed_phrases_count}")

        if seed_phrases_count == 24:
            await self._page.get_by_text("I have a 24-word recovery phrase").first.click(timeout=10000)

        for i, seed_phrase in enumerate(seed_phrases_list):
            await self._page.get_by_test_id(f"secret-recovery-phrase-word-input-{i}").fill(seed_phrase, timeout=10000)
        await self._page.get_by_test_id("onboarding-form-submit-button").click(timeout=10000)

        await self._page.get_by_text("Continue").click(timeout=10000)

        await self._page.get_by_test_id("onboarding-form-password-input").fill(self.profile.password, timeout=10000)
        await self._page.get_by_test_id("onboarding-form-confirm-password-input").fill(self.profile.password, timeout=10000)

        await self._page.get_by_test_id("onboarding-form-terms-of-service-checkbox").click(timeout=10000)

        await self._page.get_by_text("Continue").click(timeout=10000)

        await self._page.get_by_text("Get Started").wait_for(timeout=10000)

        await self._page.goto(self.popup_uri, wait_until="domcontentloaded")
        await self._page.get_by_text("Solana").wait_for(timeout=10000)

# async def main():
#     profile = Profile(id="krn58kj", profile="a", password="12345678", seed="leopard chicken fluid fiscal aerobic noise report couple juice private kite code")
#     async with WalletManager("http://local.adspower.net:50360", "0ce5ceb619279473bca8ff141ae5c5fb",
#                              "bfnaelmomeimhlpmgjnjophhpkkoljpa", profile) as manager:
#         try:
#             await manager.create_wallet()
#         except:
#             traceback.print_exc()
# asyncio.run(main())