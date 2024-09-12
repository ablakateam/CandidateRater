import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///candidates.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('static', 'img')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
