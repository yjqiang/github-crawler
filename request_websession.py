import time
import sys
from typing import Any

import requests


class WebSession:

    def __init__(self):
        self.__session = requests.Session()

    @staticmethod
    def _recv_json(rsp: requests.Response) -> Any:
        return rsp.json()

    @staticmethod
    def _recv_str(rsp: requests.Response) -> str:
        return rsp.text

    @staticmethod
    def _recv_bytes(rsp: requests.Response) -> bytes:
        return rsp.content

    def _orig_req(self, parse_rsp, method, url, **kwargs):
        i = 0
        while True:
            i += 1
            if i >= 10:
                print(f'反复请求多次未成功, {url}, {kwargs}')
                time.sleep(1)

            try:
                with self.__session.request(method, url, **kwargs) as rsp:
                    print(rsp.headers)
                    if rsp.status_code == 200:
                        body = parse_rsp(rsp)
                        if body:  # 有时候是 None 或空，直接屏蔽。read 或 text 类似，禁止返回空的东西
                            return body
                    print(f'STATUS_CODE ERROR: {rsp.status_code} {rsp.text}')
            except requests.exceptions.RequestException as e:
                print(e)
            except Exception:
                # print('当前网络不好，正在重试，请反馈开发者!!!!')
                print(sys.exc_info()[0], sys.exc_info()[1], url)

    def request_json(self, method, url, **kwargs) -> Any:
        return self._orig_req(self._recv_json, method, url, **kwargs)

    def request_binary(self, method, url, **kwargs) -> bytes:
        return self._orig_req(self._recv_bytes, method, url, **kwargs)

    def request_text(self, method, url, **kwargs) -> str:
        return self._orig_req(self._recv_str, method, url, **kwargs)
