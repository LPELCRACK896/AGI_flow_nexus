from typing import List, Optional
import boto3
from botocore.exceptions import ClientError
from datetime import date
from api.src.config import settings

class CephBuckets:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            endpoint_url=f'http://{settings.CEPH_RGW_HOST}:{settings.CEPH_RGW_PORT}',
            aws_access_key_id=settings.CEPH_RGW_ACCESS_KEY,
            aws_secret_access_key=settings.CEPH_RGW_SECRET_KEY,
            verify=False
        )

        self.year_partition: date = date(year=settings.YEAR_PARTITION, month=1, day=1)

    async def get_image(self, area_name: str, product_name: str, date_time: date) -> Optional[bytes]:
        """Retrieve a specific image by constructing its name based on area, product, and date."""
        bucket_name = settings.COLD_BUCKET_NAME if self.is_date_in_cold_zone(date_time) else settings.HOT_BUCKET_NAME

        image_key = f"{area_name}/{product_name}/{date_time.strftime('%Y-%m-%d')}.tif"

        try:
            image_response = self.s3.get_object(Bucket=bucket_name, Key=image_key)
            return image_response['Body'].read()

        except ClientError as e:
            print(f"Error retrieving image with key {image_key}: {e}")
            return None

    async def get_images_by_area_products(self, area_name: str, product_name: str, from_cold_zone: bool = False) -> List[str]:
        bucket_name = settings.COLD_BUCKET_NAME if from_cold_zone else settings.HOT_BUCKET_NAME
        prefix = f"{area_name}/{product_name}/"

        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            if 'Contents' not in response:
                return []

            images = [content['Key'] for content in response['Contents']]
            return images

        except ClientError as e:
            print(f"Error al obtener imágenes: {e}")
            return []

    def is_date_in_cold_zone(self, file_date: date) -> bool:

        return bool(file_date < self.year_partition)
