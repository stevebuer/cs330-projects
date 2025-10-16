# WSGI Test Flask Application Setup - Chat Transcript

**Date:** October 15, 2025  
**Topic:** Converting Flask test application to use Apache WSGI

## Initial Request
User wanted to update a Python Flask script to actually use WSGI for Apache configuration testing.

## Analysis of Existing Code
The existing `app.py` was a basic Flask application:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World! Steve\'s test App for WSGI'

if __name__ == '__main__':
    app.run()
```

## Changes Made

### 1. Updated app.py for WSGI
- Added `application = app` object for Apache mod_wsgi
- Added test routes: `/test` and `/info` for verification
- Modified development server configuration
- Added debugging information in `/info` route

### 2. Created wsgi.py
- WSGI entry point file for Apache
- Proper path management for Python modules
- Added logging for debugging WSGI startup

### 3. Created apache-wsgi.conf
- Complete Apache virtual host configuration
- WSGIDaemonProcess configuration for process isolation
- Static file serving setup
- Proper logging configuration
- Alternative subdirectory deployment example

### 4. Updated DocumentRoot and Paths
User requested changing Apache DocumentRoot from development path to `/var/www/dxdev`. Updated all related paths:
- DocumentRoot: `/var/www/dxdev`
- WSGIDaemonProcess python-path: `/var/www/dxdev`
- WSGIScriptAlias: `/var/www/dxdev/wsgi.py`
- Directory directives: `/var/www/dxdev`
- Static files: `/var/www/dxdev/static`

## Final File Structure
```
homework2/flask-test/
├── app.py              # Updated Flask app with WSGI support
├── wsgi.py             # WSGI entry point for Apache
└── apache-wsgi.conf    # Apache configuration file
```

## Key WSGI Features Implemented
1. **Application Object**: `application = app` for mod_wsgi
2. **Process Isolation**: WSGIDaemonProcess configuration
3. **Path Management**: Proper Python path handling
4. **Testing Routes**: `/test` and `/info` endpoints
5. **Development Mode**: Maintained ability to run locally
6. **Production Ready**: Complete Apache configuration

## Deployment Instructions
1. Copy files to `/var/www/dxdev/`
2. Set proper permissions (`www-data:www-data`, 755)
3. Copy `apache-wsgi.conf` to `/etc/apache2/sites-available/`
4. Enable site: `sudo a2ensite apache-wsgi.conf`
5. Enable mod_wsgi: `sudo a2enmod wsgi`
6. Restart Apache: `sudo systemctl restart apache2`

## Testing
- **Development**: `python3 app.py`
- **Production**: Access via Apache
- **Verification**: Visit `/test` and `/info` routes

## Git Operations
Staged files for commit:
- `homework2/flask-test/app.py` (modified)
- `homework2/flask-test/wsgi.py` (new)
- `homework2/flask-test/apache-wsgi.conf` (new)

## Result
Successfully converted basic Flask application to production-ready WSGI application with complete Apache configuration. Application can now be deployed via Apache mod_wsgi while maintaining development capabilities.