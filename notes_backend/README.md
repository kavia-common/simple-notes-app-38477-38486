# notes_backend

FastAPI Notes API for the Simple Notes App.

How to run locally (developer machine):

1) Create a virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate

2) Install dependencies
   pip install -r requirements.txt

3) Run the API
   uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --app-dir notes_backend

Notes:
- In the CI/preview environment the platform manages startup on port 3001.
- The app module is available at src.api.main:app.
- Default DB is SQLite at sqlite:///./notes.db (file notes.db in backend working dir).
