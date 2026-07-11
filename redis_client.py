import logging
from redis.asyncio import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.client = None
        self._connected = False

    async def connect(self):
        if not self._connected:
            try:
                # 使用独立配置，直接构造 Redis 对象，指定 protocol=2 兼容旧版 Redis
                self.client = Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True,
                    protocol=2  # 强制使用 RESP2 协议
                )
                await self.client.ping()
                self._connected = True
                logger.info("✅ Redis 连接成功")
            except Exception as e:
                self._connected = False
                logger.warning(f"⚠️ Redis 连接失败，将进入降级模式: {e}")

    async def get(self, key: str):
        if not self._connected:
            logger.warning(f"⚠️ Redis 降级: get({key}) 失败，返回 None")
            return None
        try:
            return await self.client.get(key)
        except Exception as e:
            logger.warning(f"⚠️ Redis 降级: get({key}) 异常，返回 None: {e}")
            return None

    async def setex(self, key: str, time: int, value: str):
        if not self._connected:
            logger.warning(f"⚠️ Redis 降级: setex({key}) 未执行")
            return
        try:
            await self.client.setex(key, time, value)
        except Exception as e:
            logger.warning(f"⚠️ Redis 降级: setex({key}) 失败: {e}")

    async def delete(self, key: str):
        if not self._connected:
            logger.warning(f"⚠️ Redis 降级: delete({key}) 未执行")
            return
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"⚠️ Redis 降级: delete({key}) 失败: {e}")

redis_client = RedisClient()