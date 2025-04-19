from pydantic import BaseModel, Field


class BaseFields(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)


class ReadLikeSchema(BaseFields):
    id: int = Field(..., gt=0)  # noqa


class CreateLikeSchema(BaseFields):
    pass
