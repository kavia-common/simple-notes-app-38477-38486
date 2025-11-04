"""
SQLAlchemy ORM models for the notes backend.
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text, Index

from .database import Base


def utcnow() -> datetime:
    # Use timezone-aware timestamps for consistency
    return datetime.now(timezone.utc)


class Note(Base):
    """
    Represents a note entity.

    Fields:
      - id: Primary key
      - title: Short title (required, up to 255 chars)
      - content: Body text (required)
      - created_at: Creation timestamp (UTC)
      - updated_at: Last update timestamp (UTC)
    """
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    __table_args__ = (
        # Composite index to speed up simple search on title/content for LIKE queries
        Index("ix_notes_title_content", "title", "content"),
    )
