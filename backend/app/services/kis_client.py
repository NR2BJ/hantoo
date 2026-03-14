import logging

import httpx

from app.models.kis_account import KISAccount
from app.services.kis_token_service import _get_base_url, get_valid_token
from app.services.rate_limiter import kis_rate_limiter
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


class KISApiError(Exception):
    def __init__(self, rt_cd: str, msg_cd: str, msg: str):
        self.rt_cd = rt_cd
        self.msg_cd = msg_cd
        self.msg = msg
        super().__init__(f"KIS API error [{msg_cd}]: {msg}")


class KISClient:
    def __init__(self):
        self._http: httpx.AsyncClient | None = None

    @property
    def http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=15.0)
        return self._http

    async def request(
        self,
        account: KISAccount,
        method: str,
        path: str,
        tr_id: str,
        params: dict | None = None,
        body: dict | None = None,
        *,
        db,
    ) -> dict:
        """Make an authenticated request to the KIS API."""
        await kis_rate_limiter.acquire(account.id)

        token = await get_valid_token(account, db)
        app_key = decrypt_value(account.app_key_enc)
        app_secret = decrypt_value(account.app_secret_enc)
        base_url = _get_base_url(account.environment)

        headers = {
            "authorization": f"Bearer {token}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": tr_id,
            "custtype": "P",
            "Content-Type": "application/json; charset=utf-8",
        }

        url = f"{base_url}{path}"
        resp = await self.http.request(
            method, url, headers=headers, params=params, json=body
        )
        resp.raise_for_status()
        data = resp.json()

        # KIS returns rt_cd for error checking
        rt_cd = data.get("rt_cd", "0")
        if rt_cd != "0":
            raise KISApiError(
                rt_cd=rt_cd,
                msg_cd=data.get("msg_cd", ""),
                msg=data.get("msg1", "Unknown error"),
            )

        return data

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()


kis_client = KISClient()
