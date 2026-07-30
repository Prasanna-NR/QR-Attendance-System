from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Login tracking fields
    last_login = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, nullable=True)
    is_logged_in = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.String(100), nullable=True)
    
    attendances = db.relationship('Attendance', backref='user', lazy=True)
    tasks = db.relationship('Task', backref='user', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_qr_path(self):
        return f"qr/{self.id}.png"
    
    def get_time_ago(self, dt):
        if not dt:
            return "Never"
        now = datetime.utcnow()
        diff = now - dt
        if diff.days > 0:
            return f"{diff.days} days ago"
        if diff.seconds < 60:
            return "Just now"
        if diff.seconds < 3600:
            return f"{diff.seconds // 60} min ago"
        return f"{diff.seconds // 3600} hours ago"
    
    def __repr__(self):
        return f'<User {self.email}>'

class Attendance(db.Model):
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    time = db.Column(db.Time, default=datetime.utcnow().time)
    status = db.Column(db.String(20), default='present')
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Attendance {self.user_id} - {self.date}>'

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='medium')
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Task {self.title}>'