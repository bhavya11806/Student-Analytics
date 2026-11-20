from datetime import datetime
from app import db

class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(30), default="attendance_warning", nullable=False)  # 'attendance_warning', 'academic_alert', 'general'
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    sent_via_sns = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification User:{self.user_id} {self.title}>"

class AcademicReport(db.Model):
    __tablename__ = "academic_reports"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    report_type = db.Column(db.String(40), nullable=False)  # 'attendance_pdf', 'attendance_excel', 'performance_pdf', 'performance_excel'
    file_name = db.Column(db.String(150), nullable=False)
    file_path = db.Column(db.String(255), nullable=True)
    s3_key = db.Column(db.String(255), nullable=True)
    s3_url = db.Column(db.String(500), nullable=True)
    file_size_kb = db.Column(db.Float, default=0.0)
    generated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    generator = db.relationship("User", foreign_keys=[generated_by])

    def __repr__(self):
        return f"<AcademicReport {self.title} ({self.report_type})>"

class SystemSetting(db.Model):
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_value(cls, key, default=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default

    @classmethod
    def set_value(cls, key, value, description=None):
        setting = cls.query.filter_by(key=key).first()
        if setting:
            setting.value = str(value)
            if description:
                setting.description = description
        else:
            setting = cls(key=key, value=str(value), description=description)
            db.session.add(setting)
        db.session.commit()
        return setting

    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
