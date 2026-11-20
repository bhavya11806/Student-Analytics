from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Student, Subject, Attendance, Department, Faculty, FacultySubject
from app.utils.decorators import faculty_required
from app.services.attendance_service import attendance_service

attendance_bp = Blueprint("attendance", __name__, url_prefix="/attendance")

@attendance_bp.route("/mark", methods=["GET", "POST"])
@login_required
@faculty_required
def mark():
    departments = Department.query.all()
    subjects = Subject.query.all()

    # Pre-select faculty department or assigned subjects
    faculty = Faculty.query.filter_by(user_id=current_user.id).first() if current_user.role == "faculty" else None
    default_dept_id = faculty.department_id if faculty else (departments[0].id if departments else None)

    dept_id = request.args.get("department_id", type=int, default=default_dept_id)
    semester = request.args.get("semester", type=int, default=5)
    subject_id = request.args.get("subject_id", type=int)

    # Filter subjects by department and semester
    filtered_subjects = Subject.query
    if dept_id:
        filtered_subjects = filtered_subjects.filter_by(department_id=dept_id)
    if semester:
        filtered_subjects = filtered_subjects.filter_by(semester=semester)
    filtered_subjects = filtered_subjects.all()

    if not subject_id and filtered_subjects:
        subject_id = filtered_subjects[0].id

    # Filter students for the class
    query = Student.query.filter_by(account_status="Active")
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if semester:
        query = query.filter_by(semester=semester)
    students = query.order_by(Student.roll_no.asc()).all()

    if request.method == "POST":
        post_sub_id = request.form.get("subject_id", type=int)
        post_date_str = request.form.get("date")
        post_session = request.form.get("session", "Regular").strip()

        if not post_sub_id or not post_date_str:
            flash("Please specify a valid subject and attendance date.", "danger")
            return redirect(url_for("attendance.mark", department_id=dept_id, semester=semester, subject_id=post_sub_id))

        try:
            att_date = datetime.strptime(post_date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
            return redirect(url_for("attendance.mark"))

        saved_count = 0
        updated_count = 0

        for student in students:
            status = request.form.get(f"status_{student.id}")
            remarks = request.form.get(f"remarks_{student.id}", "").strip() or None

            if status in ("Present", "Absent", "Late"):
                _, created = attendance_service.mark_attendance(
                    student_id=student.id,
                    subject_id=post_sub_id,
                    att_date=att_date,
                    session=post_session,
                    status=status,
                    marked_by=current_user.id,
                    remarks=remarks
                )
                if created:
                    saved_count += 1
                else:
                    updated_count += 1

        flash(f"Attendance recorded successfully: {saved_count} new entries, {updated_count} updated entries.", "success")
        return redirect(url_for("attendance.mark", department_id=dept_id, semester=semester, subject_id=post_sub_id))

    return render_template(
        "attendance.html",
        departments=departments,
        subjects=filtered_subjects,
        students=students,
        selected_dept=dept_id,
        selected_sem=semester,
        selected_subject=subject_id,
        today=date.today().isoformat()
    )

@attendance_bp.route("/records")
@login_required
@faculty_required
def records():
    subject_id = request.args.get("subject_id", type=int)
    att_date = request.args.get("date")
    status = request.args.get("status")
    roll_no = request.args.get("roll_no", "").strip()

    query = Attendance.query.join(Student).join(Subject)

    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    if att_date:
        try:
            d = datetime.strptime(att_date, "%Y-%m-%d").date()
            query = query.filter(Attendance.date == d)
        except ValueError:
            pass
    if status:
        query = query.filter(Attendance.status == status)
    if roll_no:
        query = query.filter(Student.roll_no.ilike(f"%{roll_no}%"))

    rows = query.order_by(Attendance.date.desc(), Attendance.id.desc()).limit(200).all()
    subjects = Subject.query.all()

    return render_template(
        "attendance_records.html",
        rows=rows,
        subjects=subjects,
        selected_subject=subject_id,
        selected_date=att_date,
        selected_status=status,
        search_roll=roll_no
    )

@attendance_bp.route("/edit/<int:record_id>", methods=["POST"])
@login_required
@faculty_required
def edit_record(record_id):
    record = db.session.get(Attendance, record_id)
    if not record:
        flash("Attendance record not found.", "danger")
        return redirect(url_for("attendance.records"))

    # Role & Authorization check: only Admin or the user who marked it can edit
    if current_user.role != "admin" and record.marked_by != current_user.id:
        flash("Unauthorized: You can only edit attendance records marked by yourself.", "danger")
        return redirect(url_for("attendance.records"))

    new_status = request.form.get("status")
    new_remarks = request.form.get("remarks")

    if new_status in ("Present", "Absent", "Late"):
        record.status = new_status
        record.remarks = new_remarks
        record.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Attendance record successfully modified.", "success")

    return redirect(url_for("attendance.records"))
