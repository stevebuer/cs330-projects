#
# Test Flask and WSGI
# 

from flask import Flask

# Create Flask application instance
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World! Steve\'s test App for WSGI'

@app.route('/test')
def test():
    return 'WSGI Test Route Working!'

@app.route('/info')
def info():
    import os
    return f'WSGI Application - PID: {os.getpid()}, Server: Apache mod_wsgi'

# WSGI application object - this is what Apache mod_wsgi will use
application = app

# For development testing only
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

