from typing import List, Optional
from prefect import task, unmapped
from datetime import datetime, date
import redis
import zipfile
import io

from deploys.requests.nax_requests import (
    nax_login, nax_check_token, nax_get_user,
    nax_get_area_products, nax_get_multiple_tiff_images
)
from deploys.requests.other import download_file
from deploys.redis_tasks import get_nax_token, set_nax_token
from functions import get_dict_payload_from_response, build_download_url_from_shared_drive
from deploys.models import Area, Product
from deploys.config import settings
from prefect.logging import get_run_logger
from deploys.ceph import CephConnection
from deploys.db import insert_satellite_image

@task
def new_login(redis_connection: redis.Redis):
    logger = get_run_logger()
    token = login(settings.NAX_USER, settings.NAX_PASSWORD)

    if not check_token(token):
        logger.error(f"Generated token is invalid: {token}")
        return None

    set_nax_token(redis_connection, token)
    return token

@task
def authentication(redis_connection: redis.Redis):
    logger = get_run_logger()
    token = get_nax_token(redis_connection)

    if token is None:
        logger.warning("Error finding token in Redis. Starting login process.")
        return new_login(redis_connection)

    if not check_token(token):
        logger.warning(f"Invalid token: {token}. Starting login process.")
        return new_login(redis_connection)

    return token

@task
def login(user: str, password: str) -> str:
    logger = get_run_logger()
    response = nax_login(user, password)

    if response.status_code == 200:
        token = response.content.decode("utf-8").strip('"')
        logger.info(f"Login successful, token stored: {token}")
        return token

    logger.error(f"Login failed with status code: {response.status_code}. Response: {response.text}")
    raise ValueError("Login failed. Ensure proper user and password.")

@task
def check_token(token: str) -> bool:
    logger = get_run_logger()
    response = nax_check_token(token=token)

    if response.status_code == 200:
        return True

    data = response.json()
    if response.status_code in [400, 401, 402, 403]:
        logger.warning(f"Invalid token. API feedback: {data}")
        return False

    logger.error(f"Server error. Status code: {response.status_code}, API feedback: {data}")
    raise Exception(f"Server error. Status code: {response.status_code}, API feedback: {data}")

@task
def get_areas(token) -> Optional[List[Area]]:
    response = nax_get_user(token)
    if response.status_code != 200:
        raise RuntimeError("Failed retrieving user data.")

    payload = get_dict_payload_from_response(response)
    if not payload["areas"]:
        raise Exception("No areas found.")

    return [Area(id=area["id"], name=area["nombre"], title=area["titulo"])
            for area in payload["areas"] if area["activo"]]

@task
def get_products_on_area(token: str, area: Area):
    logger = get_run_logger()
    response = nax_get_area_products(token=token, area_id=area.id)

    if response.status_code != 200:
        raise RuntimeError(f"Failed retrieving product data on area {area.id}")

    payload = get_dict_payload_from_response(response)
    area.products = [Product(id=product["id"], name=product["nombre"], title=product["titulo"])
                     for product in payload]
    logger.info(f"Found {len(area.products)} products in area {area.name}.")

@task
def get_and_load_products_from_area(
    token: str, areas: List[Area], start_date: datetime, end_date: datetime,
    ceph_conn: CephConnection, pg_conn
):
    futures = get_images_drive_url.map(
        unmapped(token),
        [area for area in areas for _ in area.products],
        [product for area in areas for product in area.products],
        unmapped(start_date),
        unmapped(end_date),
        unmapped(ceph_conn),
        unmapped(pg_conn)
    )
    return futures.result()

@task
def get_images_drive_url(
    token: str, area: Area, product: Product, start_date: datetime,
    end_date: datetime, ceph_conn: CephConnection, pg_conn
):
    logger = get_run_logger()
    response = nax_get_multiple_tiff_images(token, area.id, product.name, start_date, end_date)

    if response.status_code == 200:
        data = response.json()
        if "download_link" in data:
            logger.info(f"Got {data['download_link']} for {product.name} from {area.name}.")
            return download_zip_from_drive_shared_and_upload(
                data["download_link"], area, product, ceph_conn, pg_conn
            )

        logger.warning(f"No download_link in response: {data}.")
        return None

    if response.status_code == 400:
        logger.warning(f"No data available for {product.name} in {area.name}.")
        return

    logger.error(f"Got {response.status_code} ({response.text}) for {product.name} in {area.name}.")

@task
def download_zip_from_drive_shared_and_upload(
    share_url: str, area: Area, product: Product, ceph_con: CephConnection, pg_conn
):
    logger = get_run_logger()
    download_url = build_download_url_from_shared_drive(share_url)
    response = download_file(download_url)

    if response.status_code != 200:
        raise RuntimeError(f"Failed downloading file from {download_url}. Status: {response.status_code}")
    try:
        zip_file = zipfile.ZipFile(io.BytesIO(response.content))

        for file_name in zip_file.namelist():
            logger.info(f"Extracting: {file_name}")
            date_data_from_filename = file_name.split(".")[0]
            year, month, day = int(date_data_from_filename[:4]), int(date_data_from_filename[4:6]), int(date_data_from_filename[6:])
            file_date = date(year, month, day)

            with zip_file.open(file_name) as extracted_file:
                file_data = extracted_file.read()
                etag = ceph_con.upload_satellite_image(file_data, file_date, area, product)

                if etag:
                    logger.info(f"File {file_name} uploaded successfully. ETag: {etag}")
                    insert_satellite_image(conn=pg_conn ,product_id=product.id, area_id=area.id, image_etag=etag, date_time=file_date)

                else:
                    logger.error(f"Failed to upload {file_name}.")
    except Exception as e:
        logger.error(f"Unable to extract file from response: {response}")
        return