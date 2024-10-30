import boto3
from datetime import date
from deploys.config import settings
from io import BytesIO
from prefect import task, get_run_logger

from deploys.db import insert_satellite_image
from deploys.models import Area, Product


def build_file_name(file_date: date, area: str, product: str) -> str:
    date_str = file_date.strftime('%Y-%m-%d')
    return f"{area}/{product}/{date_str}.tif"


class CephConnection:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'http://{settings.CEPH_RGW_HOST}:{settings.CEPH_RGW_PORT}',
            aws_access_key_id=settings.CEPH_RGW_ACCESS_KEY,
            aws_secret_access_key=settings.CEPH_RGW_SECRET_KEY,
            verify=False
        )
        self.year_partition: date = date(year=settings.YEAR_PARTITION, month=1, day=1)

    @task(name="Upload image to ceph. Calls task to map into postgres database")
    def upload_satellite_image(self, file_data: bytes, file_date: date, area: Area, product: Product):
        logger = get_run_logger()
        filename = build_file_name(file_date, area.name, product.name)
        target_bucket = (
            settings.HOT_BUCKET_NAME if file_date > self.year_partition else settings.COLD_BUCKET_NAME
        )

        etag = self.__upload_data(filename=filename, file_data=file_data, bucket=target_bucket)
        if etag:
            logger.info(f"File '{filename}' successfully uploaded to bucket '{target_bucket}'. ETag: {etag}")

            return etag
        else:
            logger.error(f"Failed to upload '{filename}' to bucket '{target_bucket}'.")
            return


    def __upload_data(self, filename: str, file_data: bytes, bucket: str):

        logger = get_run_logger()
        try:

            file_obj = BytesIO(file_data)
            response = self.s3.upload_fileobj(file_obj, bucket, filename)
            etag = self.s3.head_object(Bucket=bucket, Key=filename)["ETag"]
            logger.info(f"File '{filename}' successfully uploaded to bucket '{bucket}'. ETag: {etag}")
            return etag
        except Exception as e:
            logger.error(f"An error occurred uploading s3 file: {e}")
            return None

    def __create_bucket(self, bucket_name: str):
        try:
            self.s3.create_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' creado exitosamente.")
        except Exception as e:
            print(f"Error al crear el bucket: {e}")

    def list_buckets(self):
        try:
            response = self.s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            print(f"Buckets disponibles: {buckets}")
            return buckets
        except Exception as e:
            print(f"Error al listar los buckets: {e}")

    def __delete_bucket(self, bucket_name: str):
        try:
            self.s3.delete_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' eliminado exitosamente.")
        except Exception as e:
            print(f"Error al eliminar el bucket: {e}")