from components.utils.Config import Config


postgres = Config(
    path="./components/env/postgres.env",
    required_fields=[
        "DATABASE_URL"
    ]
)
postgres.setup()