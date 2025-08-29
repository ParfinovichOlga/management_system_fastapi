import aioredis
from config import config

token_blacklist = aioredis.StrictRedis(
    host=config.REDIS_HOST, port=config.REDIS_PORT, db=0
)


async def add_jti_to_blacklist(jti: str, ex: int) -> None:
    await token_blacklist.set(name=jti, value="", ex=ex * 60)


async def token_in_blacklist(jti: str) -> bool:
    jti = await token_blacklist.get(jti)
    return jti is not None
