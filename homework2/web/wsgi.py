from web.app import app as application

# This allows running the app directly or through WSGI
if __name__ == '__main__':
    application.run_server(debug=True)