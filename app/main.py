"""Main FastAPI application"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.config import settings
import secrets

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Add settings and CSRF token to templates context
def add_template_context(request: Request):
    """Add common context variables to all templates"""
    return {
        "request": request,
        "settings": settings,
        "csrf_token": secrets.token_urlsafe(32)
    }

templates.env.globals.update({"get_context": add_template_context})

# CORS middleware
ALLOWED_ORIGINS = []
if settings.is_development:
    ALLOWED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET,
    session_cookie="oauth_session",
    max_age=600,  # 10 minutes for OAuth flow
    same_site="lax",
    https_only=not settings.is_development
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # HSTS (only in production)
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# Root route - redirect to login
@app.get("/")
async def root():
    """Redirect to login page"""
    return RedirectResponse(url="/login")

# Login page route
@app.get("/login")
async def login_page(request: Request):
    """Display login page"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "csrf_token": secrets.token_urlsafe(32)}
    )

# Dashboard (requires authentication)
@app.get("/dashboard")
async def dashboard(request: Request):
    """
    Main dashboard page

    Requires authentication - redirect to appropriate team page
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # For now, show a simple dashboard
    # Later, redirect based on user's teams
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

# Admin pages (requires admin access)
@app.get("/admin/users")
async def admin_users_page(request: Request):
    """
    Admin user management page

    Requires admin access
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # Check if user is admin
    if user.get('user_level') != 'admin':
        return templates.TemplateResponse(
            "unauthorized.html",
            {"request": request, "message": "You need admin access to view this page"}
        )

    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

# Team Pages

@app.get("/teams/new-branch")
async def new_branch_page(request: Request):
    """
    New Branch Team - Branch Management page

    Requires: new_branch team access
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # Check team access
    if user.get('user_level') != 'admin':
        user_teams = user.get('teams', {})
        if 'new_branch' not in user_teams:
            return templates.TemplateResponse(
                "unauthorized.html",
                {"request": request, "message": "You need new_branch team access to view this page"}
            )

    return templates.TemplateResponse(
        "teams/new_branch.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

@app.get("/teams/legal/ppp09")
async def legal_ppp09_page(request: Request):
    """
    Legal Team - ภ.พ.09 Management page

    Requires: legal team access
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # Check team access
    if user.get('user_level') != 'admin':
        user_teams = user.get('teams', {})
        if 'legal' not in user_teams:
            return templates.TemplateResponse(
                "unauthorized.html",
                {"request": request, "message": "You need legal team access to view this page"}
            )

    return templates.TemplateResponse(
        "teams/legal_ppp09.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

@app.get("/teams/srd")
async def srd_page(request: Request):
    """
    SRD Team - Layout & Design Documents page

    Requires: srd team access
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # Check team access
    if user.get('user_level') != 'admin':
        user_teams = user.get('teams', {})
        if 'srd' not in user_teams:
            return templates.TemplateResponse(
                "unauthorized.html",
                {"request": request, "message": "You need srd team access to view this page"}
            )

    return templates.TemplateResponse(
        "teams/srd.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

@app.get("/teams/scm")
async def scm_page(request: Request):
    """
    SCM Team - Distribution Center Documents page

    Requires: scm team access
    """
    from app.middleware.session import get_session_user

    user = get_session_user(request)

    if not user:
        return RedirectResponse(url="/login")

    # Check team access
    if user.get('user_level') != 'admin':
        user_teams = user.get('teams', {})
        if 'scm' not in user_teams:
            return templates.TemplateResponse(
                "unauthorized.html",
                {"request": request, "message": "You need scm team access to view this page"}
            )

    return templates.TemplateResponse(
        "teams/scm.html",
        {
            "request": request,
            "user": user,
            "csrf_token": secrets.token_urlsafe(32)
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 50)
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📊 Version: {settings.APP_VERSION}")
    print(f"🔧 Environment: {settings.ENVIRONMENT}")
    print(f"🐛 Debug mode: {settings.DEBUG}")
    print(f"🌍 Project ID: {settings.PROJECT_ID or '(not set)'}")
    print("=" * 50)

    # Validate configuration in production
    if settings.is_production:
        try:
            settings.validate()
            print("✅ Configuration validated successfully")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            raise
    else:
        # Development warnings
        if settings.SESSION_SECRET.startswith("dev-secret"):
            print("⚠️  WARNING: Using default SESSION_SECRET. Set a custom one in .env for security!")
        if not settings.PROJECT_ID:
            print("⚠️  WARNING: PROJECT_ID not set. BigQuery and GCS will not work.")
        if not settings.GOOGLE_CLIENT_ID:
            print("⚠️  WARNING: GOOGLE_CLIENT_ID not set. OAuth login will not work.")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("=" * 50)
    print("👋 Shutting down Retail Branch Management System")
    print("=" * 50)

# Include routers
from app.routes import auth_routes, admin_routes, branch_routes, document_routes, legal_ppp09_routes

app.include_router(auth_routes.router)
app.include_router(admin_routes.router)
app.include_router(branch_routes.router)
app.include_router(document_routes.router)
app.include_router(legal_ppp09_routes.router)
