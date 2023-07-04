from sqlalchemy import event
from sqlalchemy.ext import asyncio
from sqlalchemy.orm import sessionmaker

from core import config

async_engine: asyncio.AsyncEngine = asyncio.create_async_engine(
    config.settings.SQLALCHEMY_DATABASE_URI.format(protocol="asyncpg"),
    pool_recycle=300,
    pool_pre_ping=True,
    echo=config.settings.SQLALCHEMY_ECHO,
)


@event.listens_for(async_engine.sync_engine, "do_connect")
def handle_do_connect(dialect, conn_rec, cargs, cparams):
    if config.settings.DB_IAM_AUTH:
        password = config.get_rds_password(
            config.settings.POSTGRES_HOST,
            config.settings.POSTGRES_USER,
            config.settings.POSTGRES_PORT,
            url_encoded=False,
        )
    else:
        password = config.settings.POSTGRES_PASSWORD

    cparams["password"] = password


AsyncSessionLocal = sessionmaker(  # type: ignore
    bind=async_engine,
    autocommit=False,
    expire_on_commit=False,
    class_=asyncio.AsyncSession,
    autoflush=False,
)
