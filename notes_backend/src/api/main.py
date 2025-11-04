from __future__ import annotations

from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Note
from .schemas import NoteCreate, NoteOut, NoteUpdate

openapi_tags = [
    {"name": "health", "description": "Service health and metadata"},
    {
        "name": "notes",
        "description": "CRUD operations for notes with pagination and simple search",
    },
]

app = FastAPI(
    title="Simple Notes API",
    description="A minimal FastAPI backend that provides CRUD endpoints for managing notes.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS for local development and previews
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Relaxed for demo/local usage
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables if not already present
Base.metadata.create_all(bind=engine)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# PUBLIC_INTERFACE
@app.get(
    "/",
    summary="Health Check",
    tags=["health"],
    response_model=HealthResponse,
    responses={200: {"description": "Service is healthy"}},
)
def health_check() -> HealthResponse:
    """
    Health check endpoint to verify that the service is running.
    Returns basic metadata about the service.
    """
    return HealthResponse(status="ok", service="Simple Notes API", version="0.1.0")


# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=NoteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new note",
    description="Create a note with a title and content.",
    tags=["notes"],
)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteOut:
    """
    Create a new note.
    Parameters:
      - payload: NoteCreate with title and content
    Returns:
      - The created Note as NoteOut
    """
    note = Note(title=payload.title, content=payload.content)
    try:
        db.add(note)
        db.commit()
        db.refresh(note)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create note",
        ) from e
    return NoteOut.model_validate(note)


# PUBLIC_INTERFACE
@app.get(
    "/notes",
    response_model=List[NoteOut],
    summary="List notes",
    description=(
        "List notes with basic pagination and simple search by title/content.\n"
        "Query params: page (>=1), page_size (1..100), q (optional search string)."
    ),
    tags=["notes"],
)
def list_notes(
    page: int = Query(1, ge=1, description="1-based page index"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    q: Optional[str] = Query(None, description="Search query against title and content"),
    db: Session = Depends(get_db),
) -> List[NoteOut]:
    """
    Return a paginated list of notes. Supports a simple search (?q=) across title/content.
    """
    offset = (page - 1) * page_size
    stmt = select(Note)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Note.title.ilike(like), Note.content.ilike(like)))
    stmt = stmt.order_by(Note.created_at.desc()).offset(offset).limit(page_size)

    try:
        results = db.execute(stmt).scalars().all()
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notes",
        ) from e

    return [NoteOut.model_validate(n) for n in results]


# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Get a note by ID",
    tags=["notes"],
)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteOut:
    """
    Retrieve a single note by its ID.
    """
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return NoteOut.model_validate(note)


# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=NoteOut,
    summary="Update a note by ID",
    description="Update title and/or content of a note.",
    tags=["notes"],
)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)) -> NoteOut:
    """
    Update a note. At least one of title or content must be provided.
    """
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if payload.title is None and payload.content is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one of 'title' or 'content' must be provided",
        )

    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content

    try:
        db.add(note)
        db.commit()
        db.refresh(note)
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update note",
        ) from e

    return NoteOut.model_validate(note)


# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note by ID",
    tags=["notes"],
    responses={
        204: {"description": "Note deleted (no content)"},
        404: {"description": "Note not found"},
    },
)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Response:
    """
    Delete a note by ID.

    Returns:
      - 204 No Content on successful deletion.
      - 404 if the note does not exist.
    """
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    try:
        db.delete(note)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete note",
        ) from e

    # Explicitly return an empty Response to avoid any body with 204 status.
    return Response(status_code=status.HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    # Allow running as: python -m src.api.main from project root or with PYTHONPATH set.
    import uvicorn

    uvicorn.run("src.api.main:app", host="0.0.0.0", port=3001, reload=False)
