from fastapi import FastAPI
from src.routers import box_router, feedback_router
from src.db.database import init_db

app = FastAPI()

app.include_router(box_router.router)
app.include_router(feedback_router.router)

# Create tables at import time so TestClient/pytest works reliably.
# (init_db uses SQLAlchemy models metadata, populated when routers/models are imported above)
init_db()

@app.get("/health")
def health():
    return {"status": "ok"}