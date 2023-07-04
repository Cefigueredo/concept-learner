from typing import AsyncGenerator

import fastapi.security

from db import async_session

oauth2_scheme = fastapi.security.OAuth2PasswordBearer(
    tokenUrl="/v1/login/token"
)


async def get_async_db() -> AsyncGenerator:
    try:
        database = async_session.AsyncSessionLocal()
        yield database
    finally:
        await database.close()
