import json

from app.services.redis_client import get_redis


async def cache_get(key: str) -> dict | list | None:
    r = get_redis()
    data = await r.get(key)
    if data is None:
        return None
    return json.loads(data)


async def cache_set(key: str, data: dict | list, ttl_seconds: int) -> None:
    r = get_redis()
    await r.set(key, json.dumps(data, ensure_ascii=False), ex=ttl_seconds)


async def cache_delete(key: str) -> None:
    r = get_redis()
    await r.delete(key)
