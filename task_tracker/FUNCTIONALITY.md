# Task Tracker Application - Functionality Overview

## Overview
The Task Tracker is a comprehensive task management system built with Python Flask that allows you to manage projects and tasks with a calendar view.

## Features Implemented

### 1. Projects
- **Create and manage projects** with names and identifiers
- Each project has a unique identifier that serves as a prefix for tasks within the project
- View all tasks associated with a project
- Navigation between projects and their related tasks

### 2. Tasks
Tasks include all the required fields:

- **Identifier**: Automatically generated as "project identifier" + "task number"
- **Title**: Name and short content of the task
- **Description**: Additional information about the task
- **Planned Date**: Date when the task is planned
- **Deadline**: Deadline date for the task
- **Priority**: Dropdown with options "Прочее, Низкий, Базовый, Важный, Срочный"
- **Show in Calendar**: Checkbox to determine if the task appears in the calendar
- **Completed**: Checkbox to mark task as completed
- **Completion Date**: Automatically set when task is marked as completed

Buttons: "Save" and "Cancel"

### 3. Calendar
- Google Calendar-like interface showing tasks based on "Planned Date" and "Deadline"
- Color-coded events based on priority level:
  - Срочный: Red
  - Важный: Orange
  - Базовый: Blue
  - Низкий: Gray
  - Прочее: Light blue
- Click on events to view task details in a modal
- Interactive FullCalendar.js implementation

## Database Schema
- **Projects Table**: Stores project information (id, name, identifier)
- **Tasks Table**: Stores task information (id, project_id, title, description, planned_date, deadline, priority, show_in_calendar, completed, completion_date)

## Technology Stack
- **Backend**: Python Flask
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Database**: SQLite (creates tasks.db on first run)
- **Calendar**: FullCalendar.js

## File Structure
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

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python run.py`
3. Access the application at `http://localhost:5000`

## Usage Flow
1. Start by creating a project with a name and identifier
2. Add tasks to the project with all required details
3. View all tasks in the project list
4. Edit tasks as needed
5. Check the calendar view to see tasks visualized by date
6. Mark tasks as completed when done

All functionality matches the requirements specified in the original request.