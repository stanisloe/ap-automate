import aiohttp
import playwright.async_api


class AdspowerPlaywright:
    def __init__(self, uri: str, api_key: str, profile_id: str):
        self.uri = uri
        self.api_key = api_key
        self.profile_id = profile_id

    async def __aenter__(self):
        uri = await self._open_browser()
        self._playwright = playwright.async_api.async_playwright()
        self._pw = await self._playwright.__aenter__()
        return await self._pw.chromium.connect_over_cdp(uri)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._close_browser()
        await self._playwright.__aexit__(exc_type, exc_val, exc_tb)



    async def _open_browser(self):
        url = f"{self.uri}/api/v1/browser/start"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"user_id": self.profile_id}
        async with aiohttp.request("GET", url, params=params, headers=headers) as response:
                json_response = await response.json()
        if json_response["code"] != 0:
            raise Exception(json_response)

        return json_response["data"]["ws"]["puppeteer"]


    async def _close_browser(self):
        url = f"{self.uri}/api/v1/browser/stop"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"user_id": self.profile_id}
        async with aiohttp.request("GET", url, params=params, headers=headers) as response:
            json_response = await response.json()
        if json_response["code"] != 0:
            raise Exception(json_response)
