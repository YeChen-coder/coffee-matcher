# Coffee Matcher API Template

This repository provides a FastAPI template for a Coffee Matcher application built with SQLModel and SQLite. The layout mirrors a typical production-ready FastAPI project, separating models, schemas, CRUD logic, and API routers.

## Project Layout

```
coffee-matcher/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/        # Route handlers
│   │       └── router.py          # API router
│   ├── core/                      # Settings and configuration
│   ├── crud/                      # Database operations
│   ├── db/                        # Session and engine management
│   ├── models/                    # SQLModel table definitions
│   ├── schemas/                   # Pydantic/SQLModel schemas
│   └── main.py                    # FastAPI application factory
├── scripts/
│   └── init_db.py                 # Sample data loader
├── requirements.txt
└── README.md
```

## Getting Started

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create the SQLite database and seed sample data (optional)**
   ```bash
   python -m scripts.init_db
   ```

3. **Run the API**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Explore the docs**
   Visit http://localhost:8000/docs to interact with the generated OpenAPI documentation.

## Notes

- Configuration is centralized in `app/core/config.py`. Override defaults via environment variables or a local `.env` file.
- Database tables are created automatically on application startup.
- The template includes CRUD endpoints for users, venues, time slots, match requests, and user preferences under `/api/v1/`.

Feel free to adapt this template to your specific business rules and front-end requirements.
