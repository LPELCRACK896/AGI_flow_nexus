from datetime import date, timedelta
from prefect import flow
from deploys.nax import authentication, get_areas, get_products_on_area, get_and_load_products_from_area
from deploys.redis_tasks import get_redis_connection
from deploys.ceph import CephConnection


@flow
def etl_satellite_images_given_dates_product_area(start_date, end_):
    pass

@flow
def etl_satellite_images(start_date: date, end_date: date):

    difference = (end_date - start_date).days
    if difference > 12:
        raise ValueError("End date cannot be more than 12 days away from start date")

    redis_connection = get_redis_connection()

    # Authentication
    token = authentication(redis_connection)
    # Extract Areas
    areas = get_areas(token)

    print(f"Found {len(areas)} areas: {areas}")
    for area in areas:
        get_products_on_area(token, area)
    # Extract Products of Each Area
    ceph_connection = CephConnection()
    get_and_load_products_from_area(token=token, areas=areas, start_date=start_date, end_date=end_date, ceph_conn=ceph_connection)

    # Iterate Over
    pass


if __name__ == "__main__":
    start_date = date(year=2023, month=9, day=1)
    end_date = start_date + timedelta(days=1)
    etl_satellite_images(start_date=start_date, end_date=end_date)