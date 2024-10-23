import aio_pika
import asyncpg
import redis
import json
from datetime import datetime, timezone
from dotenv import dotenv_values
import logging
import asyncio

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
envs = dotenv_values(".env")
RABBITMQ_HOST = envs.get("RABBITMQ_HOST", "localhost")
PG_DSN = envs["POSTGRES_DSN"]
REDIS_HOST = envs.get("REDIS_HOST", "localhost")
REDIS_PORT = int(envs.get("REDIS_PORT", 6379))

# Initialize Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

async def update_redis(station_id, timestamp):
    """Update Redis with the latest timestamp."""
    redis_key = f"station:{station_id}"
    await redis_client.hset(redis_key, mapping={
        "last_updated": timestamp.isoformat(),
        "last_checked": datetime.now(timezone.utc).isoformat()
    })
    logger.info(f"Updated Redis for station {station_id}")

def parse_station_data(station_data):
    """Parse station data and ensure it has the correct date_time field."""
    try:
        # Extraer el campo 'fecha' del station_data
        timestamp_str = station_data.get("fecha", "")
        now = datetime.now()

        # Parsear el timestamp, agregando el año actual
        parsed_date = datetime.strptime(f"{now.year}-{timestamp_str}", "%Y-%d-%m %H:%M")

        # Manejar fechas futuras reemplazando por el año anterior si es necesario
        if parsed_date > now:
            parsed_date = parsed_date.replace(year=now.year - 1)

        # Asegurar que el timestamp sea timezone-aware
        date_time = parsed_date.replace(tzinfo=timezone.utc)

        # Extraer lecturas y convertirlas a float
        readings = station_data.get("lecturas", {})
        temperature = float(readings.get("temperatura", 0.0))
        radiation = float(readings.get("radiacion", 0.0))
        relative_humidity = float(readings.get("humedad_relativa", 0.0))
        precipitation = float(readings.get("precipitacion", 0.0))
        wind_speed = float(readings.get("velocidad_viento", 0.0))
        wetness = float(readings.get("mojadura", 0.0))
        wind_direction = float(readings.get("direccion_viento", 0.0))
        heat_index = float(readings.get("indice_calor", 0.0))

        # Preparar los datos para la inserción en la base de datos
        parsed_data = (
            station_data["station_id"],
            date_time,  # Ahora timezone-aware
            temperature,
            radiation,
            relative_humidity,
            precipitation,
            wind_speed,
            wetness,
            wind_direction,
            heat_index
        )

        logger.info(f"Parsed data: {parsed_data}")
        return parsed_data

    except Exception as e:
        logger.error(f"Error parsing station data: {e}")
        raise


async def insert_station_data(parsed_station_data):
    """Insert the station data into PostgreSQL asynchronously."""
    try:
        conn = await asyncpg.connect(PG_DSN)

        # Insert the parsed data into the database
        await conn.execute(
            """
            INSERT INTO StationRegisters (
                station_id, date_time, temperature, radiation, 
                relative_humidity, precipitation, wind_speed, wetness, 
                wind_direction, heat_index
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10
            )
            """,
            *parsed_station_data  # Unpack the parsed data tuple
        )

        await conn.close()
        logger.info(f"Inserted data for station {parsed_station_data[0]}")

    except Exception as e:
        logger.error(f"Failed to insert station data: {e}")

async def on_message(message):
    """Callback function for processing received messages."""
    try:
        # Acknowledge the RabbitMQ message
        await message.ack()
        station_data = message.body.decode()
        station_data = json.loads(station_data)

        logger.info(f"Received data: {station_data}")

        # Parse and validate the station data
        parsed_data = parse_station_data(station_data)

        # Insert the parsed data into PostgreSQL
        await insert_station_data(parsed_data)

    except Exception as e:
        logger.error(f"Failed to process message: {e}")


async def main():
    """Main function to set up RabbitMQ consumer."""
    connection = await aio_pika.connect_robust(
        f"amqp://{RABBITMQ_HOST}/", loop=asyncio.get_event_loop()
    )

    channel = await connection.channel()

    # Declare the queue (creates it if it doesn't exist)
    queue = await channel.declare_queue("station_updates", durable=True)

    logger.info("Waiting for messages. To exit, press CTRL+C")

    # Start listening to the queue
    await queue.consume(on_message)

    # Keep the event loop running
    await asyncio.Future()  # Keeps the script running

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer stopped.")
