# Calculator REST API

Simple Calculator API built with FastAPI.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn calculator.main:app --reload
```

## Test

```bash
pytest -q
```

## Endpoints

- POST /add        {"a": float, "b": float} -> {"result": float}
- POST /subtract   {"a": float, "b": float} -> {"result": float}
- POST /multiply   {"a": float, "b": float} -> {"result": float}
- POST /divide     {"a": float, "b": float} -> {"result": float} (400 on division by zero)

