import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-cloud-student-analytics-secret-key-2026")
    
    # Database configuration - support MySQL/RDS or fallback to SQLite locally
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Default local SQLite database
        db_path = os.path.join(basedir, "student_analytics.db")
        DATABASE_URL = f"sqlite:///{db_path}"
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File storage configuration
    REPORTS_DIR = os.path.join(basedir, "reports")
    UPLOAD_FOLDER = REPORTS_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    
    # AWS Services Configuration
    AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "")
    AWS_SNS_TOPIC_ARN = os.getenv("AWS_SNS_TOPIC_ARN", "")
    
    # System Default Thresholds (Admin configurable via DB SystemSettings)
    DEFAULT_ATTENDANCE_THRESHOLD = float(os.getenv("DEFAULT_ATTENDANCE_THRESHOLD", "75.0"))
    DEFAULT_ACADEMIC_PASS_THRESHOLD = float(os.getenv("DEFAULT_ACADEMIC_PASS_THRESHOLD", "40.0"))
    DEFAULT_ACADEMIC_GOOD_THRESHOLD = float(os.getenv("DEFAULT_ACADEMIC_GOOD_THRESHOLD", "75.0"))
    
    # Cloud / Local storage mode toggle
    USE_S3_STORAGE = os.getenv("USE_S3_STORAGE", "false").lower() in ("true", "1", "yes")

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
