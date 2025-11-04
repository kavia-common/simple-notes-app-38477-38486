"""
Database configuration for the FastAPI notes backend.

This module sets up a SQLite database using SQLAlchemy. It exposes a SessionLocal
for request-scoped sessions and Base for model declarations.
"""
from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Use environment variable to allow overriding DB path, default to local SQLite file.
# IMPORTANT: Do not write .env here. The orchestrator will set env vars if provided.
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

# For SQLite, check_same_thread must be False for usage across threads.
connect_args = {"check_same_thread": False} if DB_URL.startswith("sqlite") else {}

engine = create_engine(DB_URL, connect_args=connect_args, future=True)

# Use autoflush=False and autocommit=False for explicit control in requests.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Dependency that provides a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
