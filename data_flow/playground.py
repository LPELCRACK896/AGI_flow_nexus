import redis
from config.config import connections
from flows.nax import Nax  # Asumiendo que tienes una clase Nax bien estructurada en el módulo flows.nax

# Punto de entrada principal para la ejecución del flujo de autenticación
if __name__ == "__main__":
    try:
        r = redis.Redis(host=connections.REDIS_HOST, port=connections.REDIS_PORT, db=0)
        print("Redis connection successful.")
    except redis.ConnectionError as e:
        print(f"Error connecting to Redis: {e}")
        exit(1)  # Si no se puede conectar a Redis, detener la ejecución

    nax = Nax(r)
    
    token = nax.authentication()  
    