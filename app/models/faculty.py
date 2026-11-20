from datetime import datetime
from app import db

class Faculty(db.Model):
    __tablename__ = "faculty"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    employee_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    designation = db.Column(db.String(80), default="Assistant Professor", nullable=False)
    qualification = db.Column(db.String(100), default="M.Tech / Ph.D", nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default="Active", nullable=False)  # Active, Inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="faculty_profile")
    department = db.relationship("Department", back_populates="faculty_members")
    assigned_subjects = db.relationship("FacultySubject", back_populates="faculty", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Faculty {self.employee_id} - {self.user.name if self.user else 'Unknown'}>"

class FacultySubject(db.Model):
    __tablename__ = "faculty_subjects"

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty.id"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)
    academic_year = db.Column(db.String(20), default="2026-2027", nullable=False)
    semester = db.Column(db.Integer, default=1, nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    faculty = db.relationship("Faculty", back_populates="assigned_subjects")
    subject = db.relationship("Subject", back_populates="faculty_assignments")

    __table_args__ = (
        db.UniqueConstraint("faculty_id", "subject_id", "academic_year", name="uq_faculty_subject_year"),
    )

    def __repr__(self):
        return f"<FacultySubject Faculty:{self.faculty_id} Subject:{self.subject_id}>"
