import sys
import os

# Root aur Backend directory search paths me add karein
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# App instance resolution
try:
    from backend.app import app
except ImportError:
    from app import app

# Explicitly expose app for Vercel WSGI
app = app