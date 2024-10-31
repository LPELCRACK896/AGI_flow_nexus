from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import StreamingResponse
from datetime import datetime, date
from typing import List, Optional
from io import BytesIO
import zipfile

from api.src.db.main import get_session
from api.src.db.operations.satelliteimages import SatelliteImagesService
from api.src.storage.CephBuckets import CephBuckets

ceph_buckets = CephBuckets()

satellite_images_router = APIRouter()

@satellite_images_router.get("/areas", response_model=List[dict])
async def get_areas(session: AsyncSession = Depends(get_session)):
    service = SatelliteImagesService(session)
    areas = await service.list_all_areas()
    return areas

@satellite_images_router.get("/products", response_model=List[dict])
async def get_products(session: AsyncSession = Depends(get_session)):
    service = SatelliteImagesService(session)
    products = await service.list_all_products()
    return products

@satellite_images_router.get("/areas/{area_id}", response_model=dict)
async def get_area_by_id(area_id: int, session: AsyncSession = Depends(get_session)):
    service = SatelliteImagesService(session)
    results = await service.get_area_with_products(area_id)
    if results is None:
        raise HTTPException(status_code=404, detail=f"Area with ID {area_id} not found.")
    return {"area_id": area_id, **results}

@satellite_images_router.get("/products/{area_id}/{product_id}", response_model=dict)
async def get_product_by_id(
    area_id: int, product_id: int, session: AsyncSession = Depends(get_session)
):
    service = SatelliteImagesService(session)
    product_name = await service.get_product_name(area_id, product_id)
    if product_name is None:
        raise HTTPException(status_code=404, detail=f"Product with ID {product_id} in area {area_id} not found.")
    return {"area_id": area_id, "product_id": product_id, "product_name": product_name}

@satellite_images_router.get("/etags", response_model=List[str])
async def get_etags_in_range(
    area_id: int,
    product_id: int,
    start_date: datetime = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: datetime = Query(..., description="End date in ISO format (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_session)
):
    service = SatelliteImagesService(session)
    etags = await service.get_etags_in_date_range(area_id, product_id, start_date, end_date)
    if not etags:
        raise HTTPException(status_code=404, detail="No ETags found for the given range.")
    return etags


@satellite_images_router.get("/images/by-area-product", response_model=None)
async def get_images_by_area_product(
        area_name: str,
        product_name: str,
        from_cold_zone: bool = Query(False, description="Specify if the images are in the cold zone")
):

    image_keys = await ceph_buckets.get_images_by_area_products(area_name, product_name, from_cold_zone)

    if not image_keys:
        raise HTTPException(status_code=404, detail="No images found for the specified area and product.")
    dates_available = []
    for image_key in image_keys:
        split_image_key = image_key.split("/")
        string_date =split_image_key[2].split(".")[0]
        list_date = string_date.split("-")
        image_k_date = date(year=int(list_date[0]), month=int(list_date[1]), day=int(list_date[2]))
        dates_available.append((image_k_date, string_date))

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for date_available in dates_available:
            image_data = await ceph_buckets.get_image(area_name, product_name, date_available[0])
            if image_data:
                file_name = f"{date_available[1]}.tif"
                zip_file.writestr(file_name, image_data)

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={area_name}_{product_name}_images_{'cold' if from_cold_zone else 'hot'}.zip"}
    )

@satellite_images_router.get("/image", response_model=Optional[bytes])
async def get_image(
        area_name: str,
        product_name: str,
        date_time : date = Query(..., description="Date in ISO format (YYYY-MM-DD)"),
):

    image_data = await ceph_buckets.get_image(area_name, product_name, date_time)

    if image_data is None:
        raise HTTPException(status_code=404, detail="Image not found for the specified area, product, and date.")

    file_name = f"{area_name}_{product_name}_{date_time}.tif"
    return StreamingResponse(
        iter([image_data]),  # Stream the bytes
        media_type="image/tif",  # Specify the content type of the image
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )
