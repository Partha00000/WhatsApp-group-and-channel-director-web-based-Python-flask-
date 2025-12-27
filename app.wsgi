#!/usr/bin/python3
import sys
import os

# Add project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'sqlite:///whatsapp_groups.db')
os.environ['SESSION_SECRET'] = os.environ.get('SESSION_SECRET', 'your-secret-key-here')

from main import app as application

if __name__ == "__main__":
    application.run()