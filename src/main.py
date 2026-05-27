from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from src.routers import box_router, feedback_router
from src.routers.auth_router import router as auth_router
from src.db.database import init_db

app = FastAPI()

app.include_router(box_router.router)
app.include_router(feedback_router.router)
app.include_router(auth_router)

# Create tables at import time so TestClient/pytest works reliably.
# (init_db uses SQLAlchemy models metadata, populated when routers/models are imported above)
init_db()

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse(
        """
        <html>
            <head>
                <title>Anonymous Feedback API</title>
            </head>
            <body>
                <h1>Anonymous Feedback API</h1>
                <p>Перейдите на страницу документации API, чтобы увидеть доступные команды.</p>
                <ul>
                    <li><a href="/docs">Swagger UI</a> — браузерная документация OpenAPI</li>
                    <li><a href="/redoc">ReDoc</a> — альтернативная документация OpenAPI</li>
                </ul>
                <p>Схема OpenAPI доступна по адресу <code>/openapi.json</code>.</p>
            </body>
        </html>
        """
    )

@app.get("/health")
def health():
    return {"status": "ok"}