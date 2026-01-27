from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime
import json

app = Flask(__name__, template_folder='../templates')

# Database setup
DATABASE = 'tasks.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Create projects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            identifier TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create tasks table
    c.execute('''
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
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return render_template('projects.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,)).fetchall()
    conn.close()
    return render_template('project_detail.html', project=project, tasks=tasks)

@app.route('/task/<int:task_id>')
def task_detail(task_id):
    conn = get_db_connection()
    task = conn.execute('''
        SELECT t.*, p.identifier as project_identifier 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ?
    ''', (task_id,)).fetchone()
    
    # Generate task ID (project identifier + task number)
    task_id_display = f"{task['project_identifier']}-{task['id']}"
    
    conn.close()
    return render_template('task_detail.html', task=task, task_id_display=task_id_display)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        identifier = request.form['identifier']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO projects (name, identifier) VALUES (?, ?)', (name, identifier))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Project identifier must be unique", 400
        conn.close()
        
        return redirect(url_for('projects'))
    
    return render_template('create_project.html')

@app.route('/create_task/<int:project_id>', methods=['GET', 'POST'])
def create_task(project_id):
    conn = get_db_connection()
    project = conn.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        planned_date = request.form.get('planned_date')
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Базовый')
        show_in_calendar = bool(request.form.get('show_in_calendar'))
        completed = bool(request.form.get('completed'))
        
        completion_date = None
        if completed:
            completion_date = datetime.now().strftime('%Y-%m-%d')
        
        conn.execute('''
            INSERT INTO tasks (project_id, title, description, planned_date, deadline, 
                              priority, show_in_calendar, completed, completion_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, title, description, planned_date, deadline, 
              priority, show_in_calendar, completed, completion_date))
        conn.commit()
        conn.close()
        
        return redirect(url_for('project_detail', project_id=project_id))
    
    conn.close()
    return render_template('create_task.html', project=project)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute('''
        SELECT t.*, p.identifier as project_identifier 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ?
    ''', (task_id,)).fetchone()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        planned_date = request.form.get('planned_date')
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Базовый')
        show_in_calendar = bool(request.form.get('show_in_calendar'))
        completed = bool(request.form.get('completed'))
        
        completion_date = None
        if completed and not task['completion_date']:
            # Only set completion date if task wasn't already completed
            completion_date = datetime.now().strftime('%Y-%m-%d')
        elif not completed:
            # If unchecking completed, remove completion date
            completion_date = None
        else:
            # Keep existing completion date if task was already completed
            completion_date = task['completion_date']
        
        conn.execute('''
            UPDATE tasks SET title=?, description=?, planned_date=?, deadline=?, 
                          priority=?, show_in_calendar=?, completed=?, completion_date=?
            WHERE id = ?
        ''', (title, description, planned_date, deadline, priority, 
              show_in_calendar, completed, completion_date, task_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Generate task ID for display
    task_id_display = f"{task['project_identifier']}-{task['id']}"
    conn.close()
    return render_template('edit_task.html', task=task, task_id_display=task_id_display)

@app.route('/calendar')
def calendar():
    conn = get_db_connection()
    # Get tasks that should appear in calendar (either planned or deadline dates)
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.show_in_calendar = 1 AND (t.planned_date IS NOT NULL OR t.deadline IS NOT NULL)
    ''').fetchall()
    conn.close()
    
    # Format tasks for calendar
    calendar_events = []
    for task in tasks:
        # Add planned date event if exists
        if task['planned_date']:
            calendar_events.append({
                'title': f"[{task['project_identifier']}-{task['id']}] {task['title']}",
                'start': task['planned_date'],
                'color': '#3174ad' if task['priority'] == 'Срочный' else 
                         '#ff9f43' if task['priority'] == 'Важный' else
                         '#1098ad' if task['priority'] == 'Базовый' else
                         '#6c757d' if task['priority'] == 'Низкий' else '#e03131',
                'extendedProps': {
                    'taskId': task['id'],
                    'projectId': task['project_id'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'completed': task['completed']
                }
            })
        
        # Add deadline event if exists and it's different from planned date
        if task['deadline'] and task['deadline'] != task['planned_date']:
            calendar_events.append({
                'title': f"[{task['project_identifier']}-{task['id']}] DEADLINE: {task['title']}",
                'start': task['deadline'],
                'color': '#e03131',  # Red for deadlines
                'extendedProps': {
                    'taskId': task['id'],
                    'projectId': task['project_id'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'completed': task['completed']
                }
            })
    
    return render_template('calendar.html', events=json.dumps(calendar_events))

@app.route('/api/tasks')
def api_tasks():
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
    ''').fetchall()
    conn.close()
    
    tasks_list = []
    for task in tasks:
        task_dict = dict(task)
        task_dict['id_display'] = f"{task['project_identifier']}-{task['id']}"
        tasks_list.append(task_dict)
    
    return jsonify(tasks_list)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)