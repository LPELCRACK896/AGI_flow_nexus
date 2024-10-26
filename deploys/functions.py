import json

def get_dict_payload_from_response(response):
    try:
        payload = response.json()
    except ValueError:
        content = response.content.decode("utf-8")
        payload = json.loads(content)

    return payload

def build_download_url_from_shared_drive(share_url)-> str:
    """
    Example url: "https://drive.google.com/file/d/1_cJfKJQIkTeRLxUC76Ogkgpa0fFXh6Za/view"
    Expected url: "https://drive.usercontent.google.com/uc?id=1_cJfKJQIkTeRLxUC76Ogkgpa0fFXh6Za&export=download"
    :param share_url:
    :return:
    """
    file_id = share_url.split("/")[-2]
    download_url = f"https://drive.usercontent.google.com/uc?id={file_id}&export=download"
    return download_url