# Testing Guide

## Prerequisites

1. **Activate Virtual Environment:**
   ```powershell
   .\.vev\Scripts\activate.bat
   ```

2. **Install Dependencies:**
   ```powershell
   pip install -r backend/requirements.txt
   ```

3. **Docker Installed:**
   - Make sure Docker is running on your system

## Running Tests

### Option 1: Automated (Recommended)
```powershell
python run_tests.py
```

### Option 2: Manual
```powershell
# Start test database
python start_test_db.py

# Run tests
pytest -v backend/test/api/drug/test_drug_api.py

# Stop test database
python start_test_db.py stop
```

### Option 3: Quick Test (if test DB already running)
```powershell
pytest -v backend/test/api/drug/test_drug_api.py
```

## Test Database

- **Port:** 5434 (to avoid conflicts with main DB on 5432)
- **Database:** `tabbuddy_test`
- **User:** `postgres`
- **Password:** `postgres`
- **URL:** `postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test`

## What Tests Verify

✅ **Database State Verification:**
- Drug count changes after add/delete operations
- Data persistence in PostgreSQL
- API responses match database state
- Failed operations don't corrupt database

✅ **API Endpoints:**
- `POST /drug` - Add drug with validation
- `GET /drug` - Retrieve all drugs
- `PUT /drug/{name}` - Update existing drug
- `DELETE /drug/{name}` - Remove drug

✅ **Error Handling:**
- Duplicate drug prevention
- Non-existent drug handling
- Database transaction safety

## Troubleshooting

**Docker Issues:**
- Ensure Docker Desktop is running
- Check if port 5434 is available
- Try: `docker ps` to see running containers

**Database Connection:**
- Test database starts automatically
- Wait for "PostgreSQL test database is ready!" message
- Check logs for connection errors

**Test Failures:**
- Each test gets a fresh database
- Tests run in isolation
- Check that all dependencies are installed
