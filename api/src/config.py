from pydantic_settings import  BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PG_DATABASE_URL: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str
    PG_HOST: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file="./src/.env",
        extra="ignore"
    )



settings = Settings()