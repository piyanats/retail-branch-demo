"""Main FastAPI application"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
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

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("=" * 50)
    print("👋 Shutting down Retail Branch Management System")
    print("=" * 50)

# Include routers (will be added in Phase 2)
# from app.routes import auth_routes
# app.include_router(auth_routes.router)
