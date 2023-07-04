from crud import base
from models import concepts as models
from schemas import concept as schemas

crud_concept = base.BaseCRUD[models.Concept, schemas.ConceptInDB](
    models.Concept, schemas.ConceptInDB
)
