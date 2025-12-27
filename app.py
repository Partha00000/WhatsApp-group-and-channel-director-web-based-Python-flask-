import os
import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_ckeditor import CKEditor
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()
ckeditor = CKEditor()

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_timeout": 20,
    "pool_size": 10,
    "max_overflow": 20,
    "echo": False
}

# Flask-Login configuration
app.config['LOGIN_VIEW'] = 'admin.login'
app.config['LOGIN_MESSAGE'] = 'Please log in to access the admin panel.'
app.config['LOGIN_MESSAGE_CATEGORY'] = 'info'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', '587'))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

# CKEditor configuration
app.config['CKEDITOR_SERVE_LOCAL'] = False
app.config['CKEDITOR_HEIGHT'] = 400

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
mail.init_app(app)
ckeditor.init_app(app)

# Import models and routes
from models import *
from routes import *
from admin_routes import admin

# Register blueprints
app.register_blueprint(admin)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    
    # Create default admin user if none exists
    if not User.query.filter_by(username='admin').first():
        from werkzeug.security import generate_password_hash
        admin_user = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin/admin123")
