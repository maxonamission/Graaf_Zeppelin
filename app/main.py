"""Graaf Zeppelin — Causal Reasoning Platform voor Sportdeelname."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import (
    auth,
    conversations,
    explorations,
    graph,
    license,
    models,
    reasoning,
    releases,
    wizard,
)
from app.config import settings
from app.core.auth import decode_access_token
from app.core.dag_engine import CausalDAG
from app.core.rate_limit import limiter
from app.db import init_db

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Load graph model once at startup
    dag = CausalDAG.load(settings.graph_model_path)
    app.state.dag = dag
    # S12-04: derive domain display name from config or model metadata
    app.state.domain_display_name = settings.domain_display_name or dag.domain_name
    yield


app = FastAPI(
    title="Graaf Zeppelin",
    description="Causaal redeneerplatform",
    version="1.0.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── Security headers middleware (S11-02) ──────────────────────────────


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://unpkg.com https://d3js.org https://cdn.jsdelivr.net 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "frame-ancestors 'none'"
        )
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


app.add_middleware(SecurityHeadersMiddleware)


# ── CSRF protection via custom header check (S11-02) ─────────────────
# Combined with SameSite=Lax cookies, this provides double-submit defense.
# All fetch() calls from JS already include Content-Type: application/json,
# which is a custom header that cannot be set by plain HTML forms.

_CSRF_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class CSRFMiddleware(BaseHTTPMiddleware):
    """Reject state-changing requests that lack a JSON content-type.

    Browser forms send application/x-www-form-urlencoded or multipart.
    Our API only accepts application/json, so a cross-site form submission
    will be rejected here. Combined with SameSite=Lax cookies, this
    prevents CSRF attacks.
    """

    async def dispatch(self, request: Request, call_next):
        if request.method not in _CSRF_SAFE_METHODS:
            path = request.url.path
            if path.startswith("/api/"):
                content_type = request.headers.get("content-type", "")
                content_length = request.headers.get("content-length", "0")
                # Allow bodyless requests (e.g. DELETE with no payload)
                has_body = content_length != "0" and content_type != ""
                if has_body and "application/json" not in content_type:
                    from fastapi.responses import JSONResponse

                    return JSONResponse(
                        status_code=415,
                        content={"detail": "Content-Type moet application/json zijn"},
                    )
        return await call_next(request)


app.add_middleware(CSRFMiddleware)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


def _tpl_ctx(request: Request, **extra) -> dict:
    """Build template context with domain_name injected."""
    ctx = {
        "request": request,
        "domain_name": getattr(request.app.state, "domain_display_name", "Graaf Zeppelin"),
    }
    ctx.update(extra)
    return ctx


# Register API routers
app.include_router(auth.router)
app.include_router(graph.router)
app.include_router(reasoning.router)
app.include_router(releases.router)
app.include_router(license.router)
app.include_router(conversations.router)
app.include_router(wizard.router)
app.include_router(models.router)
app.include_router(explorations.router)


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
    return templates.TemplateResponse(request, "home.html", _tpl_ctx(request))


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", _tpl_ctx(request))


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "register.html", _tpl_ctx(request))


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "dashboard.html", _tpl_ctx(request, user=user))


@app.get("/graph", response_class=HTMLResponse)
async def graph_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "graph_viewer.html", _tpl_ctx(request, user=user))


@app.get("/reasoning", response_class=HTMLResponse)
async def reasoning_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "reasoning.html", _tpl_ctx(request, user=user))


@app.get("/releases", response_class=HTMLResponse)
async def releases_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "releases.html", _tpl_ctx(request, user=user))


@app.get("/verkenner", response_class=HTMLResponse)
async def wizard_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "wizard.html", _tpl_ctx(request, user=user))


@app.get("/license", response_class=HTMLResponse)
async def license_page(request: Request):
    user = _get_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "license.html", _tpl_ctx(request, user=user))
