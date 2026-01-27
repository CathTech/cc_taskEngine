# Task Tracker Application

A comprehensive task management system built with Python Flask that allows you to manage projects and tasks with a calendar view.

## Features

### Projects
- Create and manage projects with names and identifiers
- Each project has a unique identifier that serves as a prefix for tasks within the project
- View all tasks associated with a project

### Tasks
- Create tasks with the following fields:
  - **Identifier**: Automatically generated as "project identifier" + "task number"
  - **Title**: Name and short content of the task
  - **Description**: Additional information about the task
  - **Planned Date**: Date when the task is planned
  - **Deadline**: Deadline date for the task
  - **Priority**: Dropdown with options "Other, Low, Basic, Important, Urgent"
  - **Show in Calendar**: Checkbox to determine if the task appears in the calendar
  - **Completed**: Checkbox to mark task as completed
  - **Completion Date**: Automatically set when task is marked as completed

### Calendar
- Google Calendar-like interface showing tasks based on "Planned Date" and "Deadline"
- Color-coded events based on priority level
- Click on events to view task details

## Installation

1. Clone or download the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. The database will be automatically initialized when you run the application:
```bash
python run.py
```

3. Open your browser and go to `http://localhost:5000`

4. Start by creating a project, then add tasks to it, and view everything in the calendar

## Database Initialization

The database is automatically created when the application starts. If you need to manually initialize or reset the database:

- To initialize the database with sample data: `python setup_db.py --sample-data`
- To initialize the database without sample data: `python setup_db.py`

## Project Structure

```
task_tracker/
├── backend/
│   └── app.py          # Main Flask application
├── templates/          # HTML templates
│   ├── index.html
│   ├── projects.html
│   ├── project_detail.html
│   ├── task_detail.html
│   ├── create_project.html
│   ├── create_task.html
│   ├── edit_task.html
│   └── calendar.html
├── requirements.txt    # Python dependencies
└── run.py             # Startup script
```

## Technology Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript with Bootstrap
- Database: SQLite (creates tasks.db on first run)
- Calendar: FullCalendar.js