"""Application settings service.

Manages all app configuration in the DB. On first startup, auto-generates
security keys and marks the app as needing setup (admin account creation).

Settings are cached in memory and refreshed when updated via the API.
"""

import secrets
from typing import Any

from cryptography.fernet import Fernet
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import AppSetting

# Default settings with their initial values and metadata
DEFAULT_SETTINGS: list[dict[str, Any]] = [
    # -- General --
    {
        "key": "setup_completed",
        "value": "false",
        "is_secret": False,
        "category": "general",
        "description": "초기 셋업 완료 여부",
    },
    {
        "key": "app_name",
        "value": "Hantoo",
        "is_secret": False,
        "category": "general",
        "description": "앱 이름 (로그인 화면 등에 표시)",
    },
    # -- Security (auto-generated) --
    {
        "key": "jwt_secret",
        "value": "__auto__",
        "is_secret": True,
        "category": "security",
        "description": "JWT 토큰 서명 키 (자동 생성)",
    },
    {
        "key": "jwt_expire_minutes",
        "value": "1440",
        "is_secret": False,
        "category": "security",
        "description": "JWT 토큰 만료 시간 (분)",
    },
    {
        "key": "encryption_key",
        "value": "__auto__",
        "is_secret": True,
        "category": "security",
        "description": "KIS 자격증명 암호화 키 (자동 생성)",
    },
    {
        "key": "require_2fa",
        "value": "false",
        "is_secret": False,
        "category": "security",
        "description": "모든 유저에게 2FA 필수 여부",
    },
    {
        "key": "allowed_ips",
        "value": "",
        "is_secret": False,
        "category": "security",
        "description": "허용된 IP 목록 (쉼표 구분, 비워두면 전체 허용)",
    },
    # -- KIS API --
    {
        "key": "kis_prod_base_url",
        "value": "https://openapi.koreainvestment.com:9443",
        "is_secret": False,
        "category": "kis",
        "description": "KIS 실전투자 API URL",
    },
    {
        "key": "kis_paper_base_url",
        "value": "https://openapivts.koreainvestment.com:29443",
        "is_secret": False,
        "category": "kis",
        "description": "KIS 모의투자 API URL",
    },
    {
        "key": "kis_ws_url",
        "value": "ws://ops.koreainvestment.com:21000",
        "is_secret": False,
        "category": "kis",
        "description": "KIS WebSocket URL",
    },
    # -- LLM --
    {
        "key": "anthropic_api_key",
        "value": "",
        "is_secret": True,
        "category": "llm",
        "description": "Anthropic (Claude) API 키",
    },
    {
        "key": "openai_api_key",
        "value": "",
        "is_secret": True,
        "category": "llm",
        "description": "OpenAI API 키",
    },
    {
        "key": "default_llm_provider",
        "value": "claude",
        "is_secret": False,
        "category": "llm",
        "description": "기본 LLM 프로바이더 (claude / openai)",
    },
]


class SettingsService:
    """In-memory cached settings backed by PostgreSQL."""

    def __init__(self):
        self._cache: dict[str, str] = {}
        self._secrets: set[str] = set()

    async def initialize(self, db: AsyncSession) -> None:
        """Called once at app startup. Seeds defaults and loads into cache."""
        await self._seed_defaults(db)
        await self._load_all(db)

    async def _seed_defaults(self, db: AsyncSession) -> None:
        """Insert default settings for any keys that don't exist yet."""
        result = await db.execute(select(AppSetting.key))
        existing_keys = {row[0] for row in result.all()}

        for setting_def in DEFAULT_SETTINGS:
            if setting_def["key"] in existing_keys:
                continue

            value = setting_def["value"]
            if value == "__auto__":
                value = self._generate_secret(setting_def["key"])

            db.add(
                AppSetting(
                    key=setting_def["key"],
                    value=value,
                    is_secret=setting_def["is_secret"],
                    category=setting_def["category"],
                    description=setting_def["description"],
                )
            )

        await db.commit()

    def _generate_secret(self, key: str) -> str:
        if key == "encryption_key":
            return Fernet.generate_key().decode()
        return secrets.token_hex(32)

    async def _load_all(self, db: AsyncSession) -> None:
        result = await db.execute(select(AppSetting))
        for setting in result.scalars().all():
            self._cache[setting.key] = setting.value
            if setting.is_secret:
                self._secrets.add(setting.key)

    def get(self, key: str, default: str = "") -> str:
        return self._cache.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        val = self._cache.get(key, "")
        if not val:
            return default
        return val.lower() in ("true", "1", "yes")

    def get_int(self, key: str, default: int = 0) -> int:
        val = self._cache.get(key, "")
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    async def set(self, key: str, value: str, db: AsyncSession) -> None:
        result = await db.execute(select(AppSetting).where(AppSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting:
            setting.value = value
        else:
            db.add(AppSetting(key=key, value=value))
        await db.commit()
        self._cache[key] = value

    async def get_all_for_ui(self, db: AsyncSession) -> list[dict]:
        """Return all settings for the admin UI. Mask secret values."""
        result = await db.execute(select(AppSetting).order_by(AppSetting.category, AppSetting.key))
        settings = []
        for s in result.scalars().all():
            settings.append(
                {
                    "key": s.key,
                    "value": "••••••••" if s.is_secret and s.value else s.value,
                    "is_secret": s.is_secret,
                    "category": s.category,
                    "description": s.description,
                    "has_value": bool(s.value),
                }
            )
        return settings

    @property
    def setup_completed(self) -> bool:
        return self.get_bool("setup_completed")


# Singleton
app_settings = SettingsService()
