import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base # Assuming import structure is correct
from main import app
from database import get_db 

# Use a specific file-based SQLite database for testing 
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- 1. FUNCTION-SCOPED DATABASE SETUP FIXTURE (The Fix!) ---
@pytest.fixture(scope="function") # Changed scope to function
def db_setup():
    """Creates tables before each test and drops them afterwards for clean isolation."""
    # This runs BEFORE every test function:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    try:
        yield
    finally:
        # This runs AFTER every test function:
        Base.metadata.drop_all(bind=engine) # Ensures clean teardown

# --- 2. OVERRIDE THE GET_DB DEPENDENCY (Cleaned) ---
def override_get_db():
    """Provides a fresh session for each dependency call, WITHOUT wiping the tables."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override to the main application instance
app.dependency_overrides[get_db] = override_get_db

# --- 3. CREATE THE TEST CLIENT FIXTURE ---
@pytest.fixture(scope="function") # Changed scope to function
def client(db_setup): # CRITICAL: This now depends on the db_setup fixture
    """A fixture to provide a test client for making requests."""
    with TestClient(app) as c:
        yield c