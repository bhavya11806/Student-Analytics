import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import AcademicReport, Student, Department
from app.utils.decorators import roles_required
from app.services.report_service import report_service
from app.services.s3_service import s3_service

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

@reports_bp.route("")
@login_required
@roles_required("admin", "faculty", "student")
def index():
    if current_user.role == "student":
        student = Student.query.filter_by(user_id=current_user.id).first()
        reports = AcademicReport.query.filter(AcademicReport.file_name.ilike(f"%{student.roll_no}%")).order_by(AcademicReport.created_at.desc()).all() if student else []
    else:
        reports = AcademicReport.query.order_by(AcademicReport.created_at.desc()).limit(50).all()

    departments = Department.query.all()
    students = Student.query.all() if current_user.role in ("admin", "faculty") else []

    return render_template("reports.html", reports=reports, departments=departments, students=students)

@reports_bp.route("/student-attendance/<int:student_id>")
@login_required
@roles_required("admin", "faculty", "student")
def generate_student_attendance_pdf(student_id):
    # Authorization check: student can only download their own
    if current_user.role == "student":
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or student.id != student_id:
            flash("Unauthorized access to report.", "danger")
            return redirect(url_for("reports.index"))

    filepath, report_rec = report_service.generate_student_attendance_pdf(student_id, current_user.id)

    # If S3 presigned URL is available, redirect to it; otherwise stream local file
    if report_rec.s3_url:
        return redirect(report_rec.s3_url)
    return send_file(filepath, as_attachment=True, download_name=report_rec.file_name, mimetype="application/pdf")

@reports_bp.route("/student-performance/<int:student_id>")
@login_required
@roles_required("admin", "faculty", "student")
def generate_student_performance_pdf(student_id):
    if current_user.role == "student":
        student = Student.query.filter_by(user_id=current_user.id).first()
        if not student or student.id != student_id:
            flash("Unauthorized access to report.", "danger")
            return redirect(url_for("reports.index"))

    filepath, report_rec = report_service.generate_student_performance_pdf(student_id, current_user.id)

    if report_rec.s3_url:
        return redirect(report_rec.s3_url)
    return send_file(filepath, as_attachment=True, download_name=report_rec.file_name, mimetype="application/pdf")

@reports_bp.route("/export/attendance-excel")
@login_required
@roles_required("admin", "faculty")
def export_attendance_excel():
    dept_id = request.args.get("department_id", type=int)
    sem = request.args.get("semester", type=int)

    filepath, report_rec = report_service.generate_attendance_excel(dept_id, sem, current_user.id)

    if report_rec.s3_url:
        return redirect(report_rec.s3_url)
    return send_file(
        filepath,
        as_attachment=True,
        download_name=report_rec.file_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@reports_bp.route("/export/performance-excel")
@login_required
@roles_required("admin", "faculty")
def export_performance_excel():
    dept_id = request.args.get("department_id", type=int)
    sem = request.args.get("semester", type=int)

    filepath, report_rec = report_service.generate_performance_excel(dept_id, sem, current_user.id)

    if report_rec.s3_url:
        return redirect(report_rec.s3_url)
    return send_file(
        filepath,
        as_attachment=True,
        download_name=report_rec.file_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@reports_bp.route("/download/<int:report_id>")
@login_required
def download_saved_report(report_id):
    report = db.session.get(AcademicReport, report_id)
    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for("reports.index"))

    # If S3 configured and has key, get fresh presigned URL
    if report.s3_key and s3_service.is_configured():
        fresh_url = s3_service.generate_presigned_url(report.s3_key)
        if fresh_url:
            return redirect(fresh_url)

    # Otherwise stream local file
    if report.file_path and os.path.exists(report.file_path):
        return send_file(report.file_path, as_attachment=True, download_name=report.file_name)

    flash("Report file is no longer available locally.", "warning")
    return redirect(url_for("reports.index"))
