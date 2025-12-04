"""
API Client for DX Cluster Reports
Handles communication with the API for fetching spot data and statistics
"""

import os
import requests
from typing import Optional, Dict, List, Any
import streamlit as st
from datetime import datetime, timedelta

class DXApiClient:
    """Client for interacting with DX Cluster API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of the API (e.g., http://localhost:8080)
        """
        self.base_url = base_url or os.getenv('API_BASE_URL', 'http://localhost:8080')
        self.timeout = 30
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP GET request to API (forcing IPv4)
        
        Args:
            endpoint: API endpoint (e.g., '/api/spots')
            params: Query parameters
            
        Returns:
            JSON response as dict
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            # Create session with IPv4 preference
            import socket
            from requests.adapters import HTTPAdapter
            from urllib3.util.connection import create_connection
            
            def create_ipv4_connection(address, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
                """Force IPv4 connections"""
                host, port = address
                err = None
                for res in socket.getaddrinfo(host, port, socket.AF_INET, socket.SOCK_STREAM):
                    af, socktype, proto, canonname, sa = res
                    sock = None
                    try:
                        sock = socket.socket(af, socktype, proto)
                        if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                            sock.settimeout(timeout)
                        if source_address:
                            sock.bind(source_address)
                        sock.connect(sa)
                        return sock
                    except socket.error as _:
                        err = _
                        if sock is not None:
                            sock.close()
                if err is not None:
                    raise err
                else:
                    raise socket.error("getaddrinfo returns an empty list")
            
            # Monkey patch for this request
            old_create_connection = create_connection
            import urllib3.util.connection
            urllib3.util.connection.create_connection = create_ipv4_connection
            
            try:
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                return response.json()
            finally:
                # Restore original function
                urllib3.util.connection.create_connection = old_create_connection
                
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return {}
    
    def get_spots(self, 
                  band: Optional[str] = None,
                  hours: int = 24,
                  limit: int = 1000,
                  dx_call: Optional[str] = None,
                  spotter_call: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch DX spots from API
        
        Args:
            band: Filter by band (e.g., '10m', '20m')
            hours: Time window in hours
            limit: Maximum number of spots to return
            dx_call: Filter by DX callsign
            spotter_call: Filter by spotter callsign
            
        Returns:
            List of spot dictionaries
        """
        params = {
            'hours': hours,
            'limit': limit
        }
        
        if band:
            params['band'] = band
        if dx_call:
            params['dx_call'] = dx_call
        if spotter_call:
            params['spotter_call'] = spotter_call
            
        result = self._make_request('/api/spots', params)
        return result.get('spots', [])
    
    def get_band_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get band activity statistics
        
        Args:
            hours: Time window in hours
            
        Returns:
            Dictionary with band statistics
        """
        params = {'hours': hours}
        return self._make_request('/api/stats/bands', params)
    
    def get_top_dx_stations(self, hours: int = 24, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most active DX stations
        
        Args:
            hours: Time window in hours
            limit: Number of stations to return
            
        Returns:
            List of DX station statistics
        """
        params = {
            'hours': hours,
            'limit': limit
        }
        result = self._make_request('/api/stats/top-dx', params)
        return result.get('stations', [])
    
    def get_top_spotters(self, hours: int = 24, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most active spotters
        
        Args:
            hours: Time window in hours
            limit: Number of spotters to return
            
        Returns:
            List of spotter statistics
        """
        params = {
            'hours': hours,
            'limit': limit
        }
        result = self._make_request('/api/stats/top-spotters', params)
        return result.get('spotters', [])
    
    def get_propagation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get propagation conditions summary
        
        Args:
            hours: Time window in hours
            
        Returns:
            Dictionary with propagation statistics
        """
        params = {'hours': hours}
        return self._make_request('/api/stats/propagation', params)
    
    def health_check(self) -> bool:
        """
        Check if API is reachable
        
        Returns:
            True if API responds successfully
        """
        try:
            result = self._make_request('/api/health')
            return result.get('status') == 'ok'
        except:
            return False


@st.cache_resource
def get_api_client() -> DXApiClient:
    """
    Get cached API client instance
    
    Returns:
        DXApiClient instance
    """
    return DXApiClient()
