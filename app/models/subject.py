from datetime import datetime
from app import db

class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, default=1)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    credits = db.Column(db.Integer, default=4, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = db.relationship("Department", back_populates="subjects")
    faculty_assignments = db.relationship("FacultySubject", back_populates="subject", cascade="all, delete-orphan")
    attendance_records = db.relationship("Attendance", back_populates="subject", cascade="all, delete-orphan")
    marks_records = db.relationship("Mark", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.code} - {self.name} (Sem {self.semester})>"
