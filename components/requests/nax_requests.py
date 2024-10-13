from projects.nax_etl.config.config import routes, data_sources
import requests
import datetime


def nax_login(user, password):
    return requests.post(
        url=data_sources.NAX_API + routes.NAX_LOGIN,
        data={"user": user, "password": password}
    )


def nax_check_token(token):
    headers = {"Authorization": token}
    return requests.get(
        url=data_sources.NAX_API + routes.NAX_TEST_TOKEN,
        headers=headers
    )


def nax_get_user(token):
    headers = {"Authorization": token}
    return requests.get(
        url=data_sources.NAX_API + routes.NAX_GET_USER,
        headers=headers
    )


def nax_get_values(token, area_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    headers = {"Authorization": token}
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    ep = routes.NAX_GET_VALUES.replace("<area_id>", str(area_id))
    ep = ep.replace("<start_date>", start_date_str)
    ep = ep.replace("<end_date>", end_date_str)

    url = data_sources.NAX_API + ep

    return requests.get(
        url=url,
        headers=headers
    )


def nax_get_multiple_tiff_images(token: str, area_id: int, product_name: str, start_date: datetime.datetime,
                                 end_date: datetime.datetime):
    """
    Payload
    {"fecha__range":["2024-08-26","2024-09-05"],"fk_producto__nombre":"ndvi_filt","fk_producto__fk_area":219}
    """
    headers = {"Authorization": token}

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    diff = (end_date - start_date).days

    image_count = diff // 5  # Images are taken every 5 days - Integer Divison
    if image_count > 13:
        raise ValueError(f"Cannot request more than 13 images, requested {image_count:.2f}")

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    date_range = [start_date_str, end_date_str]
    return requests.post(
        url=data_sources.NAX_API + routes.NAX_DOWNLOAD_TIFF_IMAGE,
        headers=headers,
        data={
            "fecha__range": date_range,
            "fk_producto__nombre": product_name,
            "fk_producto__fk_area": area_id

        }
    )

