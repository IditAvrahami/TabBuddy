import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.drug import router as drug_router
from backend.api.meal import router as meal_router
from backend.database import Base, engine

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI(title="TabBuddy API", version="1.0.0")

# Create PostgreSQL tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("PostgreSQL tables created successfully")
except Exception as e:
    logger.error("Failed to create PostgreSQL tables: %s", e)
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drug_router)
app.include_router(meal_router)
logger.info("TabBuddy API started successfully")

