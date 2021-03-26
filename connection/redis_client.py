import aioredis
from aioredlock import Aioredlock
from dynaconf import settings


class Redis:
    def __init__(self, uri=None):
        self.conn: aioredis.Redis = None
        self.lock_manager: Aioredlock = None
        self.uri = uri

    async def init(self, uri=None):
        if uri is not None:
            self.uri = uri
        self.conn = await aioredis.create_redis_pool(self.uri, minsize=2)
        self.lock_manager = Aioredlock([self.conn], retry_count=10000)

    async def set(self, key, val, expire=None):
        if expire is None:
            _expire = settings.get("REDIS_CACHE_TIME", "600")
            expire = int(_expire)

        # Exclusive mode of aioredis

        with await self.conn as conn:
            await conn.set(key, val)
            if expire is not None:
                await conn.expire(key, expire)

    async def get(self, key):
        # Exclusive mode of aioredis
        return await self.conn.get(key)

    async def lock(self, key):
        return await self.lock_manager.lock(key)

    async def ping(self):
        return self.conn.ping()

    async def unlock(self, lock):
        return await self.lock_manager.unlock(lock)
