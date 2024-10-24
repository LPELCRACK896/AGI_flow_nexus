CREATE TABLE StaticStations (
    id SERIAL PRIMARY KEY,
    station_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(256),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    altitude INTEGER NOT NULL,
    stratum VARCHAR(256)
);

CREATE TABLE StationRegisters (
    station_id INTEGER NOT NULL,
    date_time TIMESTAMPTZ NOT NULL,
    temperature REAL,
    radiation REAL,
    relative_humidity REAL,
    precipitation REAL,
    wind_speed REAL,
    wetness REAL,
    wind_direction REAL,
    heat_index REAL,
    PRIMARY KEY (station_id, date_time),
    CONSTRAINT fk_station FOREIGN KEY (station_id) REFERENCES StaticStations(station_id) ON DELETE CASCADE
);

CREATE INDEX ix_station_id_date_time ON StationRegisters (station_id, date_time DESC);

/* Convertir la tabla a hypertable */
SELECT create_hypertable('StationRegisters', 'date_time');
