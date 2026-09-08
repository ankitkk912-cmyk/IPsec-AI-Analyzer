import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.insert(0, backend_dir)

# Set read-only environment flags for Vercel
os.environ['VERCEL'] = '1'

try:
    from app import app
except Exception as e:
    from flask import Flask
    app = Flask(__name__)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        import traceback
        return f'<pre>{traceback.format_exc()}</pre>', 500
