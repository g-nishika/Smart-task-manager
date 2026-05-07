from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db, ROLE_MEMBER, ROLE_ADMIN

auth_bp = Blueprint('auth', __name__)


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    can_choose_role = False
    admin_exists = User.query.filter_by(role=ROLE_ADMIN).first() is not None
    if session.get('user_role') == ROLE_ADMIN or not admin_exists:
        can_choose_role = True

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        selected_role = request.form.get('role', ROLE_MEMBER)

        if not username or not email or not password:
            flash('All fields are required.', 'warning')
            return render_template('signup.html', can_choose_role=can_choose_role)

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('signup.html', can_choose_role=can_choose_role)

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'warning')
            return render_template('signup.html', can_choose_role=can_choose_role)

        role = ROLE_MEMBER
        if can_choose_role and selected_role == ROLE_ADMIN:
            role = ROLE_ADMIN
        elif not admin_exists:
            role = ROLE_ADMIN

        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role,
        )
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception:
            db.session.rollback()
            flash('An error occurred while creating the account. Please try again.', 'danger')
            return render_template('signup.html', can_choose_role=can_choose_role)

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', can_choose_role=can_choose_role)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials. Please try again.', 'danger')
            return render_template('login.html')

        session.clear()
        session['user_id'] = user.id
        session['user_role'] = user.role
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
