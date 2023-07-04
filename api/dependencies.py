from typing import AsyncGenerator

from db import async_session


async def get_async_db() -> AsyncGenerator:
    try:
        database = async_session.AsyncSessionLocal()
        yield database
    finally:
        await database.close()
