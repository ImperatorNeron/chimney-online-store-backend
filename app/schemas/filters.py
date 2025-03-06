from fastapi import Query

from pydantic import BaseModel


class PaginationOut(BaseModel):
    offset: int
    limit: int
    total: int


class PaginationIn(BaseModel):
    offset: int = Query(default=0, ge=0, description="Page number")
    limit: int = Query(default=20, ge=1, le=40, description="Page limit")
