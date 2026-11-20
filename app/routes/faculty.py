from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app import db
from app.models import Faculty, FacultySubject, Student, Subject, Attendance, Mark
from app.utils.decorators import faculty_required
from app.services.attendance_service import attendance_service
from app.services.analytics_service import analytics_service

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")

@faculty_bp.route("/dashboard")
@login_required
@faculty_required
def dashboard():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    assigned_assignments = faculty.assigned_subjects if faculty else []
    assigned_subjects = [a.subject for a in assigned_assignments if a.subject]

    # If no subjects explicitly assigned yet, show department subjects for accessibility
    if not assigned_subjects and faculty and faculty.department:
        assigned_subjects = faculty.department.subjects

    subject_ids = [s.id for s in assigned_subjects]

    # Department students
    students = Student.query.filter_by(department_id=faculty.department_id).all() if faculty else []

    # Calculate subject metrics
    subject_stats = []
    for sub in assigned_subjects:
        metrics = attendance_service.get_subject_attendance_summary(sub.id)
        subject_stats.append({
            "subject": sub,
            "metrics": metrics
        })

    # Low attendance students in department
    low_attendance_students = attendance_service.get_low_attendance_students(
        threshold=75.0,
        department_id=faculty.department_id if faculty else None
    )

    return render_template(
        "faculty_dashboard.html",
        faculty=faculty,
        assigned_subjects=assigned_subjects,
        subject_stats=subject_stats,
        students=students,
        low_attendance_students=low_attendance_students[:10]
    )

@faculty_bp.route("/students")
@login_required
@faculty_required
def student_roster():
    faculty = Faculty.query.filter_by(user_id=current_user.id).first()
    students = Student.query.filter_by(department_id=faculty.department_id).all() if faculty else Student.query.all()

    student_data = []
    for s in students:
        att = attendance_service.get_student_attendance_summary(s.id)
        risk = analytics_service.classify_student_risk(s.id)
        student_data.append({
            "student": s,
            "attendance": att,
            "risk": risk
        })

    return render_template("faculty_students.html", students=student_data, faculty=faculty)
