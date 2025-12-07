"""
Database Client for Local User Configuration
Handles database connections for user preferences and settings
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class DBClient:
    """Client for local database operations (user config only)"""
    
    def __init__(self):
        """Initialize database connection parameters from environment"""
        self.host = os.getenv('PGHOST', 'localhost')
        self.port = os.getenv('PGPORT', '5432')
        self.database = os.getenv('PGDATABASE', 'dx_analysis')
        self.user = os.getenv('PGUSER', 'dx_web_user')
        self.password = os.getenv('PGPASSWORD', '')
    
    def get_connection(self):
        """
        Create database connection
        
        Returns:
            psycopg2 connection object or None if connection fails
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return conn
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            st.info(f"Trying to connect to: {self.user}@{self.host}:{self.port}/{self.database}")
            return None
    
    def save_user(self, callsign: str, name: Optional[str] = None, 
                  grid_square: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Save or update user in database
        
        Args:
            callsign: Ham radio callsign
            name: User's name
            grid_square: Maidenhead grid square
            
        Returns:
            User dictionary or None if failed
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dashboard_users (callsign, name, grid_square, last_login)
                VALUES (%s, %s, %s, NOW())
                ON CONFLICT (callsign)
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    grid_square = EXCLUDED.grid_square,
                    last_login = NOW()
                RETURNING id, callsign, name, grid_square
            """, (callsign.upper(), name, grid_square.upper() if grid_square else None))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'callsign': result[1],
                    'name': result[2],
                    'grid_square': result[3]
                }
        except Exception as e:
            st.error(f"Error saving user: {e}")
            if conn:
                conn.rollback()
                conn.close()
        
        return None
    
    def get_user(self, callsign: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve user from database
        
        Args:
            callsign: Ham radio callsign
            
        Returns:
            User dictionary or None if not found
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, callsign, name, grid_square, preferences
                FROM dashboard_users
                WHERE callsign = %s
            """, (callsign.upper(),))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'callsign': result[1],
                    'name': result[2],
                    'grid_square': result[3],
                    'preferences': result[4] or {}
                }
        except Exception as e:
            st.error(f"Error retrieving user: {e}")
            if conn:
                conn.close()
        
        return None
    
    def update_preferences(self, callsign: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences
        
        Args:
            callsign: Ham radio callsign
            preferences: Dictionary of preferences to store
            
        Returns:
            True if successful
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            import json
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dashboard_users
                SET preferences = %s
                WHERE callsign = %s
            """, (json.dumps(preferences), callsign.upper()))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating preferences: {e}")
            if conn:
                conn.rollback()
                conn.close()
        
        return False
    
    def create_user_with_password(self, callsign: str, password_hash: str, 
                                   name: Optional[str] = None,
                                   grid_square: Optional[str] = None,
                                   email: Optional[str] = None,
                                   phone: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Create new user with password authentication
        
        Args:
            callsign: Ham radio callsign
            password_hash: Bcrypt hashed password
            name: User's name
            grid_square: Maidenhead grid square
            email: Email address for notifications
            phone: Phone number for SMS alerts
            
        Returns:
            User dictionary or None if failed
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO dashboard_users (callsign, password_hash, name, grid_square, email, phone, timezone, last_login)
                VALUES (%s, %s, %s, %s, %s, %s, 'UTC', NOW())
                ON CONFLICT (callsign)
                DO UPDATE SET 
                    password_hash = EXCLUDED.password_hash,
                    name = EXCLUDED.name,
                    grid_square = EXCLUDED.grid_square,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    last_login = NOW()
                RETURNING id, callsign, name, grid_square, email, phone, 
                          sms_alerts_enabled, email_alerts_enabled, preferences, timezone
            """, (callsign.upper(), password_hash, name, 
                  grid_square.upper() if grid_square else None, email, phone))
            
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'callsign': result[1],
                    'name': result[2],
                    'grid_square': result[3],
                    'email': result[4],
                    'phone': result[5],
                    'sms_alerts_enabled': result[6] or False,
                    'email_alerts_enabled': result[7] or False,
                    'preferences': result[8] or {},
                    'timezone': result[9]
                }
        except Exception as e:
            st.error(f"Error creating user: {e}")
            if conn:
                conn.rollback()
                conn.close()
        
        return None
    
    def authenticate_user(self, callsign: str) -> Optional[Dict[str, Any]]:
        """
        Get user for authentication (includes password_hash)
        
        Args:
            callsign: Ham radio callsign
            
        Returns:
            User dictionary with password_hash or None
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, callsign, password_hash, name, grid_square, email, phone,
                       sms_alerts_enabled, email_alerts_enabled, preferences,
                       session_token, session_expires_at, timezone
                FROM dashboard_users
                WHERE callsign = %s
            """, (callsign.upper(),))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'callsign': result[1],
                    'password_hash': result[2],
                    'name': result[3],
                    'grid_square': result[4],
                    'email': result[5],
                    'phone': result[6],
                    'sms_alerts_enabled': result[7] or False,
                    'email_alerts_enabled': result[8] or False,
                    'preferences': result[9] or {},
                    'session_token': result[10],
                    'session_expires_at': result[11],
                    'timezone': result[12]
                }
        except Exception as e:
            st.error(f"Error authenticating user: {e}")
            if conn:
                conn.close()
        
        return None
    
    def save_session_token(self, callsign: str, session_token: str, days: int = 30) -> bool:
        """
        Save session token for user
        
        Args:
            callsign: Ham radio callsign
            session_token: Secure session token
            days: Number of days until token expires
            
        Returns:
            True if successful
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            expires_at = datetime.now() + timedelta(days=days)
            
            cursor.execute("""
                UPDATE dashboard_users
                SET session_token = %s,
                    session_expires_at = %s,
                    last_login = NOW()
                WHERE callsign = %s
            """, (session_token, expires_at, callsign.upper()))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving session: {e}")
            if conn:
                conn.rollback()
                conn.close()
        
        return False
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user by session token
        
        Args:
            session_token: Session token from cookie
            
        Returns:
            User dictionary or None if invalid/expired
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, callsign, name, grid_square, email, phone,
                       sms_alerts_enabled, email_alerts_enabled, preferences,
                       session_expires_at, timezone
                FROM dashboard_users
                WHERE session_token = %s
                  AND session_expires_at > NOW()
            """, (session_token,))
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result:
                return {
                    'id': result[0],
                    'callsign': result[1],
                    'name': result[2],
                    'grid_square': result[3],
                    'email': result[4],
                    'phone': result[5],
                    'sms_alerts_enabled': result[6] or False,
                    'email_alerts_enabled': result[7] or False,
                    'preferences': result[8] or {},
                    'session_expires_at': result[9],
                    'timezone': result[10]
                }
        except Exception as e:
            if conn:
                conn.close()
        
        return None
    
    def clear_session_token(self, callsign: str) -> bool:
        """
        Clear session token (logout)
        
        Args:
            callsign: Ham radio callsign
            
        Returns:
            True if successful
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE dashboard_users
                SET session_token = NULL,
                    session_expires_at = NULL
                WHERE callsign = %s
            """, (callsign.upper(),))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            if conn:
                conn.rollback()
                conn.close()
        
        return False
    
    def update_user_settings(self, callsign: str, **kwargs) -> bool:
        """
        Update user settings (email, phone, alert preferences, etc.)
        
        Args:
            callsign: Ham radio callsign
            **kwargs: Fields to update (email, phone, sms_alerts_enabled, etc.)
            
        Returns:
            True if successful
        """
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            params = []
            
            allowed_fields = ['name', 'grid_square', 'email', 'phone', 
                            'sms_alerts_enabled', 'email_alerts_enabled', 'timezone']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    set_clauses.append(f"{field} = %s")
                    params.append(value)
            
            if not set_clauses:
                return False
            
            params.append(callsign.upper())
            query = f"UPDATE dashboard_users SET {', '.join(set_clauses)} WHERE callsign = %s"
            
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error updating settings: {e}")
            if conn:
                conn.rollback()
                conn.close()
        
        return False
    
    def get_latest_solar_data(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent solar data from wwv_announcements table
        
        Returns:
            Dictionary with solar_flux, sunspot_number, k_index, a_index, and timestamp
            or None if no data available
        """
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute('''
                SELECT 
                    solar_flux,
                    sunspot_number,
                    k_index,
                    a_index,
                    timestamp
                FROM wwv_announcements
                WHERE solar_flux IS NOT NULL 
                   OR sunspot_number IS NOT NULL
                   OR k_index IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            st.error(f"Error fetching solar data: {e}")
            if conn:
                conn.close()
            return None


@st.cache_resource
def get_db_client() -> DBClient:
    """
    Get cached database client instance
    
    Returns:
        DBClient instance
    """
    return DBClient()
