from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, user_logged_in, user_logged_out, current_user
from config import Config
import os
from datetime import datetime

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Track user login
    @user_logged_in.connect_via(app)
    def on_user_logged_in(sender, user, **extra):
        try:
            user.last_login = datetime.utcnow()
            user.last_activity = datetime.utcnow()
            user.is_logged_in = True
            user.session_id = session.get('_id', 'unknown')
            db.session.commit()
        except Exception as e:
            print(f"Error updating login status: {e}")
    
    # Track user logout
    @user_logged_out.connect_via(app)
    def on_user_logged_out(sender, user, **extra):
        try:
            if user:
                user.is_logged_in = False
                user.session_id = None
                db.session.commit()
        except Exception as e:
            print(f"Error updating logout status: {e}")
    
    from app.routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    # Track user activity on every request
    @app.before_request
    def update_last_activity():
        try:
            if current_user.is_authenticated:
                current_user.last_activity = datetime.utcnow()
                current_user.is_logged_in = True
                db.session.commit()
        except Exception as e:
            pass
    
    # ==================== DATABASE & ADMIN CREATION ====================
    with app.app_context():
        db.create_all()
        from app.utils import generate_qr_code
        
        # Force create/update admin user
        try:
            # Check if any users exist
            user_count = User.query.count()
            
            if user_count == 0:
                # No users at all - create admin
                admin = User(
                    name='Admin',
                    email='admin@example.com',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                generate_qr_code(admin.id)
                print('='*50)
                print('✅ Admin user created! (No users existed)')
                print('📧 Email: admin@example.com')
                print('🔑 Password: admin123')
                print('='*50)
            else:
                # Check if admin exists
                admin = User.query.filter_by(email='admin@example.com').first()
                
                if not admin:
                    # Create admin even if other users exist
                    admin = User(
                        name='Admin',
                        email='admin@example.com',
                        role='admin',
                        is_active=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    generate_qr_code(admin.id)
                    print('='*50)
                    print('✅ Admin user created! (Added to existing users)')
                    print('📧 Email: admin@example.com')
                    print('🔑 Password: admin123')
                    print('='*50)
                else:
                    # Reset admin password and ensure active
                    admin.set_password('admin123')
                    admin.is_active = True
                    admin.role = 'admin'
                    db.session.commit()
                    print('='*50)
                    print('✅ Admin user updated!')
                    print('📧 Email: admin@example.com')
                    print('🔑 Password: admin123 (reset)')
                    print('✅ Status: Active')
                    print('='*50)
                    
        except Exception as e:
            print(f"❌ Error creating admin: {e}")
            db.session.rollback()
            # Try one more time with a simpler approach
            try:
                # Fallback: Try to create admin without checking existing
                admin = User.query.filter_by(email='admin@example.com').first()
                if not admin:
                    admin = User(
                        name='Admin',
                        email='admin@example.com',
                        role='admin',
                        is_active=True
                    )
                    admin.set_password('admin123')
                    db.session.add(admin)
                    db.session.commit()
                    generate_qr_code(admin.id)
                    print('='*50)
                    print('✅ Admin user created! (Fallback method)')
                    print('📧 Email: admin@example.com')
                    print('🔑 Password: admin123')
                    print('='*50)
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")
    
    return app