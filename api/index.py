import sys
import os

# Backend folder ko Python path me add karein
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app