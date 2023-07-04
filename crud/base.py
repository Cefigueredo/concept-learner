import datetime as dt
import typing

import fastapi
import pydantic
import sqlalchemy as sa
from fastapi import status
from sqlalchemy import exc
from sqlalchemy.ext import asyncio
from sqlalchemy.orm import properties
from sqlalchemy.sql import dml, selectable

ModelType = typing.TypeVar("ModelType")
InDBPydanticSchema = typing.TypeVar("InDBPydanticSchema")


class BaseCRUD(typing.Generic[ModelType, InDBPydanticSchema]):
    def __init__(
        self,
        model: type[ModelType],
        in_db_pydantic_schema: type[InDBPydanticSchema],
    ):
        self.model = model
        self.in_db_pydantic_schema = in_db_pydantic_schema
        self.fields: set[str] = set()
        self.primary_keys: set[str] = set()

        for attr in sa.inspection.inspect(self.model).attrs:
            if isinstance(attr, properties.ColumnProperty) and (
                cols := attr.columns
            ):
                column = cols[0]
                self.fields.add(column.key)
                if column.primary_key:
                    self.primary_keys.add(column.key)

    async def _filter(self, statement, **fields) -> selectable.Select:
        if fields.keys() <= self.fields:
            # Temporal solution for chaining where clauses
            for field, value in fields.items():
                statement = statement.where(
                    getattr(self.model, field) == value
                )
        else:
            raise KeyError("Invalid key")

        return statement

    async def _pk_filter(
        self, statement, **primary_keys
    ) -> (dml.DMLWhereBase | dml.Delete | dml.Update):
        if primary_keys.keys() <= self.primary_keys:
            for field, value in primary_keys.items():
                statement = statement.where(
                    getattr(self.model, field) == value
                )
        else:
            raise KeyError("Invalid primary key")

        return statement

    def _build_no_result_found_error(
        self, primary_keys
    ) -> fastapi.HTTPException:
        pks = ", ".join(map(lambda t: f"{t[0]}={t[1]}", primary_keys.items()))
        return fastapi.HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"{self.model.__name__} "  # type: ignore
                f"with primary keys {pks} was not found"
            ),
        )

    async def get_multiple(
        self,
        db: asyncio.AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **fields,
    ) -> list[ModelType]:
        async with db.begin():
            statement = sa.select(self.model)
            statement = await self._filter(statement, **fields)

            response = list(
                (await db.execute(statement.offset(skip).limit(limit)))
                .scalars()
                .all()
            )

        return response

    async def get(self, db: asyncio.AsyncSession, **primary_keys) -> ModelType:
        try:
            async with db.begin():
                statement = sa.select(self.model)
                statement = await self._pk_filter(statement, **primary_keys)
                response = (await db.execute(statement)).scalar_one()

        except exc.NoResultFound:
            raise self._build_no_result_found_error(primary_keys)

        return response

    async def get_or_none(
        self, db: asyncio.AsyncSession, **primary_keys
    ) -> typing.Optional[ModelType]:
        try:
            return await self.get(db, **primary_keys)

        except exc.NoResultFound:
            return None

    async def create(
        self,
        db: asyncio.AsyncSession,
        memory_instance,
    ) -> ModelType:
        try:
            async with db.begin():
                db_instance = self.model(
                    **memory_instance.dict()
                )  # type: ignore
                print("db_instance: ", db_instance.__dict__)
                db.add(db_instance)

            await db.commit()

            # Required to load relations
            await db.refresh(db_instance)

            return db_instance

        except exc.IntegrityError as e:
            await db.rollback()
            raise fastapi.HTTPException(
                status.HTTP_400_BAD_REQUEST,
                e.args[0].split("DETAIL: ")[1],
            )

    async def delete(self, db: asyncio.AsyncSession, **primary_keys) -> None:
        async with db.begin():
            statement = sa.delete(self.model)
            statement = await self._pk_filter(statement, **primary_keys)
            statement = statement.returning(self.model)
            await db.execute(statement)

        await db.commit()

    async def update(
        self, db: asyncio.AsyncSession, memory_instance, **primary_keys
    ) -> ModelType:
        try:
            async with db.begin():
                statement = sa.select(self.model)
                statement = await self._pk_filter(statement, **primary_keys)
                db_instance = (await db.execute(statement)).scalar_one()

                if hasattr(memory_instance, "last_updated_ts"):
                    memory_instance.last_updated_ts = dt.datetime.utcnow()

                new_data = memory_instance.dict(exclude_unset=True)

                for field, value in new_data.items():
                    setattr(db_instance, field, value)

            await db.commit()

            return db_instance

        except pydantic.ValidationError as e:
            raise fastapi.HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.errors(),
            )

        except exc.IntegrityError as e:
            await db.rollback()
            raise fastapi.HTTPException(
                status.HTTP_400_BAD_REQUEST,
                e.args[0].split("DETAIL: ")[1],
            )

        except exc.NoResultFound:
            raise self._build_no_result_found_error(primary_keys)
