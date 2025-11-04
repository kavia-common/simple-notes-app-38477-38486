# simple-notes-app-38477-38486

Backend: FastAPI Notes API (notes_backend)

This backend provides RESTful CRUD endpoints for a simple notes application, with SQLite persistence via SQLAlchemy.

## Quick start

- Python >= 3.10 recommended
- Install dependencies:
  pip install -r notes_backend/requirements.txt

- Run the API (default preview port 3001 is already managed by the environment):
  uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --app-dir notes_backend

OpenAPI docs: http://localhost:3001/docs

Note: Preview/start process may be managed by the platform. Do not modify preview management.

## Environment variables

- DATABASE_URL (optional): SQLAlchemy connection string.
  Default: sqlite:///./notes.db (created under working directory of the process).

Create a .env file if needed. Do not commit secrets.
An example file is provided at notes_backend/.env.example.

## API

Base URL: http://localhost:3001

- Health
  GET /
  200: {"status":"ok","service":"Simple Notes API","version":"0.1.0"}

- Create Note
  POST /notes
  body:
    {"title":"My Note","content":"Content goes here"}
  201: {"id":1,"title":"My Note","content":"Content goes here","created_at":"...","updated_at":"..."}

  curl:
    curl -s -X POST http://localhost:3001/notes \
      -H "Content-Type: application/json" \
      -d '{"title":"My Note","content":"Content goes here"}' | jq .

- List Notes (pagination + search)
  GET /notes?page=1&page_size=10&q=term

  curl:
    curl -s "http://localhost:3001/notes?page=1&page_size=5&q=note" | jq .

- Get Note
  GET /notes/{id}

  curl:
    curl -s http://localhost:3001/notes/1 | jq .

- Update Note
  PUT /notes/{id}
  body:
    {"title":"Updated","content":"New content"}

  curl:
    curl -s -X PUT http://localhost:3001/notes/1 \
      -H "Content-Type: application/json" \
      -d '{"title":"Updated","content":"New content"}' | jq .

- Delete Note
  DELETE /notes/{id}

  curl:
    curl -s -X DELETE http://localhost:3001/notes/1 -i

## Notes

- CORS is enabled for local development.
- Basic validation and error handling are in place.
- SQLite database file is created automatically when the service runs.
