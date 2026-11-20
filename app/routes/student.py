from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Student, Attendance, Mark
from app.utils.decorators import student_required
from app.services.attendance_service import attendance_service
from app.services.analytics_service import analytics_service
from app.services.notification_service import notification_service

student_bp = Blueprint("student", __name__, url_prefix="/student")

@student_bp.route("/dashboard")
@login_required
@student_required
def dashboard():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template("student_dashboard.html", student=None)

    # Attendance calculations
    att_summary = attendance_service.get_student_attendance_summary(student.id)

    # Academic & marks calculations
    academic_summary = analytics_service.get_student_academic_summary(student.id)

    # Risk analysis & recommendations
    risk = analytics_service.classify_student_risk(student.id)

    # Recent marks
    recent_marks = Mark.query.filter_by(student_id=student.id).order_by(Mark.exam_date.desc()).limit(8).all()

    # In-app notifications for this student
    notifications = notification_service.get_user_notifications(current_user.id)

    return render_template(
        "student_dashboard.html",
        student=student,
        attendance=att_summary,
        academic=academic_summary,
        risk=risk,
        recent_marks=recent_marks,
        notifications=notifications
    )

@student_bp.route("/attendance-history")
@login_required
@student_required
def attendance_history():
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template("student_attendance_history.html", records=[])

    records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    summary = attendance_service.get_student_attendance_summary(student.id)
    return render_template("student_attendance_history.html", student=student, records=records, summary=summary)
