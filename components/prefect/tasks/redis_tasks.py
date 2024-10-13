from components.prefect.models.Area import Area
import projects.nax_etl.config.config as config
from redis.exceptions import RedisError
from prefect import task
import datetime
import redis

rds_conn = config.redis

@task
def get_redis_connection() -> redis.Redis:
    """Crea una conexión a Redis y la devuelve"""
    try:
        conn = redis.Redis(host=rds_conn.REDIS_HOST, port=rds_conn.REDIS_PORT, db=0)
        conn.ping()
        return conn
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


@task(tags=["load"])
def set_area(connection: redis.Redis, area: Area):
    """Guarda una nueva área en Redis usando un hash, recibiendo el modelo Area."""
    key = f"area:{area.id}"
    data = area.model_dump(exclude_unset=True)
    units_data = data.pop('units')
    data.update(units_data)
    connection.hset(key, mapping=data)
    print(f"Área {area.name} con id {area.id} guardada exitosamente.")
    return True


@task
def get_area(connection: redis.Redis, id: int):
    """Recupera la información de un área específica por su ID."""
    key = f"area:{id}"

    if not connection.exists(key):
        print(f"Área con id {id} no encontrada.")
        return None

    area_data = connection.hgetall(key)
    area_data_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in area_data.items()}

    return area_data_decoded


@task
async def get_all_areas(connection: redis.Redis):
    """Obtiene todas las áreas almacenadas en Redis."""
    # Usamos un patrón para buscar todas las claves que comienzan con "area:"
    keys = await connection.keys('area:*')

    if not keys:
        return "No hay áreas almacenadas."

    all_areas = {}
    for key in keys:
        area_id = key.decode('utf-8').split(":")[1]
        area_data = connection.hgetall(key)

        area_data_decoded = {k.decode('utf-8'): v.decode('utf-8') for k, v in area_data.items()}
        all_areas[area_id] = area_data_decoded

    return all_areas


@task
def set_area_last_updated(connection: redis.Redis, id: int, last_update: datetime.datetime):
    """Actualiza el campo last_updated de un área específica en Redis."""
    key = f"area:{id}"

    if not connection.exists(key):
        return f"Área con id {id} no encontrada."

    connection.hset(key, "last_updated", last_update.strftime('%Y-%m-%d %H:%M:%S'))

    return f"Área con id {id} actualizada. Campo last_updated: {last_update}"