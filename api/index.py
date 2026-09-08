import sys
import os

try:
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from app import app
except Exception as e:
    import traceback
    def app(environ, start_response):
        status = '500 Internal Server Error'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [traceback.format_exc().encode('utf-8')]
