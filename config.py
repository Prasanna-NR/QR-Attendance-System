import os

class Config:
    SECRET_KEY = 'your-secret-key-change-in-production-123456789'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///attendance.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'qr')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'