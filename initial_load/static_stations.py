import json
from postgresql import get_connection


def load_json_data(file_path: str) -> list:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


stations = load_json_data("./data/stations.json")


from dotenv import dotenv_values

envs = dotenv_values(".env")

async def upload_data(stations):
    conn = await get_connection(
        user=envs["PG_USER"],
        password=envs["PG_PASSWORD"],
        database=envs["PG_DATABASE"],
        host=envs["PG_HOST"]
    )
    try:
        query = """
        INSERT INTO StaticStations (
            station_id, name, latitude, longitude, altitude, stratum
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        for station in stations:
            await conn.execute(
                query,
                station["station_id"],
                station["name"],
                float(station["latitude"]),
                float(station["longitude"]),
                int(station["altitude"]),
                station["stratum"]
            )
        print("Estaciones cargadas correctamente.")
    except Exception as e:
        print(f"Error al cargar los datos: {e}")
    finally:
        await conn.close()



import asyncio

async def main():
    await upload_data(stations)

if __name__ == "__main__":
    asyncio.run(main())