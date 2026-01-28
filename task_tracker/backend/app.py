from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import os
from datetime import datetime
import json

# Import and run database initialization
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from init_db import init_database

app = Flask(__name__, template_folder='../templates')

# Database setup
DATABASE = 'tasks.db'

def init_db():
    init_database()  # Use the centralized initialization

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Get non-completed tasks sorted from newest to oldest (by ID)
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.completed = 0
        ORDER BY t.id DESC
    ''').fetchall()
    
    # Add overdue status to tasks
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    for i, task in enumerate(tasks):
        is_overdue = False
        if task['deadline'] and task['deadline'] < today:
            is_overdue = True
        elif task['planned_date'] and task['planned_date'] < today:
            is_overdue = True
        tasks[i] = dict(task)
        tasks[i]['overdue'] = is_overdue
    
    conn.close()
    
    return render_template('index.html', tasks=tasks)

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
    
    # Add overdue status to tasks
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    for i, task in enumerate(tasks):
        is_overdue = False
        if task['deadline'] and task['deadline'] < today:
            is_overdue = True
        elif task['planned_date'] and task['planned_date'] < today:
            is_overdue = True
        tasks[i] = dict(task)
        tasks[i]['overdue'] = is_overdue
    
    conn.close()
    return render_template('project_detail.html', project=project, tasks=tasks)

@app.route('/task/<int:task_id>')
def task_detail(task_id):
    conn = get_db_connection()
    task = conn.execute('''
        SELECT t.*, p.identifier as project_identifier, p.name as project_name, p.responsible as project_responsible 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ?
    ''', (task_id,)).fetchone()
    
    # Calculate task number within project (count of tasks in project with ID <= current task ID)
    task_number_in_project = conn.execute(
        'SELECT COUNT(*) FROM tasks WHERE project_id = ? AND id <= ?', 
        (task['project_id'], task_id)
    ).fetchone()[0]
    
    # Generate task ID (project identifier + task number in project)
    task_id_display = f"{task['project_identifier']}-{task_number_in_project}"
    
    conn.close()
    return render_template('task_detail.html', task=task, task_id_display=task_id_display)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        identifier = request.form['identifier']
        responsible = request.form.get('responsible', '')
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO projects (name, identifier, responsible) VALUES (?, ?, ?)', (name, identifier, responsible))
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
    
    # Get date parameter from URL if present
    prefill_date = request.args.get('date', '')
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        planned_date = request.form.get('planned_date')
        planned_start_time = request.form.get('planned_start_time')
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Базовый')
        show_in_calendar = bool(request.form.get('show_in_calendar', 'on'))  # Default to True
        completed = bool(request.form.get('completed'))
        color = request.form.get('color', '#1098ad')
        kanban_enabled = bool(request.form.get('kanban_enabled', 'on'))  # Default to True
        kanban_status = request.form.get('kanban_status', 'Новая')
        responsible = request.form.get('responsible', '')
        
        completion_date = None
        if completed:
            completion_date = datetime.now().strftime('%Y-%m-%d')
        
        conn.execute('''
            INSERT INTO tasks (project_id, title, description, planned_date, planned_start_time, deadline, 
                              priority, show_in_calendar, completed, completion_date, color, kanban_enabled, kanban_status, responsible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project_id, title, description, planned_date, planned_start_time, deadline, 
              priority, show_in_calendar, completed, completion_date, color, kanban_enabled, kanban_status, responsible))
        conn.commit()
        conn.close()
        
        return redirect(url_for('project_detail', project_id=project_id))
    
    conn.close()
    return render_template('create_task.html', project=project, prefill_date=prefill_date)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    conn = get_db_connection()
    task = conn.execute('''
        SELECT t.*, p.identifier as project_identifier, p.responsible as project_responsible 
        FROM tasks t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ?
    ''', (task_id,)).fetchone()
    
    # Get all projects for the move-to-project feature
    all_projects = conn.execute('SELECT * FROM projects ORDER BY name').fetchall()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        planned_date = request.form.get('planned_date')
        planned_start_time = request.form.get('planned_start_time')
        deadline = request.form.get('deadline')
        priority = request.form.get('priority', 'Базовый')
        show_in_calendar = bool(request.form.get('show_in_calendar'))
        completed = bool(request.form.get('completed'))
        color = request.form.get('color', '#1098ad')
        kanban_enabled = bool(request.form.get('kanban_enabled'))
        kanban_status = request.form.get('kanban_status', 'Новая')
        responsible = request.form.get('responsible', '')
        
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
            UPDATE tasks SET title=?, description=?, planned_date=?, planned_start_time=?, deadline=?, 
                          priority=?, show_in_calendar=?, completed=?, completion_date=?, color=?, kanban_enabled=?, kanban_status=?, responsible=?
            WHERE id = ?
        ''', (title, description, planned_date, planned_start_time, deadline, priority, 
              show_in_calendar, completed, completion_date, color, kanban_enabled, kanban_status, responsible, task_id))
        conn.commit()
        conn.close()
        
        return redirect(url_for('task_detail', task_id=task_id))
    
    # Calculate task number within project (count of tasks in project with ID <= current task ID)
    task_number_in_project = conn.execute(
        'SELECT COUNT(*) FROM tasks WHERE project_id = ? AND id <= ?', 
        (task['project_id'], task_id)
    ).fetchone()[0]

    # Generate task ID for display
    task_id_display = f"{task['project_identifier']}-{task_number_in_project}"
    conn.close()
    return render_template('edit_task.html', task=task, task_id_display=task_id_display, all_projects=all_projects)

@app.route('/completed_tasks')
def completed_tasks():
    conn = get_db_connection()
    # Get completed tasks that were completed less than a week ago
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.completed = 1 
        AND (
            t.completion_date IS NULL 
            OR t.completion_date >= date('now', '-7 days')
        )
        ORDER BY t.completion_date DESC, t.id DESC
    ''').fetchall()
    
    # Add overdue status to tasks
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    for i, task in enumerate(tasks):
        is_overdue = False
        if task['deadline'] and task['deadline'] < today:
            is_overdue = True
        elif task['planned_date'] and task['planned_date'] < today:
            is_overdue = True
        tasks[i] = dict(task)
        tasks[i]['overdue'] = is_overdue
    
    conn.close()
    
    return render_template('completed_tasks.html', tasks=tasks)


