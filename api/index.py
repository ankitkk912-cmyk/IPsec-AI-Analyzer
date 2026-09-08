import sys
import os

# Set root directory in python path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Catch exact runtime exception and display it on browser
try:
    from app import app
except Exception as e:
    import traceback
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return f"<h3>Application Startup Error</h3><pre>{traceback.format_exc()}</pre>", 500