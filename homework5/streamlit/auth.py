"""
Authentication module for password-based login with persistent sessions
Handles password hashing, session tokens, and cookie management
"""

import bcrypt
import secrets
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import extra_streamlit_components as stx

# Cookie manager singleton
_cookie_manager = None

def get_cookie_manager():
    """Get the cookie manager instance (singleton pattern to avoid cache warnings)"""
    global _cookie_manager
    if _cookie_manager is None:
        _cookie_manager = stx.CookieManager()
    return _cookie_manager

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        password_hash: Stored hash to compare against
        
    Returns:
        True if password matches
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

def generate_session_token() -> str:
    """
    Generate a secure random session token
    
    Returns:
        64-character hexadecimal token
    """
    return secrets.token_hex(32)

def set_auth_cookie(callsign: str, session_token: str, days: int = 30):
    """
    Set authentication cookie in browser
    
    Args:
        callsign: User's callsign
        session_token: Secure session token
        days: Number of days until cookie expires
    """
    cookie_manager = get_cookie_manager()
    
    # Set cookie with expiry (using unique key per invocation)
    cookie_manager.set(
        'dx_session_token',
        session_token,
        expires_at=datetime.now() + timedelta(days=days),
        key=f'set_token_{hash(session_token) % 10000}'
    )
    
    cookie_manager.set(
        'dx_callsign',
        callsign,
        expires_at=datetime.now() + timedelta(days=days),
        key=f'set_callsign_{hash(callsign) % 10000}'
    )

def get_auth_cookie() -> Optional[Dict[str, str]]:
    """
    Get authentication data from cookie
    
    Returns:
        Dictionary with 'callsign' and 'session_token' or None
    """
    cookie_manager = get_cookie_manager()
    
    try:
        session_token = cookie_manager.get('dx_session_token')
        callsign = cookie_manager.get('dx_callsign')
        
        if session_token and callsign:
            return {
                'callsign': callsign,
                'session_token': session_token
            }
    except:
        pass
    
    return None

def clear_auth_cookie():
    """Clear authentication cookies"""
    cookie_manager = get_cookie_manager()
    
    try:
        cookie_manager.delete('dx_session_token')
        cookie_manager.delete('dx_callsign')
    except:
        pass

def is_session_valid(session_expires_at: Optional[datetime]) -> bool:
    """
    Check if a session token is still valid
    
    Args:
        session_expires_at: Session expiration datetime
        
    Returns:
        True if session is still valid
    """
    if not session_expires_at:
        return False
    
    return datetime.now() < session_expires_at