@app.route('/all_completed_tasks')
def all_completed_tasks():
    """Show all completed tasks including those completed more than a week ago"""
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.completed = 1
        ORDER BY t.completion_date DESC, t.id DESC
    ''').fetchall()
    
    # Add overdue status to tasks
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    for i, task in enumerate(tasks):
        is_overdue = False
        if task['deadline'] and task['deadline'] < today:
            is_overdue = True
        elif task['planned_date'] and task['planned_date'] < today:
            is_overdue = True
        tasks[i] = dict(task)
        tasks[i]['overdue'] = is_overdue
    
    conn.close()
    
    return render_template('completed_tasks.html', tasks=tasks, show_all=True)


@app.route('/kanban')
def kanban():
    conn = get_db_connection()
    # Get all tasks that have Kanban enabled
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.kanban_enabled = 1
        ORDER BY t.id DESC
    ''').fetchall()
    
    # Add overdue status to tasks
    from datetime import date
    today = date.today().strftime('%Y-%m-%d')
    for i, task in enumerate(tasks):
        is_overdue = False
        if task['deadline'] and task['deadline'] < today:
            is_overdue = True
        elif task['planned_date'] and task['planned_date'] < today:
            is_overdue = True
        tasks[i] = dict(task)
        tasks[i]['overdue'] = is_overdue
    
    conn.close()
    
    return render_template('kanban.html', tasks=tasks)


