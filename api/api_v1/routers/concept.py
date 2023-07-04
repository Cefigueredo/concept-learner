from typing import Any

import fastapi
from fastapi import responses, status
from sqlalchemy.ext import asyncio

import schemas.concept as schemas
from api import dependencies
from crud.crud_concept import crud_concept

router = fastapi.APIRouter(
    prefix="/concept",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
    tags=["Concept"],
)


@router.get(
    "",
    response_model=list[schemas.Concept],
    status_code=status.HTTP_200_OK,
)
async def get_concepts(
    skip: int = 0,
    limit: int = fastapi.Query(le=100, ge=1, default=50),
    db: asyncio.AsyncSession = fastapi.Depends(dependencies.get_async_db),
) -> Any:
    """Get all Concepts"""
    response = await crud_concept.get_multiple(db, skip=skip, limit=limit)

    schema = [schemas.ConceptInDB.from_orm(record) for record in response]

    return schema


@router.get(
    "/{concept_id}",
    response_model=schemas.Concept,
    status_code=status.HTTP_200_OK,
)
async def get_concept(
    concept_id: str = fastapi.Path(
        max_length=63,
        description="Concept ID",
    ),
    db: asyncio.AsyncSession = fastapi.Depends(dependencies.get_async_db),
) -> Any:
    """Get Concept by id"""
    concept = await crud_concept.get(db, id=concept_id)

    schema = schemas.ConceptInDB.from_orm(concept)

    return schema


@router.post(
    "",
    response_model=schemas.Concept,
    status_code=status.HTTP_201_CREATED,
)
async def add_concept(
    *,
    db: asyncio.AsyncSession = fastapi.Depends(dependencies.get_async_db),
    concept: schemas.Concept = fastapi.Body(
        example={
            "id": "4d9c6b62-de34-11ed-b5ea-0242ac120002",
            "posting_id": "4d9c6b62-de34-11ed-b5ea-0242ac120003",
            "user_id": "",
            "created_at": 123123123,
            "type": "referral",
            "company": "Factored",
        }
    ),
) -> Any:
    """Create a new Concept"""
    db_concept = await crud_concept.create(db, concept)

    schema = schemas.ConceptInDB.from_orm(db_concept)

    return schema


@router.put(
    "/{concept_id}",
    response_model=schemas.Concept,
    status_code=status.HTTP_200_OK,
)
async def update_concept(
    *,
    db: asyncio.AsyncSession = fastapi.Depends(dependencies.get_async_db),
    concept_id: str = fastapi.Path(
        max_length=63,
        description="Concept ID",
    ),
    concept: schemas.ConceptUpdate = fastapi.Body(
        examples={
            "All_fields": {
                "summary": "An example with all fields",
                "description": "Description",
                "value": {
                    "concept": "Pizza",
                    "difficutly": "Pizza",
                },
            },
            "Partial_fields": {
                "summary": "An example with partial fields",
                "description": "Description",
                "value": {
                    "concept": "Pizza",
                    "difficutly": "Pizza",
                },
            },
        }
    ),
) -> Any:
    """Update an concept"""
    db_concept_updated = await crud_concept.update(db, concept, id=concept_id)

    schema = schemas.ConceptInDB.from_orm(db_concept_updated)
    return schema


@router.delete("/{concept_id}", status_code=status.HTTP_200_OK)
async def delete_concept(
    concept_id: str = fastapi.Path(
        max_length=63,
        description="Concept ID",
    ),
    db: asyncio.AsyncSession = fastapi.Depends(dependencies.get_async_db),
) -> responses.JSONResponse:
    """Delete an concept"""
    await crud_concept.delete(db, id=concept_id)

    return responses.JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": ("Deletion of Employee was executed successfully.")
        },
    )
