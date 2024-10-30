from deploys.flows import etl_satellite_images_per_area


if __name__ == '__main__':
    etl_satellite_images_per_area.serve(
        name="Carga de datos imágenes satelitales por area",
        description="Activación manual de flujo de extracción, para determinada área, de datos en un intervalo de fechas que no debe ser mayor a 10 días. "
    )