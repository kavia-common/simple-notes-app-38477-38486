"""
Pydantic schemas for the notes backend.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Short title of the note")
    content: str = Field(..., min_length=1, description="Content/body of the note")


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Updated title")
    content: Optional[str] = Field(None, min_length=1, description="Updated content")


class NoteOut(BaseModel):
    id: int = Field(..., description="Unique identifier of the note")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last updated timestamp (UTC)")

    class Config:
        from_attributes = True  # Allow ORM objects
