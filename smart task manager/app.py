import os
from pathlib import Path
from flask import Flask, redirect, url_for
from models import db, init_db, seed_data
from routes.auth import auth_bp, current_user as auth_current_user
from routes.dashboard import main_bp


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    database_url = os.environ.get('DATABASE_URL')

    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        sqlite_path = Path(app.root_path) / 'team_task_manager.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{sqlite_path}'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_user():
        return {'current_user': auth_current_user()}

    with app.app_context():
        init_db()
        seed_data()

    @app.route('/')
    def home():
        return redirect(url_for('main.dashboard'))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
