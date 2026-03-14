"""Graaf Zeppelin — Causal Reasoning Platform voor Sportdeelname."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api import auth, conversations, graph, license, reasoning, releases, wizard
from app.config import settings
from app.core.auth import decode_access_token
from app.core.dag_engine import CausalDAG
from app.db import init_db

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Load graph model once at startup
    app.state.dag = CausalDAG.load(settings.graph_model_path)
    yield


app = FastAPI(
    title="Graaf Zeppelin",
    description="Causaal redeneerplatform voor sportdeelname",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Register API routers
app.include_router(auth.router)
app.include_router(graph.router)
app.include_router(reasoning.router)
app.include_router(releases.router)
app.include_router(license.router)
app.include_router(conversations.router)
app.include_router(wizard.router)


def _get_user_from_cookie(request: Request) -> dict | None:
    """Try to extract user info from JWT cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    return decode_access_token(token)


# ── Page Routes ──────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = _get_user_from_cookie(request)
    if user:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "user": user}
    )


@app.get("/graph", response_class=HTMLResponse)
async def graph_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "graph_viewer.html", {"request": request, "user": user}
    )


@app.get("/reasoning", response_class=HTMLResponse)
async def reasoning_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "reasoning.html", {"request": request, "user": user}
    )


@app.get("/releases", response_class=HTMLResponse)
async def releases_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "releases.html", {"request": request, "user": user}
    )


@app.get("/verkenner", response_class=HTMLResponse)
async def wizard_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "wizard.html", {"request": request, "user": user}
    )


@app.get("/license", response_class=HTMLResponse)
async def license_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(
        "license.html", {"request": request, "user": user}
    )
