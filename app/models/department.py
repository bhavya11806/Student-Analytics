from datetime import datetime
from app import db

class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    courses = db.relationship("Course", back_populates="department", cascade="all, delete-orphan")
    subjects = db.relationship("Subject", back_populates="department", cascade="all, delete-orphan")
    faculty_members = db.relationship("Faculty", back_populates="department")
    students = db.relationship("Student", back_populates="department")

    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"

class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    duration_years = db.Column(db.Integer, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    department = db.relationship("Department", back_populates="courses")
    semesters = db.relationship("Semester", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.code} - {self.name}>"

class Semester(db.Model):
    __tablename__ = "semesters"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(20), default="2026-2027", nullable=False)

    course = db.relationship("Course", back_populates="semesters")

    __table_args__ = (
        db.UniqueConstraint("course_id", "semester_number", "academic_year", name="uq_course_sem_year"),
    )

    def __repr__(self):
        return f"<Semester {self.semester_number} ({self.academic_year})>"
