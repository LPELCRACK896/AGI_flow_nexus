import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import asyncio
from other.volume_analysis.db import get_connection
import projects.agi_api.config.config as cfg # deleted on refactor.

pg_config = cfg.postgres
pg_user = pg_config.USER
pg_password = pg_config.PASSWORD
pg_database = pg_config.DATABASE
pg_host = pg_config.HOST

async def get_table_info():
    conn = await get_connection(
        user=pg_user,
        password=pg_password,
        database=pg_database,
        host=pg_host
    )
    try:
        query_size = "SELECT pg_table_size('StationRegisters');"
        query_rows = "SELECT COUNT(*) FROM StationRegisters;"
        size_in_bytes = await conn.fetchval(query_size)
        row_count = await conn.fetchval(query_rows)
        print(f"Filas: {row_count}, Tamaño: {size_in_bytes} bytes")
        return size_in_bytes, row_count
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

# Cargar datos desde CSV
async def load_day_data(filename, station_id=67):
    data = pd.read_csv(f"./data/samples/csv/{filename}")
    data = data.rename(columns={
        "Estacion": "name", "Fecha": "date_time", "temperatura": "temperature",
        "radiacion": "radiation", "humedad relativa": "relative_humidity",
        "precipitacion": "precipitation", "velocidad viento": "wind_speed",
        "mojadura": "wetness", "direccion viento": "wind_direction",
        "indice calor": "heat_index"
    })
    data["date_time"] = pd.to_datetime(data["date_time"], format='%Y-%m-%d %H:%M')

    conn = await get_connection(
        user=pg_user, password=pg_password, database=pg_database, host=pg_host
    )
    try:
        query = """
            INSERT INTO StationRegisters (
                station_id, name, date_time, temperature, radiation, 
                relative_humidity, precipitation, wind_speed, 
                wetness, wind_direction, heat_index
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        """
        for _, row in data.iterrows():
            await conn.execute(
                query,
                station_id, row["name"],
                row["date_time"], float(row["temperature"]),
                float(row["radiation"]), float(row["relative_humidity"]),
                float(row["precipitation"]), float(row["wind_speed"]),
                float(row["wetness"]), float(row["wind_direction"]),
                float(row["heat_index"])
            )
        print(f"Datos de {filename} cargados correctamente.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()

# Añadir línea de regresión
def add_regression_line(x, y, ax):
    m, b = np.polyfit(x, y, 1)
    y_fit = m * np.array(x) + b
    ax.plot(x, y_fit, color='blue', linestyle='--', linewidth=2)
    print(m)
    print(b)
    ax.text(0.05, 0.95, f'y = {m:.10f}x + {b:.10f}',
            transform=ax.transAxes, fontsize=10, verticalalignment='top')

# Generar gráficas con regresión lineal
def generate_plots(sizes, row_counts):
    iterations = range(len(sizes))

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # Gráfica 1: Número de Filas vs Iteraciones
    axes[0].plot(iterations, row_counts, marker='o')
    axes[0].set_xlabel('Iteración')
    axes[0].set_ylabel('Número de Filas')
    axes[0].set_title('Número de Filas vs Iteraciones')
    add_regression_line(iterations, row_counts, axes[0])

    # Gráfica 2: Tamaño vs Iteraciones
    axes[1].plot(iterations, sizes, marker='o', color='green')
    axes[1].set_xlabel('Iteración')
    axes[1].set_ylabel('Tamaño (Bytes)')
    axes[1].set_title('Tamaño vs Iteraciones')
    add_regression_line(iterations, sizes, axes[1])

    # Gráfica 3: Número de Filas vs Tamaño
    axes[2].plot(sizes, row_counts, marker='o', color='red')
    axes[2].set_xlabel('Tamaño (Bytes)')
    axes[2].set_ylabel('Número de Filas')
    axes[2].set_title('Número de Filas vs Tamaño')
    add_regression_line(sizes, row_counts, axes[2])

    plt.tight_layout()
    plt.show()

# Función principal para realizar las iteraciones y generar las gráficas
async def main():
    sizes = []
    row_counts = []
    days = ["01-10", "02-10", "03-10", "04-10", "05-10"]

    for i in range(6): # 6 veces 5 días = 6 días = 1 mes
        for day in days: # 5 días de sample
            for _ in range(57): # 57 estaciones
                await load_day_data(f"{day}.csv", 67)
            size, row_count = await get_table_info()
            sizes.append(size * 10**-9)
            row_counts.append(row_count)

    generate_plots(sizes, row_counts)

# Ejecutar la función principal
if __name__ == "__main__":
    asyncio.run(main())
