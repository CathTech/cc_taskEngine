#!/usr/bin/env python3
"""
Script to update the database schema for new functionality.
This script adds missing columns and tables if they don't exist yet.
"""

import sqlite3
import sys
from typing import List, Tuple


def get_existing_columns(conn: sqlite3.Connection, table_name: str) -> List[str]:
    """Get list of existing columns in a table."""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    return columns


def check_and_add_column(conn: sqlite3.Connection, table_name: str, column_name: str, column_def: str) -> bool:
    """Check if column exists and add it if it doesn't exist."""
    existing_columns = get_existing_columns(conn, table_name)
    
    if column_name not in existing_columns:
        cursor = conn.cursor()
        try:
            alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"
            cursor.execute(alter_query)
            print(f"Added column '{column_name}' to table '{table_name}'")
            return True
        except sqlite3.Error as e:
            print(f"Error adding column '{column_name}' to table '{table_name}': {e}")
            return False
    else:
        print(f"Column '{column_name}' already exists in table '{table_name}'")
        return False


def update_database_schema():
    """Update the database schema to include all necessary fields for new functionality."""
    print("Starting database update...")
    
    conn = sqlite3.connect('tasks.db')
    
    # Check and add columns to tasks table
    tasks_updates_needed = 0
    
    # Check if planned_start_time column exists (was mentioned in requirements as "запланированное время начала выполнения задачи")
    if check_and_add_column(conn, 'tasks', 'planned_start_time', 'TIME'):
        tasks_updates_needed += 1
        
    # Check if color column exists
    if check_and_add_column(conn, 'tasks', 'color', "TEXT DEFAULT '#1098ad'"):
        tasks_updates_needed += 1
        
    # Check if kanban_enabled column exists
    if check_and_add_column(conn, 'tasks', 'kanban_enabled', 'BOOLEAN DEFAULT 0'):
        tasks_updates_needed += 1
        
    # Check if kanban_status column exists
    if check_and_add_column(conn, 'tasks', 'kanban_status', "TEXT DEFAULT 'Новая'"):
        tasks_updates_needed += 1
    
    # Check if completed column exists (for tracking completed tasks)
    if check_and_add_column(conn, 'tasks', 'completed', 'BOOLEAN DEFAULT 0'):
        tasks_updates_needed += 1
        
    # Check if completion_date column exists
    if check_and_add_column(conn, 'tasks', 'completion_date', 'DATE'):
        tasks_updates_needed += 1
    
    # Check if show_in_calendar column exists
    if check_and_add_column(conn, 'tasks', 'show_in_calendar', 'BOOLEAN DEFAULT 0'):
        tasks_updates_needed += 1

    # Check and create projects table if it doesn't exist
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='projects' ''')
    if not cursor.fetchone():
        print("Creating projects table...")
        cursor.execute('''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                identifier TEXT UNIQUE NOT NULL
            )
        ''')
        print("Created projects table")
    else:
        print("Projects table already exists")

    # Check and create tasks table if it doesn't exist (as fallback)
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='tasks' ''')
    if not cursor.fetchone():
        print("Creating tasks table...")
        cursor.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                planned_date DATE,
                planned_start_time TIME,
                deadline DATE,
                priority TEXT DEFAULT 'Базовый',
                show_in_calendar BOOLEAN DEFAULT 0,
                completed BOOLEAN DEFAULT 0,
                completion_date DATE,
                color TEXT DEFAULT '#1098ad',
                kanban_enabled BOOLEAN DEFAULT 0,
                kanban_status TEXT DEFAULT 'Новая',
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        print("Created tasks table")
    else:
        print("Tasks table already exists")

    # Update kanban_status column to include all possible values as constraints would
    # (though SQLite doesn't enforce CHECK constraints properly, we document them)
    
    if tasks_updates_needed > 0:
        print(f"\nSuccessfully updated database schema. {tasks_updates_needed} columns added.")
    else:
        print("\nDatabase schema is already up-to-date. No changes needed.")

    # Verify the final structure
    print("\nVerifying final table structure:")
    cursor.execute("PRAGMA table_info(tasks)")
    columns = cursor.fetchall()
    print("Current 'tasks' table structure:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - Default: {col[4]}")

    conn.commit()
    conn.close()
    print("\nDatabase update completed!")


if __name__ == "__main__":
    try:
        update_database_schema()
    except Exception as e:
        print(f"Error during database update: {e}")
        sys.exit(1)