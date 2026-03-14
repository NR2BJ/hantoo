import logging
from datetime import datetime, timedelta, timezone

import httpx

from app.models.kis_account import KISAccount
from app.services.settings_service import app_settings
from app.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


def _get_base_url(environment: str) -> str:
    if environment == "paper":
        return app_settings.get("kis_paper_base_url")
    return app_settings.get("kis_prod_base_url")


async def get_valid_token(account: KISAccount, db) -> str:
    """Get a valid KIS OAuth token for the account, refreshing if needed."""
    now = datetime.now(timezone.utc)

    # Use cached token if still valid (>5 min remaining)
    if account.access_token and account.token_expires_at:
        if account.token_expires_at > now + timedelta(minutes=5):
            return account.access_token

    # Fetch new token
    base_url = _get_base_url(account.environment)
    app_key = decrypt_value(account.app_key_enc)
    app_secret = decrypt_value(account.app_secret_enc)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()

    token = data["access_token"]
    # KIS tokens are valid for ~24 hours
    expires_at = now + timedelta(hours=23, minutes=50)

    account.access_token = token
    account.token_expires_at = expires_at
    await db.commit()

    logger.info("Refreshed KIS token for account %s", account.label)
    return token
