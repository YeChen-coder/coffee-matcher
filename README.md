# Coffee Matcher

## Project Layout

```
coffee-matcher/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/         # Route handlers
│   │       └── router.py          # API router
│   ├── core/                      # Settings and configuration
│   ├── crud/                      # Database operations
│   ├── db/                        # Session and engine management
│   ├── models/                    # SQLModel table definitions
│   ├── schemas/                   # Pydantic/SQLModel schemas
│   └── main.py                    # 
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
   Visit http://localhost:8000/docs
