import redis
import projects.nax_etl.config.config as config
from components.prefect.flows.NaxFlows import NaxFlows

redis_connection = config.redis

r = redis.Redis(
    host=redis_connection.REDIS_HOST,
    port=redis_connection.REDIS_PORT,
    db=0,
    password=redis_connection.REDIS_PASSWORD
)

nax = NaxFlows(r)

token = nax.authentication()
nax.update_areas(token)