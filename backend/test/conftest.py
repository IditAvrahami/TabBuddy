import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set DATABASE_URL before importing backend modules
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test")

from backend.database import Base, get_db
from backend.models import DrugORM
from backend.main import app

@pytest.fixture(scope="session")
def test_db_url():
    """Get test database URL from environment or use default"""
    return os.getenv("TEST_DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5434/tabbuddy_test")

@pytest.fixture(scope="session")
def test_engine(test_db_url):
    """Create test database engine"""
    engine = create_engine(test_db_url)
    return engine

@pytest.fixture(scope="session")
def test_session_factory(test_engine):
    """Create test session factory"""
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(autouse=True)
def setup_test_db(test_engine):
    """Set up test database tables"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_session_factory):
    """Create database session for tests"""
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_client(test_session_factory):
    """Create test client with overridden database dependency"""
    def override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def clean_db_between_tests(test_session_factory):
    """Clean database between tests but keep tables"""
    # Create a new session for cleanup
    session = test_session_factory()
    try:
        # Clear all data but keep table structure - only if table exists
        try:
            session.query(DrugORM).delete()
            session.commit()
        except Exception:
            # Table doesn't exist yet, that's ok
            session.rollback()
        yield
        # Clean up after test - only if table exists
        try:
            session.query(DrugORM).delete()
            session.commit()
        except Exception:
            # Table might not exist, that's ok
            session.rollback()
    finally:
        session.close()

def get_db_count(session):
    """Helper to count drugs in database"""
    return session.query(DrugORM).count()

def get_db_drug(session, name):
    """Helper to get drug from database by name"""
    return session.query(DrugORM).filter(DrugORM.name == name).first()
