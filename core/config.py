import os
import pathlib
import secrets
from urllib import parse

import boto3  # type: ignore
import pydantic

BASE_DIR = pathlib.Path(__file__).parent.parent.resolve()


class Settings(pydantic.BaseSettings):
    PROJECT_NAME: str = "MAIN PROJECT"
    PROJECT_VERSION: str = "0.1.0"
    PROJECT_DESCRIPTION: str = (
        "This is the main project. It is a template for creating new projects."
    )
    PROJECT_CONTACT: dict = {
        "name": "Carlos Figueredo",
        "email": "email@gmail.com",
    }
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    SSO_ID_TOKEN_EXPIRE_MINUTES: int = 2
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "postgres"
    DB_IAM_AUTH: bool = False
    CORS_ORIGIN: list[str] = ["*"]
    SQLALCHEMY_ECHO: bool = True

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return (
            f"postgresql+{{protocol}}://{self.POSTGRES_USER}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def TEST_SQLALCHEMY_DATABASE_URI(self):
        return (
            f"postgresql+{{protocol}}://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    RDS_HOSTNAME: str = POSTGRES_HOST
    RDS_PORT: int = POSTGRES_PORT

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")


def get_rds_password(
    rds_hostname: str,
    db_user: str,
    rds_port: int = 5432,
    aws_region: str | None = None,
    url_encoded: bool = True,
) -> str:
    """
    Get password for RDS database using IAM authentication

    Args:
        rds_hostname (str): RDS hostname
        db_user (str): Username for database
        rds_port (int, optional): Port for RDS database. Defaults to 5432.
        aws_region (Optional[str], optional): AWS region. Defaults to None.
        url_encoded (bool, optional): Whether to return url encoded password.
        Defaults to True.

    Raises:
        Exception: Unset aws_region

    Returns:
        str: Password for database for given user
    """
    if not aws_region:
        aws_region = boto3.session.Session().region_name
        if not aws_region:
            raise Exception(
                "Error: no aws_region given and the default region is not set!"
            )

    if ":" in rds_hostname:
        split_hostname = rds_hostname.split(":")
        rds_hostname = split_hostname[0]
        rds_port = int(split_hostname[1])

    rds_client = boto3.client("rds")

    password = rds_client.generate_db_auth_token(
        Region=aws_region,
        DBHostname=rds_hostname,
        Port=rds_port,
        DBUsername=db_user,
    )
    if url_encoded:
        return parse.quote_plus(password)
    else:
        return password


settings = Settings()
