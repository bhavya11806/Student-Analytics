from datetime import datetime
from app import db

class Mark(db.Model):
    __tablename__ = "marks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False, index=True)
    exam_type = db.Column(db.String(60), nullable=False)  # 'Midterm 1', 'Midterm 2', 'Internal Exam', 'Assignment', 'End Semester'
    marks_obtained = db.Column(db.Float, nullable=False)
    max_marks = db.Column(db.Float, nullable=False)
    exam_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    remarks = db.Column(db.String(200), nullable=True)
    entered_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = db.relationship("Student", back_populates="marks_records")
    subject = db.relationship("Subject", back_populates="marks_records")
    marker = db.relationship("User", foreign_keys=[entered_by])

    @property
    def percentage(self):
        if self.max_marks > 0:
            return round((self.marks_obtained / self.max_marks) * 100, 2)
        return 0.0

    @property
    def grade(self):
        pct = self.percentage
        if pct >= 90: return "A+"
        if pct >= 80: return "A"
        if pct >= 70: return "B+"
        if pct >= 60: return "B"
        if pct >= 50: return "C"
        if pct >= 40: return "D"
        return "F"

    def __repr__(self):
        return f"<Mark Student:{self.student_id} Subject:{self.subject_id} {self.exam_type}: {self.marks_obtained}/{self.max_marks}>"
