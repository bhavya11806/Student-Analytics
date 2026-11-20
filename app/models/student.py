from datetime import datetime
from app import db

class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    roll_no = db.Column(db.String(40), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    course = db.Column(db.String(80), default="B.Tech Computer Science", nullable=False)
    semester = db.Column(db.Integer, default=5, nullable=False)
    admission_year = db.Column(db.Integer, default=2024, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    account_status = db.Column(db.String(20), default="Active", nullable=False)  # Active, Inactive, Graduated
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="student_profile")
    department = db.relationship("Department", back_populates="students")
    attendance_records = db.relationship("Attendance", back_populates="student", cascade="all, delete-orphan", lazy="dynamic")
    marks_records = db.relationship("Mark", back_populates="student", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<Student {self.roll_no} - {self.user.name if self.user else 'Unknown'}>"
