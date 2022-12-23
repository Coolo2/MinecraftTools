from __future__ import annotations
import typing

import aiohttp


if typing.TYPE_CHECKING:
    from client import Client

class HTTP():
    def __init__(self, client : Client):
        self.client = client
    
    async def get_redirect(self, url : str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                return r.url

    async def fetch_json(self, method : str, url : str, data : dict = None, headers : dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers) as r:
                return await r.json()
    
    async def fetch_text(self, method : str, url : str, data : dict = None) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url) as r:
                return await r.text()