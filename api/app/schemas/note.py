from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str | None = None


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