@app.route('/calendar')
def calendar():
    conn = get_db_connection()
    # Get tasks that should appear in calendar (either planned or deadline dates)
    # Order by planned date/time, prioritizing tasks with time over those without time
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.show_in_calendar = 1 AND (t.planned_date IS NOT NULL OR t.deadline IS NOT NULL)
        ORDER BY 
            CASE WHEN t.planned_start_time IS NOT NULL THEN 0 ELSE 1 END,
            t.planned_date ASC,
            t.planned_start_time ASC,
            t.id DESC
    ''').fetchall()
    conn.close()
    
    # Format tasks for calendar
    calendar_events = []
    for task in tasks:
        # Add planned date event if exists
        if task['planned_date']:
            # Use the task's color if available, otherwise default to priority-based colors
            color = task['color'] if task['color'] else (
                '#e03131' if task['priority'] == 'Срочный' else 
                '#ff9f43' if task['priority'] == 'Важный' else
                '#1098ad' if task['priority'] == 'Базовый' else
                '#6c757d' if task['priority'] == 'Низкий' else '#3498db'
            )
            
            # Combine date and time if both exist
            start_datetime = task['planned_date']
            if task['planned_start_time']:
                start_datetime = f"{task['planned_date']}T{task['planned_start_time']}"
            
            calendar_events.append({
                'title': f"[{task['project_identifier']}-{task['id']}] {task['title']}",
                'start': start_datetime,
                'color': color,
                'extendedProps': {
                    'taskId': task['id'],
                    'projectId': task['project_id'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'completed': task['completed'],
                    'color': task['color'],
                    'startTime': task['planned_start_time']
                }
            })
        
        # Add deadline event if exists and it's different from planned date
        if task['deadline'] and task['deadline'] != task['planned_date']:
            # Use the task's color if available, otherwise default to red for deadlines
            color = task['color'] if task['color'] else '#e03131'
            
            calendar_events.append({
                'title': f"[{task['project_identifier']}-{task['id']}] DEADLINE: {task['title']}",
                'start': task['deadline'],
                'color': color,
                'extendedProps': {
                    'taskId': task['id'],
                    'projectId': task['project_id'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'completed': task['completed'],
                    'color': task['color'],
                    'startTime': None
                }
            })
    
    return render_template('calendar.html', events=json.dumps(calendar_events))


@app.route('/select_project_for_task')
def select_project_for_task():
    """Show project selection page for creating a task"""
    conn = get_db_connection()
    projects = conn.execute('SELECT * FROM projects ORDER BY name').fetchall()
    conn.close()
    
    return render_template('select_project.html', projects=projects)

@app.route('/create_task_from_calendar', methods=['POST'])
def create_task_from_calendar():
    """Create a task from calendar date click"""
    data = request.get_json()
    date = data.get('date')
    
    # Redirect to project selection page with date parameter
    redirect_url = url_for('select_project_for_task') + f'?date={date}' if date else url_for('select_project_for_task')
    return jsonify({'redirect_url': redirect_url})

@app.route('/create_task_without_project', methods=['GET', 'POST'])
def create_task_without_project():
    """Create a task without selecting a project first (for dump project)"""
    # Find or create dump project
    conn = get_db_connection()
    dump_project = conn.execute("SELECT id FROM projects WHERE identifier = 'dump'").fetchone()
    
    if not dump_project:
        # Create dump project if it doesn't exist
        conn.execute("INSERT INTO projects (name, identifier, responsible) VALUES ('Dump', 'dump', '')")
        dump_project_id = conn.execute("SELECT id FROM projects WHERE identifier = 'dump'").fetchone()[0]
    else:
        dump_project_id = dump_project[0]
    
    # Create task with default values
    conn.execute('''
        INSERT INTO tasks (project_id, title, description, planned_date, planned_start_time, deadline, 
                          priority, show_in_calendar, completed, completion_date, color, kanban_enabled, kanban_status, responsible)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (dump_project_id, 'Quick Note', '', None, None, None, 'Базовый', True, False, None, '#1098ad', True, 'Новая', ''))
    
    task_id = conn.execute('SELECT id FROM tasks ORDER BY id DESC LIMIT 1').fetchone()[0]
    conn.commit()
    conn.close()
    
    if request.method == 'POST':
        return jsonify({'redirect_url': url_for('edit_task', task_id=task_id)})
    else:
        # For GET request, redirect directly to the edit task page
        return redirect(url_for('edit_task', task_id=task_id))

