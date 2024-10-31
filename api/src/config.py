from pydantic_settings import  BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PG_DATABASE_URL: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str
    PG_HOST: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    CEPH_RGW_HOST: str
    CEPH_RGW_PORT: str
    CEPH_RGW_ACCESS_KEY: str
    CEPH_RGW_SECRET_KEY: str

    YEAR_PARTITION: int
    HOT_BUCKET_NAME: str
    COLD_BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file="./src/.env",
        extra="ignore"
    )

settings = Settings()