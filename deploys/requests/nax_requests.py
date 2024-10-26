from deploys.config import nax_routing
import requests
import datetime


def nax_login(user, password):
    return requests.post(
        url=nax_routing.BASE_URL + nax_routing.POST_LOGIN,
        data={"user": user, "password": password}
    )

def nax_check_token(token):
    headers = {"Authorization": token}
    return requests.get(
        url=nax_routing.BASE_URL + nax_routing.GET_CHECK_TOKEN,
        headers=headers
    )


def nax_get_user(token):
    headers = {"Authorization": token}
    return requests.get(
        url=nax_routing.BASE_URL  + nax_routing.GET_USER,
        headers=headers
    )


def nax_get_values(token, area_id: int, start_date: datetime.datetime, end_date: datetime.datetime):
    headers = {"Authorization": token}
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    ep = nax_routing.GET_VALUES.replace("<area_id>", str(area_id))
    ep = ep.replace("<start_date>", start_date_str)
    ep = ep.replace("<end_date>", end_date_str)

    url = nax_routing.BASE_URL + ep

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

    if diff > 12:
        raise ValueError(f"Cannot request using dates with more than 12 days difference, requested {diff:.2f}")

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    date_range = [start_date_str, end_date_str]
    url =nax_routing.BASE_URL + nax_routing.POST_DOWNLOAD_TIFF_IMAGE
    payload = {
        "fk_producto__fk_area": area_id,
        "fk_producto__nombre": product_name,
        "fecha__range": date_range
    }
    return requests.post(
        url=url,
        headers=headers,
        json=payload
    )


def nax_get_area_products(token:str, area_id: int):
    headers = {"Authorization": token}
    ep = nax_routing.GET_AREA_PRODUCTS.replace("<area_id>", str(area_id))
    url = nax_routing.BASE_URL + ep
    return requests.get(
        url=url,
        headers=headers
    )