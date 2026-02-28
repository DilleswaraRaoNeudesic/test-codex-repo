# Calculator REST API

Simple Calculator REST API built with FastAPI.

## Setup

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
uvicorn calculator.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for interactive docs.

## Test

```bash
pytest -q
```

