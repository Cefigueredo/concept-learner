import pydantic


class BaseSchema(pydantic.BaseModel):
    @pydantic.validator("*", pre=True)
    def default_when_none(cls, v, field):
        if v == "":
            v = None

        if all(
            (
                getattr(field, "default", None) is not None,
                v is None,
            )
        ):
            return field.default
        else:
            return v
