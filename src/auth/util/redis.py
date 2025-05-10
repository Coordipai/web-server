import redis.asyncio as redis

from src.config import config

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    password=config.REDIS_PASSWORD,
    decode_responses=True,
)


async def save_token_to_redis(token_type: str, id: int, token: str):
    """
    Save Token in Redis
    """
    await redis_client.set(f"{token_type}:{id}", token)


async def get_token_from_redis(token_type: str, id: int):
    """
    Get Token from Redis
    """
    return await redis_client.get(f"{token_type}:{id}")


async def delete_token_from_redis(token: str):
    """
    Delete Token from Redis
    """
    return await redis_client.delete(token)
