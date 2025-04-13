import redis.asyncio as redis
from src import config

redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=0,
    decode_responses=True,
)


def save_token_to_redis(token_type: str, id: int, token: str):
    """
    Save Token in Redis
    """
    redis_client.set(f"{token_type}:{id}", token)


def get_token_from_redis(token_type: str, id: int):
    """
    Get Token from Redis
    """
    return redis_client.get(f"{token_type}:{id}")


# TODO Refresh accessToken
