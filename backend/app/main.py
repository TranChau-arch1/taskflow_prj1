import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv

from app.database import engine, Base, get_db
from app.routers import tasks, chat
from app.schemas import HealthResponse

load_dotenv()

# Create tables automatically upon startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TaskFlow REST API",
    description="API quản lý công việc (Task Management) xây dựng bằng FastAPI, SQLAlchemy và PostgreSQL/SQLite",
    version="1.0.0"
)

# CORS configuration
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins_raw.strip() == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tasks.router)
app.include_router(chat.router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Chào mừng đến với TaskFlow API! 🚀",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connectivity
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "online",
        "database": db_status,
        "version": "1.0.0"
    }
