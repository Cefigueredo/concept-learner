from schemas import base_schema, enums


class ConceptBase(base_schema.BaseSchema):
    concept: str | None
    meaning: str | None
    difficulty: enums.ConceptEnum | None

    class Config:
        validate_assignment = True


class ConceptCreate(ConceptBase):
    concept: str
    meaning: str

    class Config:
        extra = "forbid"


class ConceptUpdate(base_schema.BaseSchema):
    concept: str | None
    meaning: str | None

    class Config:
        validate_assignment = True
        extra = "forbid"


class ConceptInDBBase(ConceptBase):
    id: int

    class Config:
        orm_mode = True


class ConceptInDB(ConceptInDBBase):
    pass


class Concept(ConceptInDBBase):
    pass
