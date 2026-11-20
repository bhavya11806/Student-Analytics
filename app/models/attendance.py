from datetime import datetime
from app import db

class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    session = db.Column(db.String(30), default="Regular", nullable=False)  # 'Lecture 1', 'Morning', 'Afternoon', 'Regular'
    status = db.Column(db.String(15), nullable=False)  # 'Present', 'Absent', 'Late'
    marked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    remarks = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="attendance_records")
    subject = db.relationship("Subject", back_populates="attendance_records")
    marker = db.relationship("User", foreign_keys=[marked_by])

    __table_args__ = (
        db.UniqueConstraint("student_id", "subject_id", "date", "session", name="uq_attendance_student_sub_date_session"),
    )

    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Subject:{self.subject_id} {self.date} {self.status}>"
