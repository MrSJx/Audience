# Phase 8 Persistence

Phase 8 stores generated reports in SQLite so they can be retrieved later.

## Implemented persistence

- SQLite database initialization on app startup
- `reports` table for metadata and stored JSON payloads
- report save on every analysis request
- report retrieval by id
- recent report listing

Files involved:

- [backend/app/core/database.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/core/database.py>)
- [backend/app/services/repository_service.py](</C:/Users/swapn/OneDrive/Documents/GitHub/Audience/backend/app/services/repository_service.py>)
