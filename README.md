# Coffee Matcher

A backend service for coordinating coffee meetings between users, built with modern Python tooling and designed for scalability.

**Live Demo:** http://3.99.190.20/

Currently deployed on AWS EC2 (Ubuntu) using systemd for process management.

## Tech Stack

**Framework & Runtime**
- FastAPI 0.104.1 - Async web framework with automatic OpenAPI documentation
- Uvicorn 0.24.0 - ASGI server with automatic reload during development

**Data Layer**
- SQLModel 0.0.8 - Combines SQLAlchemy ORM with Pydantic validation
- SQLite - Embedded relational database with zero-configuration deployment

**Validation & Processing**
- Pydantic - Type validation and settings management via BaseSettings
- email-validator 2.1.0 - RFC-compliant email validation
- python-multipart 0.0.6 - Handles multipart form data parsing

## Architecture

The application follows a layered architecture pattern separating concerns across distinct modules:

- **API Layer** (`app/api/v1/endpoints/`) - Request handlers organized by resource
- **Business Logic** (`app/crud/`) - Database operations encapsulated in reusable functions
- **Data Models** (`app/models/`) - SQLModel table definitions with bidirectional relationships
- **Schemas** (`app/schemas/`) - Request/response contracts validated via Pydantic
- **Configuration** (`app/core/`) - Centralized settings with environment variable support
- **Database** (`app/db/`) - Session management and connection lifecycle

## Data Model

The schema supports the core matching workflow with five primary entities:

**User**
- Profile information (name, email, bio, location)
- Optional AI analysis metadata stored as JSON
- Relationships: timeslots, match requests (sent/received), preferences, venues

**MatchRequest**
- Tracks meeting proposals between users
- Status tracking: pending/confirmed/declined
- Links requester, target user, venue, and timeslot
- Includes proposed time and optional message

**TimeSlot**
- User availability windows defined by start/end times
- Status field for availability management
- Foreign key relationship to owning user

**Venue**
- Meeting locations with type classification (coffee/restaurant)
- Includes price range, location, description
- Optional creator tracking via user relationship

**UserPreference**
- Stores typed preference data as key-value pairs
- Confidence scoring (1-10 scale)
- Supports multiple preference types per user

### Relationships

The data model implements several important patterns:

- Self-referential many-to-many on User via MatchRequest (requester/target)
- One-to-many from User to TimeSlot for availability management
- Many-to-one from MatchRequest to Venue for location selection
- One-to-many from User to UserPreference for personalization

All foreign keys are indexed for query performance, and bidirectional relationships use SQLModel's `Relationship` with explicit foreign key configuration to avoid ambiguity.

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

## Deployment

The application runs as a systemd service on production servers.

**Service Management**
```bash
# Start the service
sudo systemctl start coffee-matcher.service

# Enable auto-restart on boot
sudo systemctl enable coffee-matcher.service

# Check service status
sudo systemctl status coffee-matcher.service
```

**Log Inspection**
```bash
# View recent logs
sudo journalctl -xeu coffee-matcher.service --since "10 minutes ago"

# Follow logs in real-time
sudo journalctl -xeu coffee-matcher.service -f

# View logs from specific time range
sudo journalctl -xeu coffee-matcher.service --since "2025-01-01" --until "2025-01-02"
```

The systemd service configuration should be placed in `/etc/systemd/system/coffee-matcher.service` and must be enabled during initial deployment to ensure the service restarts automatically after system reboots.


