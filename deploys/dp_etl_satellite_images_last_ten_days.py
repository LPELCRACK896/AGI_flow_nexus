from deploys.flows import etl_satellite_images_last_ten_days

if __name__ == '__main__':
    etl_satellite_images_last_ten_days.serve(
            name="Carga incremental imágenes satelitales cada 10 días.",
            cron="0 0 */10 * *",
            description="Este flujo se ejecuta cada 10 días.")