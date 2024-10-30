CREATE TABLE Areas (
    area_id INTEGER PRIMARY KEY, -- Clave primaria, única, no es serial (los valores serán gestionados manualmente o desde la aplicación)
    area_name VARCHAR(256) -- Nombre del área (opcionalmente puedes definirlo como NOT NULL si es obligatorio)
);

CREATE TABLE AreaProducts (
    area_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(256),
    CONSTRAINT fk_area FOREIGN KEY (area_id) REFERENCES Areas (area_id) ON DELETE CASCADE,
    CONSTRAINT unique_area_product UNIQUE (area_id, product_id)
);

CREATE INDEX idx_area_product ON AreaProducts (area_id, product_id);



CREATE TABLE SatelliteImages (
    product_id INTEGER NOT NULL, -- Clave foránea hacia AreaProducts.product_id
    area_id INTEGER NOT NULL,    -- Clave foránea hacia Areas.area_id
    date_time TIMESTAMPTZ NOT NULL, -- Marca de tiempo con zona horaria
    image_etag TEXT NOT NULL,    -- Identificador único de la imagen

    -- Claves foráneas para asegurar la integridad referencial
    CONSTRAINT fk_product FOREIGN KEY (product_id)
        REFERENCES AreaProducts (product_id) ON DELETE CASCADE,

    CONSTRAINT fk_area FOREIGN KEY (area_id)
        REFERENCES Areas (area_id) ON DELETE CASCADE,

    CONSTRAINT unique_image UNIQUE (product_id, area_id, date_time)
);

CREATE INDEX ix_satellite_images ON SatelliteImages (area_id, product_id, date_time DESC);

SELECT create_hypertable('SatelliteImages', 'date_time');

