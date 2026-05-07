from datetime import datetime, date
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User, Project, Task, db, ROLE_ADMIN, ROLE_MEMBER, TASK_STATUS, TASK_PRIORITIES

main_bp = Blueprint('main', __name__)


def current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            flash('Please log in to continue.', 'warning')
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('user_role') != ROLE_ADMIN:
            flash('Administrator access required.', 'danger')
            return redirect(url_for('main.dashboard'))
        return view(*args, **kwargs)
    return wrapped


@main_bp.app_context_processor
def inject_user():
    return {'current_user': current_user()}


@main_bp.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    if user.role == ROLE_ADMIN:
        tasks = Task.query.order_by(Task.due_date.asc(), Task.priority.desc()).all()
        total_tasks = Task.query.count()
        completed_tasks = Task.query.filter_by(status='DONE').count()
        pending_tasks = Task.query.filter(Task.status != 'DONE').count()
        overdue_tasks = Task.query.filter(Task.due_date < date.today(), Task.status != 'DONE').count()
    else:
        tasks = Task.query.filter_by(assigned_to=user.id).order_by(Task.due_date.asc()).all()
        total_tasks = Task.query.filter_by(assigned_to=user.id).count()
        completed_tasks = Task.query.filter_by(assigned_to=user.id, status='DONE').count()
        pending_tasks = Task.query.filter(Task.assigned_to == user.id, Task.status != 'DONE').count()
        overdue_tasks = Task.query.filter(Task.assigned_to == user.id, Task.due_date < date.today(), Task.status != 'DONE').count()

    projects = Project.query.order_by(Project.created_at.desc()).limit(5).all()
    status_breakdown = {status: Task.query.filter_by(status=status).count() for status in TASK_STATUS}
    team_members = User.query.filter(User.role == ROLE_MEMBER).order_by(User.username).all()
    member_stats = []
    for member in team_members:
        assigned_count = Task.query.filter_by(assigned_to=member.id).count()
        completed_count = Task.query.filter_by(assigned_to=member.id, status='DONE').count()
        pending_count = Task.query.filter(Task.assigned_to == member.id, Task.status != 'DONE').count()
        member_stats.append({
            'member': member,
            'assigned': assigned_count,
            'completed': completed_count,
            'pending': pending_count,
        })
    overdue_list = Task.query.filter(Task.due_date < date.today(), Task.status != 'DONE').order_by(Task.due_date.asc()).limit(5).all()
    return render_template(
        'dashboard.html',
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        tasks=tasks,
        projects=projects,
        status_breakdown=status_breakdown,
        team_members=team_members,
        member_stats=member_stats,
        overdue_list=overdue_list,
        today=date.today(),
    )


@main_bp.route('/projects')
@login_required
@admin_required
def projects():
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=projects)


@main_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Project title is required.', 'warning')
            return render_template('project_form.html')

        project = Project(title=title, description=description, created_by=session.get('user_id'))
        try:
            db.session.add(project)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Unable to create project. Please try again.', 'danger')
            return render_template('project_form.html')

        flash('Project created successfully.', 'success')
        return redirect(url_for('main.projects'))

    return render_template('project_form.html')


