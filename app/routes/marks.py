from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import Student, Subject, Mark, Department
from app.utils.decorators import faculty_required
from app.utils.validators import validate_marks_entry
from app.services.analytics_service import analytics_service

marks_bp = Blueprint("marks", __name__, url_prefix="/marks")

@marks_bp.route("/add", methods=["GET", "POST"])
@login_required
@faculty_required
def add():
    departments = Department.query.all()
    dept_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)

    query = Student.query.filter_by(account_status="Active")
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if semester:
        query = query.filter_by(semester=semester)
    students = query.order_by(Student.roll_no.asc()).all()

    sub_query = Subject.query
    if dept_id:
        sub_query = sub_query.filter_by(department_id=dept_id)
    if semester:
        sub_query = sub_query.filter_by(semester=semester)
    subjects = sub_query.all()

    if request.method == "POST":
        student_id = request.form.get("student_id", type=int)
        subject_id = request.form.get("subject_id", type=int)
        exam_type = request.form.get("exam_type", "").strip()
        exam_date_str = request.form.get("exam_date")
        remarks = request.form.get("remarks", "").strip() or None

        try:
            marks_obtained = float(request.form.get("marks_obtained", 0))
            max_marks = float(request.form.get("max_marks", 100))
        except (ValueError, TypeError):
            flash("Marks must be numeric values.", "danger")
            return redirect(url_for("marks.add"))

        is_valid, err_msg = validate_marks_entry(marks_obtained, max_marks)
        if not is_valid:
            flash(err_msg, "danger")
            return redirect(url_for("marks.add"))

        try:
            exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date() if exam_date_str else date.today()
        except ValueError:
            exam_date = date.today()

        # Check existing mark for same student, subject, and exam type
        existing = Mark.query.filter_by(student_id=student_id, subject_id=subject_id, exam_type=exam_type).first()
        if existing:
            existing.marks_obtained = marks_obtained
            existing.max_marks = max_marks
            existing.exam_date = exam_date
            existing.remarks = remarks
            existing.entered_by = current_user.id
            db.session.commit()
            flash(f"Updated examination score for {existing.student.roll_no} in {existing.subject.name}.", "info")
        else:
            new_mark = Mark(
                student_id=student_id,
                subject_id=subject_id,
                exam_type=exam_type,
                marks_obtained=marks_obtained,
                max_marks=max_marks,
                exam_date=exam_date,
                remarks=remarks,
                entered_by=current_user.id
            )
            db.session.add(new_mark)
            db.session.commit()
            flash("Academic mark recorded successfully.", "success")

        return redirect(url_for("marks.add", department_id=dept_id, semester=semester))

    return render_template(
        "marks.html",
        departments=departments,
        students=students,
        subjects=subjects,
        selected_dept=dept_id,
        selected_sem=semester,
        today=date.today().isoformat()
    )

@marks_bp.route("/records")
@login_required
@faculty_required
def records():
    subject_id = request.args.get("subject_id", type=int)
    exam_type = request.args.get("exam_type")
    roll_no = request.args.get("roll_no", "").strip()

    query = Mark.query.join(Student).join(Subject)

    if subject_id:
        query = query.filter(Mark.subject_id == subject_id)
    if exam_type:
        query = query.filter(Mark.exam_type == exam_type)
    if roll_no:
        query = query.filter(Student.roll_no.ilike(f"%{roll_no}%"))

    marks_list = query.order_by(Mark.exam_date.desc(), Mark.id.desc()).all()
    subjects = Subject.query.all()

    return render_template(
        "marks_records.html",
        marks=marks_list,
        subjects=subjects,
        selected_subject=subject_id,
        selected_exam=exam_type,
        search_roll=roll_no
    )

@marks_bp.route("/edit/<int:mark_id>", methods=["POST"])
@login_required
@faculty_required
def edit_mark(mark_id):
    mark = db.session.get(Mark, mark_id)
    if not mark:
        flash("Mark record not found.", "danger")
        return redirect(url_for("marks.records"))

    try:
        obtained = float(request.form.get("marks_obtained"))
        maximum = float(request.form.get("max_marks"))
    except (ValueError, TypeError):
        flash("Invalid numeric mark input.", "danger")
        return redirect(url_for("marks.records"))

    is_valid, msg = validate_marks_entry(obtained, maximum)
    if not is_valid:
        flash(msg, "danger")
        return redirect(url_for("marks.records"))

    mark.marks_obtained = obtained
    mark.max_marks = maximum
    mark.remarks = request.form.get("remarks", mark.remarks)
    mark.entered_by = current_user.id
    db.session.commit()

    flash(f"Score updated for {mark.student.roll_no}.", "success")
    return redirect(url_for("marks.records"))
