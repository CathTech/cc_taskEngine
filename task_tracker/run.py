#!/usr/bin/env python3
"""
Task Tracker Application
A simple task management system with projects, tasks, and calendar view.
"""

import sys
import os

# Add the backend directory to the path to find the app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == "__main__":
    print("Starting Task Tracker Application...")
    print("Visit http://localhost:5000 to access the application")
    app.run(host='0.0.0.0', port=5000, debug=True)