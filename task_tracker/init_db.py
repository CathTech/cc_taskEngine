import sqlite3
from datetime import datetime

def init_database():
    """Initialize the database with required tables."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            identifier TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            planned_date DATE,
            deadline DATE,
            priority TEXT DEFAULT 'Базовый',
            show_in_calendar BOOLEAN DEFAULT 0,
            completed BOOLEAN DEFAULT 0,
            completion_date DATE,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def populate_sample_data():
    """Add sample data to demonstrate the application."""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    
    # Add sample project
    cursor.execute(
        "INSERT OR IGNORE INTO projects (name, identifier) VALUES (?, ?)",
        ("Sample Project", "SP")
    )
    project_id = cursor.lastrowid
    
    # Add sample tasks
    sample_tasks = [
        {
            "title": "Setup Database",
            "description": "Initialize the database with required tables",
            "planned_date": "2023-06-15",
            "deadline": "2023-06-20",
            "priority": "Важный",
            "in_calendar": True
        },
        {
            "title": "Create UI Components",
            "description": "Design the user interface for the task tracker",
            "planned_date": "2023-06-20",
            "deadline": "2023-06-25",
            "priority": "Базовый",
            "in_calendar": True
        },
        {
            "title": "Implement Backend API",
            "description": "Create API endpoints for CRUD operations",
            "planned_date": "2023-06-22",
            "deadline": "2023-06-30",
            "priority": "Срочный",
            "in_calendar": True
        }
    ]
    
    for task in sample_tasks:
        cursor.execute('''
            INSERT OR IGNORE INTO tasks 
            (project_id, title, description, planned_date, deadline, priority, show_in_calendar)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # Using the sample project ID
            task['title'],
            task['description'],
            task['planned_date'],
            task['deadline'],
            task['priority'],
            task['in_calendar']
        ))
    
    conn.commit()
    conn.close()
    print("Sample data added successfully!")

if __name__ == "__main__":
    init_database()
    populate_sample_data()
    print("Database setup complete!")