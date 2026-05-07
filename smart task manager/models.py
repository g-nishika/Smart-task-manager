from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

ROLE_ADMIN = 'ADMIN'
ROLE_MEMBER = 'MEMBER'
TASK_STATUS = ['TODO', 'IN_PROGRESS', 'DONE']
TASK_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH']


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_MEMBER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='creator', lazy=True)
    assigned_tasks = db.relationship(
        'Task',
        backref='assignee',
        lazy=True,
        foreign_keys='Task.assigned_to'
    )

    @property
    def initials(self):
        parts = self.username.split()
        return ''.join(part[0] for part in parts[:2]).upper()


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='TODO')
    priority = db.Column(db.String(20), nullable=False, default='MEDIUM')
    due_date = db.Column(db.Date, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db():
    db.create_all()


def seed_data():
    if User.query.filter_by(email='admin@example.com').first():
        return

    admin = User(
        username='admin',
        email='admin@example.com',
        password=generate_password_hash('Admin@123'),
        role=ROLE_ADMIN,
    )
    member1 = User(
        username='alice',
        email='alice@example.com',
        password=generate_password_hash('Member@123'),
        role=ROLE_MEMBER,
    )
    member2 = User(
        username='bob',
        email='bob@example.com',
        password=generate_password_hash('Member@123'),
        role=ROLE_MEMBER,
    )

    db.session.add_all([admin, member1, member2])
    db.session.commit()

    project = Project(
        title='Website Redesign',
        description='Redesign the team landing page and task workflows.',
        created_by=admin.id,
    )
    db.session.add(project)
    db.session.commit()

    task1 = Task(
        title='Create wireframes',
        description='Design desktop and mobile wireframes for the new homepage.',
        status='TODO',
        priority='HIGH',
        due_date=datetime.utcnow().date() + timedelta(days=7),
        assigned_to=member1.id,
        project_id=project.id,
    )
    task2 = Task(
        title='Write project plan',
        description='Document milestones, roles, and delivery expectations.',
        status='IN_PROGRESS',
        priority='MEDIUM',
        due_date=datetime.utcnow().date() + timedelta(days=3),
        assigned_to=member2.id,
        project_id=project.id,
    )
    task3 = Task(
        title='Review branding assets',
        description='Audit logos, color palettes, and typography for consistency.',
        status='DONE',
        priority='LOW',
        due_date=datetime.utcnow().date() - timedelta(days=2),
        assigned_to=member1.id,
        project_id=project.id,
    )

    db.session.add_all([task1, task2, task3])
    db.session.commit()
