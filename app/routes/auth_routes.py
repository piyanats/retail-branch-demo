"""Authentication routes"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.responses import Response
from app.services.oauth_service import oauth, validate_email_domain
from app.services.bigquery_service import bigquery_service
from app.middleware.session import create_session, get_session_user
from app.middleware.auth import get_current_user
from app.config import settings
from app.main import templates
import secrets

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/login")
async def login(request: Request):
    """
    Initiate OAuth login flow

    Redirects user to Google OAuth consent screen
    """
    redirect_uri = str(request.url_for('auth_callback'))
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback")
async def auth_callback(request: Request):
    """
    OAuth callback handler

    Handles redirect from Google after user authorization
    Validates user against database and creates session
    """
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')

        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        # Validate email domain if restrictions are configured
        if not validate_email_domain(email):
            return templates.TemplateResponse(
                "unauthorized.html",
                {
                    "request": request,
                    "email": email,
                    "csrf_token": secrets.token_urlsafe(32),
                    "reason": "Email domain not allowed"
                }
            )

        # Check if user exists in database
        query = f"""
            SELECT
                u.user_id,
                u.email,
                u.name,
                u.user_level,
                u.is_active
            FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.users` u
            WHERE u.email = '{email}'
              AND u.is_active = true
        """

        results = bigquery_service.query(query)

        if not results:
            # User not authorized
            return templates.TemplateResponse(
                "unauthorized.html",
                {
                    "request": request,
                    "email": email,
                    "csrf_token": secrets.token_urlsafe(32),
                    "reason": "User not found in system"
                }
            )

        user = results[0]

        # Get user teams
        teams_query = f"""
            SELECT
                ut.team_name,
                ut.role
            FROM `{settings.PROJECT_ID}.{settings.DATASET_ID}.user_teams` ut
            WHERE ut.user_id = '{user['user_id']}'
        """

        user_teams = bigquery_service.query(teams_query)

        # Update last login
        update_query = f"""
            UPDATE `{settings.PROJECT_ID}.{settings.DATASET_ID}.users`
            SET last_login = CURRENT_TIMESTAMP()
            WHERE user_id = '{user['user_id']}'
        """
        bigquery_service.execute(update_query)

        # Log login activity
        from datetime import datetime
        import uuid
        log_data = {
            'log_id': str(uuid.uuid4()),
            'user_id': user['user_id'],
            'user_email': user['email'],
            'action_type': 'login',
            'resource_type': 'auth',
            'resource_id': None,
            'action_detail': '{"method": "google_oauth"}',
            'ip_address': request.client.host,
            'user_agent': request.headers.get('user-agent', 'unknown'),
            'status': 'success',
            'error_message': None,
            'created_at': datetime.now().isoformat()
        }
        bigquery_service.insert_rows('audit_logs', [log_data])

        # Create session
        session_data = {
            'user_id': user['user_id'],
            'email': user['email'],
            'name': user['name'],
            'user_level': user['user_level'],
            'picture': picture,
            'teams': user_teams
        }

        session_token = create_session(session_data)

        # Redirect to dashboard
        response = RedirectResponse(url="/dashboard", status_code=302)

        # Set secure session cookie
        response.set_cookie(
            key="session",
            value=session_token,
            httponly=True,
            secure=not settings.is_development,  # HTTPS only in production
            samesite='lax',
            max_age=settings.SESSION_MAX_AGE,
            path='/'
        )

        return response

    except Exception as e:
        # Log failed login
        print(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@router.post("/logout")
@router.get("/logout")
async def logout():
    """
    Logout user

    Clears session cookie and redirects to login page
    """
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session", path='/')
    return response

@router.get("/me")
async def get_current_user_info(current_user: dict = get_current_user):
    """
    Get current user information

    Returns user data from session

    Requires authentication
    """
    return {
        "success": True,
        "user": current_user
    }

@router.get("/check")
async def check_auth(request: Request):
    """
    Check if user is authenticated

    Returns authentication status without requiring login
    """
    user = get_session_user(request)

    return {
        "authenticated": user is not None,
        "user": user if user else None
    }
