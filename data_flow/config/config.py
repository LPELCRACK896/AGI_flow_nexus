from utils.Config import Config


connections = Config(
    path="./env/connections.env",
    required_fields=[
        "REDIS_HOST", 
        "REDIS_PORT"
        ]
    )
connections.setup()


credentials = Config(
    path="./env/credentials.env",
    required_fields=[
        "NAX_USERNAME",
        "NAX_PASSWORD"
        ]

)
credentials.setup()

routes = Config(
    path="./env/routes.env",
    required_fields=[
        "NAX_LOGIN",
        "NAX_TEST_TOKEN"
        ]
)

routes.setup()

data_sources = Config(
    path="./env/data_sources.env",
    required_fields=[
        "NAX_API", 
        "ICC_URL"
    ]
)
data_sources.setup()