@main_bp.route('/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()

        if not title:
            flash('Project title cannot be empty.', 'warning')
            return render_template('project_form.html', project=project)

        project.title = title
        project.description = description
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Unable to update project. Please try again.', 'danger')
            return render_template('project_form.html', project=project)

        flash('Project updated successfully.', 'success')
        return redirect(url_for('main.projects'))

    return render_template('project_form.html', project=project)


@main_bp.route('/projects/delete/<int:project_id>', methods=['POST'])
@login_required
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    try:
        db.session.delete(project)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Unable to delete project. Please try again.', 'danger')
        return redirect(url_for('main.projects'))

    flash('Project deleted successfully.', 'success')
    return redirect(url_for('main.projects'))


@main_bp.route('/tasks')
@login_required
def tasks():
    user = current_user()
    if user.role == ROLE_ADMIN:
        tasks = Task.query.order_by(Task.due_date.asc()).all()
    else:
        tasks = Task.query.filter_by(assigned_to=user.id).order_by(Task.due_date.asc()).all()
    projects = Project.query.order_by(Project.title).all()
    members = User.query.filter(User.role == ROLE_MEMBER).order_by(User.username).all()
    return render_template('tasks.html', tasks=tasks, projects=projects, members=members, today=date.today())


@main_bp.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def create_task():
    projects = Project.query.order_by(Project.title).all()
    members = User.query.filter(User.role == ROLE_MEMBER).order_by(User.username).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'TODO')
        priority = request.form.get('priority', 'MEDIUM')
        due_date = request.form.get('due_date')
        assigned_to = request.form.get('assigned_to')
        project_id = request.form.get('project_id')

        if not title or not project_id:
            flash('Task title and project selection are required.', 'warning')
            return render_template('task_form.html', projects=projects, members=members)

        due_date_value = None
        if due_date:
            try:
                due_date_value = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid due date format.', 'warning')
                return render_template('task_form.html', projects=projects, members=members)

        assigned_to_id = None
        if assigned_to:
            try:
                assigned_to_id = int(assigned_to)
            except ValueError:
                flash('Invalid assignee selected.', 'warning')
                return render_template('task_form.html', projects=projects, members=members)

        try:
            project_id_value = int(project_id)
        except ValueError:
            flash('Invalid project selected.', 'warning')
            return render_template('task_form.html', projects=projects, members=members)

        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date_value,
            assigned_to=assigned_to_id,
            project_id=project_id_value,
        )
        try:
            db.session.add(task)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Unable to create task. Please try again.', 'danger')
            return render_template('task_form.html', projects=projects, members=members)

        flash('Task created successfully.', 'success')
        return redirect(url_for('main.tasks'))

    return render_template('task_form.html', projects=projects, members=members)


@main_bp.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    projects = Project.query.order_by(Project.title).all()
    members = User.query.filter(User.role == ROLE_MEMBER).order_by(User.username).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', task.status)
        priority = request.form.get('priority', task.priority)
        due_date = request.form.get('due_date')
        assigned_to = request.form.get('assigned_to')
        project_id = request.form.get('project_id')

        if not title or not project_id:
            flash('Task title and project selection are required.', 'warning')
            return render_template('task_form.html', task=task, projects=projects, members=members)

        due_date_value = None
        if due_date:
            try:
                due_date_value = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid due date format.', 'warning')
                return render_template('task_form.html', task=task, projects=projects, members=members)

        assigned_to_id = None
        if assigned_to:
            try:
                assigned_to_id = int(assigned_to)
            except ValueError:
                flash('Invalid assignee selected.', 'warning')
                return render_template('task_form.html', task=task, projects=projects, members=members)

        try:
            task.project_id = int(project_id)
        except ValueError:
            flash('Invalid project selected.', 'warning')
            return render_template('task_form.html', task=task, projects=projects, members=members)

        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.due_date = due_date_value
        task.assigned_to = assigned_to_id
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('Unable to update task. Please try again.', 'danger')
            return render_template('task_form.html', task=task, projects=projects, members=members)

        flash('Task updated successfully.', 'success')
        return redirect(url_for('main.tasks'))

    return render_template('task_form.html', task=task, projects=projects, members=members)


@main_bp.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
@admin_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Unable to delete task. Please try again.', 'danger')
        return redirect(url_for('main.tasks'))

    flash('Task deleted successfully.', 'success')
    return redirect(url_for('main.tasks'))


@main_bp.route('/tasks/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    user = current_user()
    task = Task.query.get_or_404(task_id)
    if user.role != ROLE_ADMIN and task.assigned_to != user.id:
        flash('You are not authorized to update this task.', 'danger')
        return redirect(url_for('main.tasks'))

    new_status = request.form.get('status')
    if new_status not in TASK_STATUS:
        flash('Invalid task status.', 'warning')
        return redirect(url_for('main.tasks'))

    task.status = new_status
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Unable to update task status. Please try again.', 'danger')
        return redirect(url_for('main.tasks'))

    flash('Task status updated successfully.', 'success')
    return redirect(url_for('main.tasks'))


@main_bp.route('/members')
@login_required
@admin_required
def members():
    members = User.query.filter(User.role == ROLE_MEMBER).order_by(User.created_at.desc()).all()
    return render_template('members.html', members=members)
