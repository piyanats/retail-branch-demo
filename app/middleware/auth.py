"""Authentication and authorization middleware"""

from fastapi import Depends, HTTPException, Request
from app.middleware.session import require_session
from typing import List, Optional

async def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user

    Args:
        request: FastAPI request object

    Returns:
        dict: Current user data

    Raises:
        HTTPException: If user is not authenticated
    """
    return require_session(request)

async def get_current_admin_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Require admin level access

    Args:
        current_user: Current authenticated user

    Returns:
        dict: User data if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.get('user_level') != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required. You don't have permission to access this resource."
        )
    return current_user

def require_team_access(team: str, min_role: str = 'viewer'):
    """
    Require access to specific team with minimum role

    Args:
        team: Team name (new_branch, legal, srd, scm)
        min_role: Minimum required role (viewer, editor, manager)

    Returns:
        Dependency function for FastAPI

    Example:
        @router.get("/api/legal/ppp09")
        async def get_ppp09(user: dict = Depends(require_team_access('legal', 'viewer'))):
            pass
    """
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        # Admin has access to everything
        if current_user.get('user_level') == 'admin':
            return current_user

        # Check team membership
        user_teams = current_user.get('teams', [])

        # Find team data
        team_data = None
        for t in user_teams:
            if t.get('team_name') == team:
                team_data = t
                break

        if not team_data:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: You are not a member of the {team} team."
            )

        # Check role level
        role_hierarchy = ['viewer', 'editor', 'manager']
        user_role = team_data.get('role', 'viewer')

        try:
            user_role_level = role_hierarchy.index(user_role)
            required_role_level = role_hierarchy.index(min_role)
        except ValueError:
            raise HTTPException(
                status_code=403,
                detail=f"Invalid role configuration."
            )

        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied: {min_role} role required. You have {user_role} role."
            )

        return current_user

    return dependency

def require_any_team_access(teams: List[str], min_role: str = 'viewer'):
    """
    Require access to at least one of the specified teams

    Args:
        teams: List of team names
        min_role: Minimum required role

    Returns:
        Dependency function for FastAPI

    Example:
        @router.get("/api/documents")
        async def get_documents(
            user: dict = Depends(require_any_team_access(['legal', 'srd']))
        ):
            pass
    """
    async def dependency(current_user: dict = Depends(get_current_user)) -> dict:
        # Admin has access to everything
        if current_user.get('user_level') == 'admin':
            return current_user

        # Check if user has access to any of the teams
        user_teams = current_user.get('teams', [])
        role_hierarchy = ['viewer', 'editor', 'manager']

        for team in teams:
            for user_team in user_teams:
                if user_team.get('team_name') == team:
                    user_role = user_team.get('role', 'viewer')

                    try:
                        user_role_level = role_hierarchy.index(user_role)
                        required_role_level = role_hierarchy.index(min_role)

                        if user_role_level >= required_role_level:
                            return current_user
                    except ValueError:
                        continue

        raise HTTPException(
            status_code=403,
            detail=f"Access denied: You need access to one of these teams: {', '.join(teams)}"
        )

    return dependency

def get_user_teams(current_user: dict) -> List[str]:
    """
    Get list of team names user has access to

    Args:
        current_user: Current user data

    Returns:
        List of team names
    """
    if current_user.get('user_level') == 'admin':
        return ['new_branch', 'legal', 'srd', 'scm']

    user_teams = current_user.get('teams', [])
    return [t.get('team_name') for t in user_teams if t.get('team_name')]

def can_edit_resource(current_user: dict, team: str) -> bool:
    """
    Check if user can edit resources in a team

    Args:
        current_user: Current user data
        team: Team name

    Returns:
        bool: True if user can edit, False otherwise
    """
    if current_user.get('user_level') == 'admin':
        return True

    user_teams = current_user.get('teams', [])

    for user_team in user_teams:
        if user_team.get('team_name') == team:
            role = user_team.get('role', 'viewer')
            return role in ['editor', 'manager']

    return False

def can_delete_resource(current_user: dict, team: str) -> bool:
    """
    Check if user can delete resources in a team

    Args:
        current_user: Current user data
        team: Team name

    Returns:
        bool: True if user can delete, False otherwise
    """
    if current_user.get('user_level') == 'admin':
        return True

    user_teams = current_user.get('teams', [])

    for user_team in user_teams:
        if user_team.get('team_name') == team:
            role = user_team.get('role', 'viewer')
            return role == 'manager'

    return False