@app.route('/api/tasks')
def api_tasks():
    conn = get_db_connection()
    tasks = conn.execute('''
        SELECT t.*, p.name as project_name, p.identifier as project_identifier, p.responsible as project_responsible
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

@app.route('/api/update_kanban_status', methods=['POST'])
def update_kanban_status():
    data = request.get_json()
    task_id = data.get('task_id')
    new_status = data.get('new_status')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET kanban_status = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/update_task_visibility', methods=['POST'])
def update_task_visibility():
    data = request.get_json()
    task_id = data.get('task_id')
    show_in_calendar = data.get('show_in_calendar')
    kanban_enabled = data.get('kanban_enabled')
    
    conn = get_db_connection()
    conn.execute('UPDATE tasks SET show_in_calendar = ?, kanban_enabled = ? WHERE id = ?', 
                 (show_in_calendar, kanban_enabled, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/toggle_task_completed', methods=['POST'])
def toggle_task_completed():
    data = request.get_json()
    task_id = data.get('task_id')
    completed = data.get('completed')
    
    conn = get_db_connection()
    
    completion_date = None
    if completed:
        completion_date = datetime.now().strftime('%Y-%m-%d')
    
    conn.execute('UPDATE tasks SET completed = ?, completion_date = ? WHERE id = ?', 
                 (completed, completion_date, task_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/move_task_to_project', methods=['POST'])
def move_task_to_project():
    data = request.get_json()
    task_id = data.get('task_id')
    project_id = data.get('project_id')
    
    if not task_id or not project_id:
        return jsonify({'error': 'Missing task_id or project_id'}), 400
    
    try:
        conn = get_db_connection()
        
        # Check if project exists
        project = conn.execute('SELECT id FROM projects WHERE id = ?', (project_id,)).fetchone()
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Update task's project
        conn.execute('UPDATE tasks SET project_id = ? WHERE id = ?', (project_id, task_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def check_ip_in_whitelist(ip_address):
    """Check if IP address is in the whitelist"""
    try:
        with open('../whitelist.txt', 'r') as f:
            whitelist = f.read().strip().split('\n')
            whitelist = [line.strip() for line in whitelist if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        # If whitelist file doesn't exist, allow all IPs for backward compatibility
        return True
    
    # Check exact match or subnet match
    import ipaddress
    for entry in whitelist:
        try:
            if '/' in entry:  # Subnet notation
                network = ipaddress.IPv4Network(entry, strict=False)
                if ipaddress.IPv4Address(ip_address) in network:
                    return True
            else:  # Exact IP match
                if ip_address == entry:
                    return True
        except ValueError:
            # Skip invalid entries
            continue
    
    return False


def get_client_ip():
    """Get client IP address considering proxies"""
    if request.headers.get('X-Forwarded-For'):
        # Handle multiple IPs in X-Forwarded-For header
        ip = request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip


@app.route('/share_task/<int:task_id>')
def share_task(task_id):
    """Generate a shareable link for a task"""
    task_url = f"{request.url_root}task/{task_id}"
    return jsonify({
        'task_id': task_id,
        'url': task_url,
        'success': True
    })


@app.route('/task/<int:task_id>/edit_allowed')
def task_edit_allowed(task_id):
    """Check if current IP is allowed to edit the task"""
    client_ip = get_client_ip()
    can_edit = check_ip_in_whitelist(client_ip)
    return jsonify({
        'task_id': task_id,
        'can_edit': can_edit,
        'client_ip': client_ip
    })


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)