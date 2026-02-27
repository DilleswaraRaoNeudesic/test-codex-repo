E-Commerce Microservices Platform (FastAPI)

Overview
- Three microservices: `order_service`, `inventory_service`, `payment_service`
- Shared Pydantic models in `models/`
- Each service persists to its own SQLite DB
- Services communicate via REST using `httpx.AsyncClient`

Run Locally
- Install deps: `pip install -r requirements.txt`
- Start services individually:
  - `uvicorn inventory_service.main:app --port 8001`
  - `uvicorn payment_service.main:app --port 8002`
  - `uvicorn order_service.main:app --port 8000` (env: `INVENTORY_URL`, `PAYMENT_URL`)
- Or use Docker Compose: `docker-compose up --build`

Key Endpoints
- Inventory: `POST /inventory/reserve`, `POST /inventory/release`, `GET /inventory/levels`, `POST /inventory/set_stock`
- Payment: `POST /payments/charge`, `POST /payments/refund`
- Order: `POST /orders`, `GET /orders`

Failure Handling
- If inventory reservation fails, order is not created
- If payment fails after reservation, inventory is released (compensation)

Testing
- Run `pytest`
- Tests cover happy path and failure scenarios for each service

