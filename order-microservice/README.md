# Order Microservice

A FastAPI microservice for order management, with inventory checks via HTTP to an external Inventory microservice.

## Features
- Create and list orders
- Checks inventory before order creation (calls Inventory microservice)

## Quickstart

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API
- `POST /orders/` — Create order (checks inventory)
- `GET /orders/` — List orders

## Inventory Service
- This service expects an Inventory microservice with endpoints:
  - `GET /inventory/{product_id}` (returns `{ "quantity": int }`)
  - `POST /inventory/reduce` (body: `{ "product_id": str, "quantity": int }`)
- Update the `base_url` in `app/services/inventory_service.py` to match your Inventory service location.
