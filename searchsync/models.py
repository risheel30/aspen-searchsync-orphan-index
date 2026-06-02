from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str = ""
    price: float = 0.0
    tags: List[str] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[List[str]] = None


class BulkUpsert(BaseModel):
    items: List[ProductCreate]
