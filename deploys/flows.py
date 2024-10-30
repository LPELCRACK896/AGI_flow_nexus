from datetime import date, timedelta
from prefect import flow, get_run_logger
from scripts.regsetup import description

from deploys.nax import authentication, get_areas, get_products_on_area, get_and_load_products_from_area
from deploys.redis_tasks import get_redis_connection
from deploys.ceph import CephConnection
from deploys.models import Area, Product
from deploys.db import initialize_connection, insert_area_and_products

@flow
def etl_satellite_images_last_ten_days():
    return etl_satellite_images(
        start_date=date.today() - timedelta(days=10),
        end_date=date.today(),
    )

@flow
def etl_satellite_images(start_date: date, end_date: date):
    difference = (end_date - start_date).days
    if difference > 12:
        raise ValueError("End date cannot be more than 12 days away from start date")

    redis_connection = get_redis_connection()

    token = authentication(redis_connection)
    areas = get_areas(token)

    print(f"Found {len(areas)} areas: {areas}")
    for area in areas:
        get_products_on_area(token, area)
    ceph_connection = CephConnection()
    pg_conn = initialize_connection()
    get_and_load_products_from_area(token=token, areas=areas, start_date=start_date, end_date=end_date, ceph_conn=ceph_connection, pg_conn=pg_conn)
    pg_conn.close()



@flow
def etl_satellite_images_per_area(start_date: date, end_date: date, area_name: str):
    logger = get_run_logger()
    difference = (end_date - start_date).days
    if difference > 12:
        raise ValueError("End date cannot be more than 12 days away from start date")

    redis_connection = get_redis_connection()

    token = authentication(redis_connection)
    areas = get_areas(token)
    filtred_areas = [area for area in areas if area_name == area.name]
    pg_conn = initialize_connection()
    if len(filtred_areas)!=1:
        logger.error(f"Unable to find area with name {area_name}. Try one of these: {', '.join([area.name for area in areas])}")

    target_area = areas[0]
    get_products_on_area(token, target_area)
    ceph_connection = CephConnection()
    get_and_load_products_from_area(
        token=token,
        areas=[target_area],
        start_date=start_date,
        end_date=end_date,
        ceph_conn=ceph_connection,
        pg_conn=pg_conn

    )
    pg_conn.close()


@flow
def etl_extract_area_product():

    redis_connection = get_redis_connection()

    token = authentication(redis_connection)
    areas = get_areas(token)

    for area in areas:
        get_products_on_area(token, area)

    pg_conn = initialize_connection()
    for area in areas:
        insert_area_and_products(pg_conn, area)




"""if __name__ == "__main__":
    etl_extract_area_product()
"""



