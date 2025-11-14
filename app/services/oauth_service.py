"""Google OAuth 2.0 service"""

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.requests import Request
from app.config import settings

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

async def get_authorization_url(request: Request, redirect_uri: str) -> str:
    """
    Generate OAuth authorization URL

    Args:
        request: Starlette request object
        redirect_uri: Callback URL after authorization

    Returns:
        str: Authorization URL to redirect user to
    """
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def get_user_info(request: Request) -> dict:
    """
    Get user information from OAuth callback

    Args:
        request: Starlette request object with authorization code

    Returns:
        dict: User information from Google

    Raises:
        OAuthError: If authorization fails
    """
    try:
        # Exchange authorization code for access token
        token = await oauth.google.authorize_access_token(request)

        # Get user info from token
        user_info = token.get('userinfo')

        if not user_info:
            raise OAuthError('Failed to get user information from Google')

        return {
            'email': user_info.get('email'),
            'name': user_info.get('name'),
            'picture': user_info.get('picture'),
            'email_verified': user_info.get('email_verified', False)
        }

    except Exception as e:
        raise OAuthError(f'OAuth authentication failed: {str(e)}')

def validate_email_domain(email: str) -> bool:
    """
    Validate email domain against allowed domains

    Args:
        email: Email address to validate

    Returns:
        bool: True if email domain is allowed or no restrictions, False otherwise
    """
    if not settings.ALLOWED_EMAIL_DOMAINS:
        # No domain restrictions
        return True

    domain = email.split('@')[1] if '@' in email else ''
    return domain in settings.ALLOWED_EMAIL_DOMAINS
