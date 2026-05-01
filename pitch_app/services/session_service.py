"""
Session management service for materials selection
"""
import logging
from typing import List
from fastapi import Request

logger = logging.getLogger(__name__)

SESSION_MATERIALS_KEY = "selected_materials"
SESSION_USER_KEY = "user_logged"


def get_selected_materials(request: Request) -> List[str]:
    """
    Get list of selected materials from session
    """
    items = request.session.get(SESSION_MATERIALS_KEY, [])
    if not isinstance(items, list):
        return []

    cleaned = []
    seen = set()

    for item in items:
        if isinstance(item, str):
            value = item.strip()
            if value and value not in seen:
                seen.add(value)
                cleaned.append(value)

    return cleaned


def set_selected_materials(request: Request, items: List[str]) -> List[str]:
    """
    Set the list of selected materials in session
    Returns the cleaned list
    """
    cleaned = []
    seen = set()

    for item in items:
        if isinstance(item, str):
            value = item.strip()
            if value and value not in seen:
                seen.add(value)
                cleaned.append(value)

    request.session[SESSION_MATERIALS_KEY] = cleaned
    logger.debug(f"Set selected materials: {len(cleaned)} items")
    return cleaned


def add_selected_material(request: Request, filename: str) -> List[str]:
    """
    Add a material to the selected list
    Returns the updated list
    """
    current = get_selected_materials(request)
    value = (filename or "").strip()

    if value and value not in current:
        current.append(value)
        logger.debug(f"Added material to selection: {value}")

    return set_selected_materials(request, current)


def remove_selected_material(request: Request, filename: str) -> List[str]:
    """
    Remove a material from the selected list
    Returns the updated list
    """
    value = (filename or "").strip()
    current = [item for item in get_selected_materials(request) if item != value]
    logger.debug(f"Removed material from selection: {value}")
    return set_selected_materials(request, current)


def clear_selected_materials(request: Request) -> List[str]:
    """
    Clear all selected materials
    Returns empty list
    """
    request.session[SESSION_MATERIALS_KEY] = []
    logger.debug("Cleared all selected materials")
    return []


def is_user_logged(request: Request) -> bool:
    """
    Check if user is logged in
    """
    return bool(request.session.get(SESSION_USER_KEY))


def get_user_info(request: Request) -> dict:
    """
    Get logged user information from session
    """
    if not is_user_logged(request):
        return {}
    
    return {
        "id": request.session.get("user_id"),
        "name": request.session.get("user_name"),
        "role": request.session.get("user_role"),
    }


def set_user_session(request: Request, user_id: int, name: str, role: str):
    """
    Set user session data after successful login
    """
    request.session[SESSION_USER_KEY] = True
    request.session["user_id"] = user_id
    request.session["user_name"] = name
    request.session["user_role"] = role
    logger.info(f"User session created: {name} (ID: {user_id}, Role: {role})")


def clear_user_session(request: Request):
    """
    Clear user session (logout)
    """
    user_name = request.session.get("user_name", "Unknown")
    request.session.clear()
    logger.info(f"User session cleared: {user_name}")

# Made with Bob
