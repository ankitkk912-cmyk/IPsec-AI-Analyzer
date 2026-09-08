import sys
import os

# Root aur Backend dono paths ko python path me add karein
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.join(base_dir, 'backend')

sys.path.insert(0, base_dir)
sys.path.insert(0, backend_dir)

try:
    from backend.app import app
except Exception:
    from app import app