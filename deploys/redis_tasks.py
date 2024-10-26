from redis.exceptions import RedisError
from deploys.config import settings
from prefect import task
import datetime
from typing import Optional
import redis

@task(tags=["setup"])
def get_redis_connection() -> redis.Redis:
    try:
        redis_connection = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        redis_connection.ping()
        return redis_connection
    except RedisError as e:
        raise RuntimeError(f"Failed to connect to Redis: {str(e)}")


@task
def set_nax_token(connection: redis.Redis, token: str):
    """Actualiza el token NAX en Redis"""
    try:
        connection.set('nax_token', token)
    except RedisError as e:
        raise RuntimeError(f"Failed to update nax_token in Redis: {str(e)}")


@task
def get_nax_token(connection: redis.Redis) -> Optional[str]:
    try:
        value = connection.get('nax_token')

        if value is None:
            raise KeyError("nax_token not found in Redis")

        return value.decode('utf-8')

    except KeyError as ke:
        return None

    except RedisError as re:
        raise RuntimeError(f"RedisError: Failed to get nax_token from Redis: {str(re)}") from re

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e