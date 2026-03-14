import asyncio
import time
import uuid

from app.services.redis_client import get_redis

MAX_REQUESTS_PER_SECOND = 20


class KISRateLimiter:
    async def acquire(self, account_id: uuid.UUID) -> None:
        """Block until a request slot is available (sliding window, 20 req/s)."""
        r = get_redis()
        key = f"kis:ratelimit:{account_id}"
        now = time.time()

        while True:
            pipe = r.pipeline()
            pipe.zremrangebyscore(key, 0, now - 1.0)
            pipe.zcard(key)
            results = await pipe.execute()
            count = results[1]

            if count < MAX_REQUESTS_PER_SECOND:
                await r.zadd(key, {f"{now}:{id(asyncio.current_task())}": now})
                await r.expire(key, 2)
                return

            # Wait for the oldest entry to expire
            oldest = await r.zrange(key, 0, 0, withscores=True)
            if oldest:
                wait_time = 1.0 - (now - oldest[0][1])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0.05)


kis_rate_limiter = KISRateLimiter()
