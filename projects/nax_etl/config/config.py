from components.utils.Config import Config

redis = Config(
    path="./components/env/redis.env",
    required_fields=[
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_PASSWORD"
    ]
)
redis.setup()

credentials = Config(
    path="./components/env/credentials.env",
    required_fields=[
        "NAX_USERNAME",
        "NAX_PASSWORD",
        "ICC_USER",
        "ICC_PASSWORD"
    ]

)
credentials.setup()

routes = Config(
    path="./components/env/routes.env",
    required_fields=[
        "NAX_LOGIN",
        "NAX_TEST_TOKEN",
        "NAX_GET_USER",
        "NAX_GET_VALUES",
        "NAX_DOWNLOAD_TIFF_IMAGE"
    ]
)

routes.setup()

data_sources = Config(
    path="./components/env/data_sources.env",
    required_fields=[
        "NAX_API",
        "ICC_URL"
    ]
)

data_sources.setup()