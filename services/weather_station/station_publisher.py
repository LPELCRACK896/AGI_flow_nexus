from datetime import datetime, timedelta, timezone
from utils.CustomLogger import CustomFormatter
from colorama import Fore, Style, init
from dotenv import dotenv_values
from bs4 import BeautifulSoup
import requests
import logging
import json
import time
import asyncpg
import redis
import pika
import asyncio

# Initialize colorama for colorful logging
init(autoreset=True)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = CustomFormatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

envs = dotenv_values(".env")
STATION_WEBSITE_URL = envs["STATION_WEBSITE_URL_1"]
LOGIN_ROUTE = envs["STATION_LOGIN_ROUTE"]
USER = envs["CREDENTIAL_STATIONS_USER"]
PASSWORD = envs["CREDENTIAL_STATIONS_PASS"]
PG_DSN = envs["POSTGRES_DSN"]
REDIS_HOST = envs.get("REDIS_HOST", "localhost")
REDIS_PORT = int(envs.get("REDIS_PORT", 6379))
RABBITMQ_HOST = envs.get("RABBITMQ_HOST", "localhost")

# Initialize Redis connection
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def send_to_rabbitmq(station_data):
    """Send data to RabbitMQ synchronously."""
    try:
        logger.info("Connecting to RabbitMQ...")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        channel = connection.channel()

        channel.queue_declare(queue="station_updates", durable=True)

        message = json.dumps(station_data)
        channel.basic_publish(
            exchange='',
            routing_key="station_updates",
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
        )
        logger.info(f"[RabbitMQ] Message sent for station {station_data['station_id']}.")
        connection.close()
    except Exception as e:
        logger.error(f"Failed to send message to RabbitMQ: {e}")

async def fetch_station_ids():
    """Fetch station IDs from the PostgreSQL database asynchronously."""
    try:
        conn = await asyncpg.connect(PG_DSN)
        rows = await conn.fetch("SELECT station_id FROM staticstations;")
        await conn.close()
        station_ids = [row['station_id'] for row in rows]
        logger.info(f"Retrieved station IDs: {station_ids}")
        return station_ids
    except Exception as e:
        logger.error(f"Failed to fetch station IDs: {e}")
        return []

async def check_and_update_redis(station_id, new_timestamp, station_data):
    """Check Redis asynchronously and send data to RabbitMQ if needed."""
    redis_key = f"station:{station_id}"
    station_data_redis = redis_client.hgetall(redis_key)

    # Inject the station_id into the station_data dictionary
    station_data["station_id"] = station_id

    if not station_data_redis:
        logger.info(f"No data found for station {station_id}. Creating entry.")
        redis_client.hset(redis_key, mapping={
            "last_updated": new_timestamp.isoformat(),
            "last_checked": datetime.now(timezone.utc).isoformat()
        })
        send_to_rabbitmq(station_data)  # Send to RabbitMQ
        return True

    last_updated = datetime.fromisoformat(station_data_redis.get("last_updated"))

    if new_timestamp > last_updated:
        logger.info(f"New data for station {station_id}. Sending to RabbitMQ.")
        redis_client.hset(redis_key, mapping={
            "last_updated": new_timestamp.isoformat(),
            "last_checked": datetime.now(timezone.utc).isoformat()
        })
        send_to_rabbitmq(station_data)  # Send to RabbitMQ
        return True
    else:
        logger.info(f"No new data for station {station_id}. Updating last_checked.")
        redis_client.hset(redis_key, "last_checked", datetime.now(timezone.utc).isoformat())
        return False

def parse_station_timestamp(timestamp_str):
    """Parse the station timestamp, adding the current year."""
    now = datetime.now()
    parsed_date = datetime.strptime(f"{now.year}-{timestamp_str}", "%Y-%d-%m %H:%M")
    if parsed_date > now:
        parsed_date = parsed_date.replace(year=now.year - 1)
    return parsed_date

async def get_station_data(session, station_id):
    """Retrieve data for a specific weather station asynchronously."""
    station_url = f"{STATION_WEBSITE_URL}/{station_id}"
    response = session.get(station_url)

    if response.ok:
        data = json.loads(response.text)
        logger.info(f"Station {station_id} data: {data}")
        return data
    else:
        logger.error(f"Failed to retrieve station {station_id} data.")
        return None

def session_check_and_login(session):
    """Check the session and log in again if necessary."""
    if not login_and_redirect(session):
        logger.warning("Re-authentication failed.")
    else:
        logger.info("Session renewed successfully.")

def extract_token(response):
    """Extract hidden token from the login page."""
    soup = BeautifulSoup(response.text, 'html.parser')
    input_hidden = soup.find('input', {'type': 'hidden', 'name': '_token'})
    return input_hidden.get('value') if input_hidden else None

def login_and_redirect(session):
    """Attempt login by accessing the main page and redirect if needed."""
    response = session.get(STATION_WEBSITE_URL, allow_redirects=True)

    if response.url.endswith(LOGIN_ROUTE):
        logger.info("Redirected to login, performing authentication.")
        token = extract_token(response)

        if not token:
            logger.error("Failed to retrieve the token.")
            return False

        form_data = {'_token': token, 'email': USER, 'password': PASSWORD}
        login_response = session.post(LOGIN_ROUTE, data=form_data)

        if login_response.ok:
            logger.info("Login successful.")
            return True
        else:
            logger.error(f"Login failed: {login_response.status_code}")
            return False
    else:
        logger.info("Accessed the main page successfully.")
        return True

async def main_loop(polling_interval: int = 600):
    """
    Main loop to poll station data and ensure session validity.
    :param polling_interval: Interval in seconds.
    :return:
    """
    station_ids = await fetch_station_ids()

    if not station_ids:
        logger.error("No station IDs found. Exiting...")
        return

    with requests.Session() as session:
        logger.info("Initial access attempt to the main page.")
        login_and_redirect(session)

        next_session_check = datetime.now(timezone.utc) + timedelta(hours=1)

        while True:
            try:
                for station_id in station_ids:
                    station_data = await get_station_data(session, station_id)
                    if station_data and station_data["lecturas"]:
                        timestamp_str = station_data.get("fecha", "")
                        new_timestamp = parse_station_timestamp(timestamp_str)
                        await check_and_update_redis(station_id, new_timestamp, station_data)

                if datetime.now(timezone.utc) >= next_session_check:
                    session_check_and_login(session)
                    next_session_check = datetime.now(timezone.utc) + timedelta(hours=1)

                sleep_time = polling_interval
                logger.warning(f"{sleep_time} seconds until next polling.")
                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                session_check_and_login(session)

if __name__ == '__main__':
    asyncio.run(main_loop())