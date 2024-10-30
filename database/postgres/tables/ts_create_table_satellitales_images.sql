CREATE TABLE SatelliteImages(
    product_id INTEGER NOT NULL,
    area_id INTEGER NOT NULL,
    date_time TIMESTAMPTZ NOT NULL,
    image_etag TEXT NOT NULL
);
CREATE INDEX ix_satellite_images ON SatelliteImages (area_id, product_id, date_time DESC);

SELECT create_hypertable('SatelliteImages', 'date_time');
