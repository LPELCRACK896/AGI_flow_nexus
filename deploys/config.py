
from pydantic_settings import  BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    CEPH_RGW_HOST: str
    CEPH_RGW_PORT: int
    CEPH_RGW_ACCESS_KEY: str
    CEPH_RGW_SECRET_KEY: str
    YEAR_PARTITION: int

    HOT_BUCKET_NAME:str
    COLD_BUCKET_NAME:str

    REDIS_HOST: str
    REDIS_PORT: int

    NAX_USER: str
    NAX_PASSWORD: str

    PG_DATABASE_URL: str
    PG_USER: str
    PG_PASSWORD: str
    PG_DATABASE: str
    PG_HOST: str

    model_config = SettingsConfigDict(
        env_file="./.env",
        extra="ignore"
    )

settings = Settings()

class NaxRouting(BaseSettings):
    BASE_URL: str
    POST_LOGIN: str
    GET_CHECK_TOKEN: str
    GET_USER: str
    GET_VALUES: str
    POST_DOWNLOAD_TIFF_IMAGE : str
    GET_AREA_PRODUCTS: str

    model_config = SettingsConfigDict(
        env_file="./routes.env",
        extra="ignore"
    )



nax_routing = NaxRouting()