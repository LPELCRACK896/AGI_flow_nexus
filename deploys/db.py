from prefect import task, get_run_logger
from deploys.config import settings
import psycopg2
from datetime import date

def initialize_connection():
    """
    Inicializa y retorna una conexión sincrónica con PostgreSQL.
    """
    conn = psycopg2.connect(
        user=settings.PG_USER,
        password=settings.PG_PASSWORD,
        database=settings.PG_DATABASE,
        host=settings.PG_HOST,
    )
    return conn

@task
def insert_satellite_image(conn, product_id: int, area_id: int, date_time: date, image_etag: str) -> bool:
    """
    Inserta un registro en la tabla SatelliteImages.
    """
    logger = get_run_logger()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO SatelliteImages (product_id, area_id, date_time, image_etag)
                VALUES (%s, %s, %s, %s);
                """,
                (product_id, area_id, date_time, image_etag)
            )
        conn.commit()
        logger.info("Registro insertado exitosamente.")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error al insertar registro: {e}")
        return False

