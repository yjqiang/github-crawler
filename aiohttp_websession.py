import sys
import asyncio
from typing import Any, Optional

import aiohttp

sem = asyncio.Semaphore(3)


class WebSession:
    __slots__ = ('session',)

    def __init__(self):
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    @staticmethod
    async def _recv_json(rsp: aiohttp.ClientResponse):
        return await rsp.json(content_type=None)

    @staticmethod
    async def _recv_str(rsp: aiohttp.ClientResponse):
        return await rsp.text()

    @staticmethod
    async def _recv_bytes(rsp: aiohttp.ClientResponse):
        return await rsp.read()

    @staticmethod
    async def _recv(rsp: aiohttp.ClientResponse):
        return rsp

    # 基本就是通用的 request
    async def _orig_req(self, parse_rsp, method: str, url: str, keep_try: bool = True, **kwargs):
        i = 0
        while keep_try or i == 0:
            i += 1
            if i >= 10:
                print(f'反复请求多次未成功, {url}, {kwargs}')
                await asyncio.sleep(1)
            try:
                async with self.session.request(method, url, **kwargs) as rsp:
                    print(url, rsp.headers.getone('X-RateLimit-Remaining', None), kwargs)
                    if rsp.status == 200:
                        return await parse_rsp(rsp)
                    elif rsp.status == 404:
                        return None
                    elif rsp.status == 403:  # 一般是 rating limit
                        return None
                    else:
                        print(f'STATUS_CODE ERROR: {url} {rsp.status} {rsp.text} {kwargs}')
                        sys.exit(-1)
            except:
                # print('当前网络不好，正在重试，请反馈开发者!!!!')
                print(sys.exc_info()[0], sys.exc_info()[1], url)

    async def request_json(self,
                           method: str,
                           url: str,
                           keep_try: bool = True,
                           **kwargs) -> Optional[Any]:
        return await self._orig_req(self._recv_json, method, url, keep_try, **kwargs)

    async def request_binary(self,
                             method: str,
                             url: str,
                             keep_try: bool = True,
                             **kwargs) -> Optional[bytes]:
        return await self._orig_req(self._recv_bytes, method, url, keep_try, **kwargs)

    async def request_text(self,
                           method: str,
                           url: str,
                           keep_try: bool = True,
                           **kwargs) -> Optional[str]:
        return await self._orig_req(self._recv_str, method, url, keep_try, **kwargs)
