import sys
import os
import traceback
from flask import Flask

# Path configuration
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.app import app
except Exception as e:
    # Error catch karke browser par display karne ke liye fallback app
    error_trace = traceback.format_exc()
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<h2>Application Initialization Error:</h2><pre>{error_trace}</pre>", 500