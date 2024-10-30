from deploys.flows import etl_satellite_images


if __name__ == '__main__':
    etl_satellite_images.serve(
        name="Carga de datos imágenes satelitales.",
        description="Activación manual de flujo de extracción de datos en un intervalo de fechas que no debe ser mayor a 10 días. "
    )