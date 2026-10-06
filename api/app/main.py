from pathlib import Path

from fastapi import FastAPI
from fastapi.routing import APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from app.api.notes import router as notes_router
from app.core.database import Base, engine

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ApiMessage(BaseModel):
    message: str


class ApiStatus(BaseModel):
    status: str


api_router = APIRouter(prefix="/api")


@api_router.get("/", response_model=ApiMessage)
def api_root():
    return {"message": "Hello from FastAPI API"}


@api_router.get("/status", response_model=ApiStatus)
def api_status():
    return {"status": "ok"}


APP_ROOT_PATH = "/s113321018"

app = FastAPI(
    title="WebUI Lab",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    root_path=APP_ROOT_PATH,
)
app.include_router(api_router)
app.include_router(notes_router)

Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def restrict_public_access(request, call_next):
    root_path = request.scope.get("root_path", "")
    path = request.url.path

    if root_path and path.startswith(root_path):
        path = path[len(root_path):] or "/"

    if path.startswith("/api"):
        return await call_next(request)

    if path in {"/", ""}:
        return await call_next(request)

    suffix = Path(path).suffix.lower()
    if suffix in {".html", ".css"}:
        return await call_next(request)

    return FileResponse(str(PROJECT_ROOT / "index.html"), status_code=403)


app.mount("/", StaticFiles(directory=str(PROJECT_ROOT), html=True), name="public")
