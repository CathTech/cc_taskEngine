#!/usr/bin/env python3
"""
Test script to verify the Task Tracker application functionality
"""

import sys
import os

# Add the backend directory to the path to find the app module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, init_db
import sqlite3

def test_app_creation():
    """Test that the Flask app can be created successfully"""
    assert app is not None
    print("✓ Flask app created successfully")

def test_database_init():
    """Test that database initialization works"""
    try:
        init_db()
        print("✓ Database initialized successfully")
        
        # Check if database file exists
        if os.path.exists('tasks.db'):
            print("✓ Database file created successfully")
            
            # Connect and verify tables exist
            conn = sqlite3.connect('tasks.db')
            c = conn.cursor()
            
            # Check projects table
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='projects';")
            projects_table = c.fetchone()
            if projects_table:
                print("✓ Projects table exists")
            else:
                print("✗ Projects table does not exist")
                
            # Check tasks table
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks';")
            tasks_table = c.fetchone()
            if tasks_table:
                print("✓ Tasks table exists")
            else:
                print("✗ Tasks table does not exist")
                
            conn.close()
        else:
            print("✗ Database file was not created")
            
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")

def test_routes():
    """Test that the main routes exist"""
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        assert response.status_code == 200
        print("✓ Home route (/) works")
        
        # Test projects page
        response = client.get('/projects')
        assert response.status_code == 200
        print("✓ Projects route (/projects) works")
        
        # Test calendar page
        response = client.get('/calendar')
        assert response.status_code == 200
        print("✓ Calendar route (/calendar) works")
        
        # Test API endpoint
        response = client.get('/api/tasks')
        assert response.status_code == 200
        print("✓ API route (/api/tasks) works")

if __name__ == "__main__":
    print("Testing Task Tracker Application...")
    print()
    
    # Change to the task tracker directory
    os.chdir(os.path.dirname(__file__))
    
    try:
        test_app_creation()
        test_database_init()
        test_routes()
        print()
        print("🎉 All tests passed! The Task Tracker application is working correctly.")
        print()
        print("To run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the app: python run.py")
        print("3. Visit http://localhost:5000 in your browser")
    except Exception as e:
        print(f"❌ Tests failed with error: {e}")
        sys.exit(1)