from prefect import task
from config.config import connections
import redis
from redis.exceptions import RedisError

# Task para obtener la conexión a Redis
@task
def get_redis_connection() -> redis.Redis:
    """Crea una conexión a Redis y la devuelve"""
    try:
        conn = redis.Redis(host=connections.REDIS_HOST, port=connections.REDIS_PORT, db=0)
        conn.ping() 
        return conn
    except RedisError as e:
        raise RuntimeError(f"Failed to connect to Redis: {str(e)}")


@task
def update_nax_token(connection: redis.Redis, token: str):
    """Actualiza el token NAX en Redis"""
    try:
        connection.set('nax_token', token)
    except RedisError as e:
        raise RuntimeError(f"Failed to update nax_token in Redis: {str(e)}")


@task
def get_nax_token(connection: redis.Redis) -> str:
    """Obtiene el token NAX almacenado en Redis"""
    try:
        value = connection.get('nax_token')

        # Agregar una verificación para debug: Verificar si el valor es None
        if value is None:
            raise KeyError("nax_token not found in Redis")
        
        # Decodificar el valor almacenado en bytes a string
        return value.decode('utf-8')

    except KeyError as ke:
        return None
    
    except RedisError as re:
        # Manejo específico del error RedisError
        raise RuntimeError(f"RedisError: Failed to get nax_token from Redis: {str(re)}") from re
    
    except Exception as e:
        # Manejo general de errores no esperados
        raise RuntimeError(f"An unexpected error occurred: {str(e)}") from e