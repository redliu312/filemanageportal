"""
Vercel serverless function entry point
"""
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app

# Vercel expects a callable named 'app'
# The Flask app instance is already callable