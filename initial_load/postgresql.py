import asyncpg

async def get_connection(user, password, database, host) -> asyncpg.Connection:
    return await asyncpg.connect(
        user=user,
        password=password,
        database=database,
        host=host
    )
