from pathlib import Path

from fastapi import FastAPI
from fastapi.routing import APIRouter
from pydantic import BaseModel
from starlette.responses import FileResponse, Response
from starlette.staticfiles import StaticFiles

from app.api.notes import router as notes_router
from app.core.database import Base, engine

# main.py 位於 api/app/；往上兩層就是前端檔案所在的 webui-lab 專案根目錄。
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class ApiMessage(BaseModel):
    message: str


class ApiStatus(BaseModel):
    status: str


# 將一般 API 集中在 /api 路徑下，避免和前端頁面路徑混在一起。
api_router = APIRouter(prefix="/api")


@api_router.get("/", response_model=ApiMessage)
def api_root():
    return {"message": "Hello from FastAPI API"}


@api_router.get("/status", response_model=ApiStatus)
def api_status():
    return {"status": "ok"}


# 部署時網站掛載在 /s113321018；本機直接執行時仍可從 / 存取。
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

# 根據已註冊的 SQLAlchemy model 建立尚未存在的資料表。
Base.metadata.create_all(bind=engine)


@app.middleware("http")
async def restrict_public_access(request, call_next):
    # 部署在反向代理後方時，先移除代理加上的路徑前綴，統一用應用程式內部路徑判斷。
    root_path = request.scope.get("root_path", "")
    path = request.url.path

    if root_path and path.startswith(root_path):
        path = path[len(root_path):] or "/"

    # API 請求交由 FastAPI 路由處理，不套用前端靜態檔案的存取限制。
    if path.startswith("/api"):
        return await call_next(request)

    # 首頁可公開瀏覽。
    if path in {"/", ""}:
        return await call_next(request)

    # 有些瀏覽器會自動詢問 favicon.ico；目前圖示使用 SVG，舊式請求以 204 正常結束。
    if path == "/favicon.ico":
        return Response(status_code=204)

    # 只放行專案根目錄中確實存在的檔案，讓 CSS、JavaScript、JSON 和圖片可供前端載入。
    suffix = Path(path).suffix.lower()
    if suffix:
        candidate = PROJECT_ROOT / path.lstrip("/")
        if candidate.exists() and not candidate.is_dir():
            return await call_next(request)

    # 不存在或未允許的路徑回傳 403，避免公開瀏覽專案中的其他內容。
    return FileResponse(str(PROJECT_ROOT / "index.html"), status_code=403)


# 將專案根目錄作為靜態網站根目錄，並讓根路徑自動提供 index.html。
app.mount("/", StaticFiles(directory=str(PROJECT_ROOT), html=True), name="public")
