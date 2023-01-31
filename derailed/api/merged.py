"""
MIT License

Copyright (c) 2022-2023 Derailed

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from functools import cached_property
import json
from typing import Any
from aiohttp import BasicAuth, ClientSession

from ..errors import HTTPException


class MergedHTTP():
    """
    Superset of Derailed's separated API implementations into one.
    """
    def __init__(
        self,
        token: str,
        proxy_url: str | None = None,
        proxy_auth: BasicAuth | None = None
    ) -> None:
        self.__token = token
        self.__proxy_url = proxy_url
        self.__proxy_auth = proxy_auth
        self.__session: ClientSession | None = None
        self.__base_url: str = 'https://derailed.one/api'

    @cached_property
    def __headers(self) -> dict[str, Any]:
        if self.__token is None:
            return {}
        else:
            return {'Authorization': self.__token}

    async def __prop_session(self) -> None:
        if self.__session is None:
            self.__session = ClientSession()


    async def request(self, route: str, method: str, data: dict[str, Any] | None = None) -> dict[str, Any] | None:
        await self.__prop_session()

        if data is not None:
            data = json.dumps(data)

        r = await self.__session.request(
            method,
            f'{self.__base_url}{route}',
            data=data,
            proxy_url=self.__proxy_url,
            proxy_auth=self.__proxy_auth,
            headers=self.__headers
        )

        if not r.ok:
            raise HTTPException(f'Error raised by Derailed (status: {r.status}): {await r.json()}')

        # Derailed does not return 200 codes else then these
        if r.status in (200, 201):
            return await r.json()
        elif r.status == 204:
            return None
