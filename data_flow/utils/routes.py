from config.config import routes, data_sources
import requests


nax_login = lambda user, password : requests.post(url=data_sources.NAX_API + routes.NAX_LOGIN, data={"user": user, "password": password})
nax_check_token = lambda headers: requests.get(url=data_sources.NAX_API + routes.NAX_TEST_TOKEN, headers=headers)


