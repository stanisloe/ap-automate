import asyncio

import aiohttp
from playwright import async_api


class AdspowerPlaywright:
    def __init__(self, uri: str, api_key: str, profile_id: str):
        self.uri = uri
        self.api_key = api_key
        self.profile_id = profile_id

    async def __aenter__(self):
        uri = await self._open_browser()
        self._pw = await async_api.async_playwright().start()
        return await self._pw.chromium.connect_over_cdp(uri)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # print("a")
        await self._close_browser()
        await self._pw.stop()



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
