from fastapi import FastAPI

from app.api.routes import router
from app.database.database import Base, engine
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rate Limiting & Monitoring System"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Rate Limiter API is running"
    }