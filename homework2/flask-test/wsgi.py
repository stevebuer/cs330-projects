#!/usr/bin/env python3
"""
WSGI entry point for Apache mod_wsgi
"""

import sys
import os

# Add the application directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask application
from app import application

# This is what Apache mod_wsgi will call
if __name__ != '__main__':
    # Log startup information for debugging
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.info(f"WSGI application starting from {__file__}")