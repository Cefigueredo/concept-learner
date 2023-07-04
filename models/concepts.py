import sqlalchemy as sa
import sqlalchemy.orm as orm

from schemas import enums

metadata = sa.MetaData(schema="main")


class Base(orm.DeclarativeBase):
    metadata = metadata


class Concept(Base):
    __tablename__ = "concept"

    id: orm.Mapped[int] = orm.mapped_column(sa.Integer(), primary_key=True)
    concept: orm.Mapped[str] = orm.mapped_column(sa.String(32), nullable=False)
    meaning: orm.Mapped[str] = orm.mapped_column(
        sa.String(128), nullable=False
    )
    difficulty: orm.Mapped[str] = orm.mapped_column(
        sa.Enum(
            enums.ConceptEnum,
            values_callable=lambda x: [e.value for e in x],
            name="enum_difficulty",
            metadata=metadata,
        ),
        nullable=False,
        default=enums.ConceptEnum.HIGH.value,
    )
