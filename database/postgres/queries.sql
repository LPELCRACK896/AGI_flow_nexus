SELECT *
FROM StationRegisters
WHERE station_id = 1
  AND date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
ORDER BY date_time ASC;


SELECT *
FROM StationRegisters
WHERE station_id = 1
  AND date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
ORDER BY date_time ASC;


/**/
SELECT time_bucket('1 day', date_time) AS day,
       station_id,
       AVG(temperature) AS avg_temp,
       SUM(precipitation) AS total_precip
FROM StationRegisters
WHERE station_id = 1
  AND date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY day, station_id
ORDER BY day ASC;

/*Obtener el promedio de la temperatura cada hora*/
SELECT time_bucket('1 hour', date_time) AS bucket,
       station_id,
       AVG(temperature) AS avg_temp
FROM StationRegisters
WHERE date_time >= NOW() - INTERVAL '1 day'
GROUP BY bucket, station_id
ORDER BY bucket DESC;

/*Máximos y mínimos diarios*/
SELECT time_bucket('1 day', date_time) AS day,
       station_id,
       MAX(temperature) AS max_temp,
       MIN(temperature) AS min_temp,
       MAX(wind_speed) AS max_wind_speed,
       MIN(radiation) AS min_radiation
FROM StationRegisters
WHERE station_id = 1
  AND date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY day, station_id
ORDER BY day ASC;

/*Comparación entre estaciones en un período específico*/
SELECT station_id,
       AVG(temperature) AS avg_temp,
       time_bucket('1 hour', date_time) AS hour
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY station_id, hour
ORDER BY hour ASC, station_id;


SELECT station_id,
       AVG(temperature) AS avg_temp,
       time_bucket('1 hour', date_time) AS hour
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY station_id, hour
ORDER BY hour ASC, station_id;

/*Detección de anomalías (valores fuera de rango)*/
SELECT station_id,
       AVG(temperature) AS avg_temp,
       time_bucket('1 hour', date_time) AS hour
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY station_id, hour
ORDER BY hour ASC, station_id;

/*Acumulación semanal de precipitación*/
SELECT time_bucket('1 week', date_time) AS week,
       station_id,
       SUM(precipitation) AS total_precip
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-31 23:59:59'
GROUP BY week, station_id
ORDER BY week ASC;

/*Último registro disponible para cada estación*/
SELECT station_id,
       last(temperature, date_time) AS last_temp,
       last(wind_speed, date_time) AS last_wind_speed,
       last(precipitation, date_time) AS last_precip
FROM StationRegisters
GROUP BY station_id;


/*Estadísticas horarias con descomposición del índice de calor*/
SELECT time_bucket('1 hour', date_time) AS hour,
       station_id,
       AVG(heat_index) AS avg_heat_index
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY hour, station_id
ORDER BY hour ASC;

/* Análisis de correlación entre temperatura y humedad */
SELECT time_bucket('1 hour', date_time) AS hour,
       station_id,
       AVG(heat_index) AS avg_heat_index
FROM StationRegisters
WHERE date_time BETWEEN '2024-10-01 00:00:00' AND '2024-10-10 23:59:59'
GROUP BY hour, station_id
ORDER BY hour ASC;
