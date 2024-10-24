from postgresql import get_connection
from dotenv import dotenv_values
import pandas as pd
import asyncio
import datetime
import json
import os

envs = dotenv_values(".env")

def json_to_dict_and_dataframe(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    dict_data = {}
    for item in data:
        dict_data[item["name"]] = item
    return dict_data

def extract_xls_into_dataframe(file_path, stations_dict):
    df = pd.read_excel(file_path, engine='xlrd')
    df = df.drop(columns=["eto"])
    df = df.rename(columns={
        'Estacion': 'name',
        "Fecha": "date_time",
        "radiacion": "radiation",
        "humedad relativa": "relative_humidity",
        "precipitacion": "precipitation",
        "temperatura": "temperature",
        "velocidad viento": "wind_speed",
        "mojadura": "wetness",
        "direccion viento": "wind_direction",
        "indice calor": "heat_index"
    })

    df['station_id'] = df['name'].map(lambda x: stations_dict.get(x, {}).get('station_id'))
    df['original_date_time'] = df['date_time']

    df['date_time'] = pd.to_datetime(
        df['original_date_time'],
        errors='coerce',
        format='%Y-%m-%d %H:%M'
    )

    if df['date_time'].isna().sum() > 0:
        print("Advertencia: Algunas fechas no pudieron ser convertidas inicialmente.")
        print(df[df['date_time'].isna()])

        df['temp_date_time'] = pd.to_datetime(
            df['original_date_time'],
            format='%d/%m/%y %H:%M',
            errors='coerce'
        )

        df['date_time'] = df['date_time'].fillna(df['temp_date_time'])

        df = df.drop(columns=["temp_date_time"])

    df = df.drop(columns=["original_date_time"])
    df['date_time'] = df['date_time'].dt.tz_localize('America/Guatemala')

    df = df.drop(columns=['name'])

    return df

async def upload_into_register_table(dataframe):
    conn = await get_connection(
        user=envs["PG_USER"],
        password=envs["PG_PASSWORD"],
        database=envs["PG_DATABASE"],
        host=envs["PG_HOST"]
    )
    query = """
    INSERT INTO StationRegisters (
        station_id, date_time, temperature, radiation, 
        relative_humidity, precipitation, wind_speed, 
        wetness, wind_direction, heat_index
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    ON CONFLICT (station_id, date_time) DO NOTHING
    """
    for _, row in dataframe.iterrows():
        await conn.execute(
            query,
            row['station_id'], row['date_time'], row['temperature'],
            row['radiation'], row['relative_humidity'], row['precipitation'],
            row['wind_speed'], row['wetness'], row['wind_direction'], row['heat_index']
        )

async def upload_xls_file_to_db_pipeline(file_name, dir_path):
    file_path = os.path.join(dir_path, file_name)
    stations_dict = json_to_dict_and_dataframe('./data/stations.json')
    dataframe = extract_xls_into_dataframe(file_path, stations_dict)
    await upload_into_register_table(dataframe)

    return

directory_path = './data/xls_cleaned'
files_to_load = os.listdir(directory_path)

async def upload_multiple_files():
    for file_name in files_to_load:
        await upload_xls_file_to_db_pipeline(file_name, directory_path)
        print("Finish uploading " + file_name)


if __name__ == "__main__":
    print(os.getcwd())
    asyncio.run(upload_multiple_files())