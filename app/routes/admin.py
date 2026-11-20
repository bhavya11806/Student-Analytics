from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Student, Faculty, Department, Course, Semester, Subject, FacultySubject, Attendance, Mark
from app.utils.decorators import admin_required
from app.utils.validators import validate_email_format, validate_password_strength, validate_roll_number
from app.services.analytics_service import analytics_service
from app.services.attendance_service import attendance_service
from app.services.notification_service import notification_service

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    stats = analytics_service.get_college_analytics()
    departments = Department.query.all()
    recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()
    low_att_students = attendance_service.get_low_attendance_students(threshold=stats["thresholds"]["attendance_threshold"])[:5]

    return render_template(
        "admin_dashboard.html",
        stats=stats,
        departments=departments,
        recent_students=recent_students,
        low_att_students=low_att_students
    )

# ----------------- Student Management -----------------
@admin_bp.route("/students", methods=["GET"])
@login_required
@admin_required
def students():
    search = request.args.get("search", "").strip()
    dept_id = request.args.get("department_id", type=int)
    semester = request.args.get("semester", type=int)

    query = Student.query.join(User)

    if search:
        query = query.filter((Student.roll_no.ilike(f"%{search}%")) | (User.name.ilike(f"%{search}%")))
    if dept_id:
        query = query.filter(Student.department_id == dept_id)
    if semester:
        query = query.filter(Student.semester == semester)

    students_list = query.order_by(Student.roll_no.asc()).all()
    departments = Department.query.all()

    # Pre-calculate quick metrics for each student
    student_data = []
    for s in students_list:
        att = attendance_service.get_student_attendance_summary(s.id)
        risk = analytics_service.classify_student_risk(s.id)
        student_data.append({
            "student": s,
            "attendance_pct": att["overall_percentage"],
            "academic_pct": risk["academic_percentage"],
            "grade": risk["grade"],
            "risk_category": risk["category"],
            "badge_class": risk["badge_class"]
        })

    return render_template("students.html", students=student_data, departments=departments,
                           search=search, selected_dept=dept_id, selected_sem=semester)

@admin_bp.route("/students/create", methods=["POST"])
@login_required
@admin_required
def create_student():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    roll_no = request.form.get("roll_no", "").strip().upper()
    dept_id = request.form.get("department_id", type=int)
    course = request.form.get("course", "B.Tech Computer Science").strip()
    semester = request.form.get("semester", type=int, default=1)
    phone = request.form.get("phone", "").strip()
    admission_year = request.form.get("admission_year", type=int, default=2024)

    if not validate_email_format(email):
        flash("Invalid email format.", "danger")
        return redirect(url_for("admin.students"))

    if not validate_roll_number(roll_no):
        flash("Invalid roll number.", "danger")
        return redirect(url_for("admin.students"))

    if User.query.filter_by(email=email).first():
        flash("Email is already registered.", "danger")
        return redirect(url_for("admin.students"))

    if Student.query.filter_by(roll_no=roll_no).first():
        flash(f"Roll Number {roll_no} is already assigned to another student.", "danger")
        return redirect(url_for("admin.students"))

    user = User(name=name, email=email, role="student", phone=phone, active=True)
    user.set_password(password or "Student@123")
    db.session.add(user)
    db.session.flush()

    student = Student(
        user_id=user.id,
        roll_no=roll_no,
        department_id=dept_id,
        course=course,
        semester=semester,
        phone=phone,
        admission_year=admission_year,
        account_status="Active"
    )
    db.session.add(student)
    db.session.commit()

    flash(f"Student {name} ({roll_no}) registered successfully.", "success")
    return redirect(url_for("admin.students"))

@admin_bp.route("/students/edit/<int:student_id>", methods=["POST"])
@login_required
@admin_required
def edit_student(student_id):
    student = db.session.get(Student, student_id)
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for("admin.students"))

    student.user.name = request.form.get("name", student.user.name).strip()
    student.phone = request.form.get("phone", student.phone).strip()
    student.course = request.form.get("course", student.course).strip()
    student.semester = request.form.get("semester", type=int, default=student.semester)
    student.department_id = request.form.get("department_id", type=int, default=student.department_id)
    student.account_status = request.form.get("account_status", student.account_status)

    db.session.commit()
    flash(f"Student details updated for {student.roll_no}.", "success")
    return redirect(url_for("admin.students"))

@admin_bp.route("/students/toggle-status/<int:student_id>", methods=["POST"])
@login_required
@admin_required
def toggle_student_status(student_id):
    student = db.session.get(Student, student_id)
    if student and student.user:
        student.user.active = not student.user.active
        student.account_status = "Active" if student.user.active else "Inactive"
        db.session.commit()
        status_text = "activated" if student.user.active else "deactivated"
        flash(f"Student {student.roll_no} {status_text}.", "info")
    return redirect(url_for("admin.students"))

@admin_bp.route("/students/delete/<int:student_id>", methods=["POST"])
@login_required
@admin_required
def delete_student(student_id):
    student = db.session.get(Student, student_id)
    if student:
        user = student.user
        db.session.delete(student)
        if user:
            db.session.delete(user)
        db.session.commit()
        flash("Student record permanently deleted.", "warning")
    return redirect(url_for("admin.students"))

# ----------------- Faculty Management -----------------
@admin_bp.route("/faculty", methods=["GET"])
@login_required
@admin_required
def faculty():
    faculty_members = Faculty.query.all()
    departments = Department.query.all()
    subjects = Subject.query.all()
    return render_template("faculty.html", faculty=faculty_members, departments=departments, subjects=subjects)

@admin_bp.route("/faculty/create", methods=["POST"])
@login_required
@admin_required
def create_faculty():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    emp_id = request.form.get("employee_id", "").strip().upper()
    dept_id = request.form.get("department_id", type=int)
    designation = request.form.get("designation", "Assistant Professor").strip()
    qualification = request.form.get("qualification", "M.Tech / Ph.D").strip()
    phone = request.form.get("phone", "").strip()

    if not validate_email_format(email):
        flash("Invalid email format.", "danger")
        return redirect(url_for("admin.faculty"))

    if User.query.filter_by(email=email).first():
        flash("Email is already registered.", "danger")
        return redirect(url_for("admin.faculty"))

    if Faculty.query.filter_by(employee_id=emp_id).first():
        flash(f"Employee ID {emp_id} is already in use.", "danger")
        return redirect(url_for("admin.faculty"))

    user = User(name=name, email=email, role="faculty", phone=phone, active=True)
    user.set_password(password or "Faculty@123")
    db.session.add(user)
    db.session.flush()

    faculty_member = Faculty(
        user_id=user.id,
        employee_id=emp_id,
        department_id=dept_id,
        designation=designation,
        qualification=qualification,
        phone=phone,
        status="Active"
    )
    db.session.add(faculty_member)
    db.session.commit()

    flash(f"Faculty member {name} ({emp_id}) added successfully.", "success")
    return redirect(url_for("admin.faculty"))

@admin_bp.route("/faculty/edit/<int:faculty_id>", methods=["POST"])
@login_required
@admin_required
def edit_faculty(faculty_id):
    f = db.session.get(Faculty, faculty_id)
    if f:
        f.user.name = request.form.get("name", f.user.name).strip()
        f.designation = request.form.get("designation", f.designation).strip()
        f.qualification = request.form.get("qualification", f.qualification).strip()
        f.phone = request.form.get("phone", f.phone).strip()
        f.department_id = request.form.get("department_id", type=int, default=f.department_id)
        db.session.commit()
        flash(f"Faculty {f.employee_id} details updated.", "success")
    return redirect(url_for("admin.faculty"))

@admin_bp.route("/faculty/toggle-status/<int:faculty_id>", methods=["POST"])
@login_required
@admin_required
def toggle_faculty_status(faculty_id):
    f = db.session.get(Faculty, faculty_id)
    if f and f.user:
        f.user.active = not f.user.active
        f.status = "Active" if f.user.active else "Inactive"
        db.session.commit()
        flash(f"Faculty account status updated.", "info")
    return redirect(url_for("admin.faculty"))

# ----------------- Subject & Department Management -----------------
@admin_bp.route("/subjects", methods=["GET"])
@login_required
@admin_required
def subjects():
    all_subjects = Subject.query.order_by(Subject.semester.asc(), Subject.code.asc()).all()
    departments = Department.query.all()
    all_faculty = Faculty.query.all()
    return render_template("subjects.html", subjects=all_subjects, departments=departments, faculty=all_faculty)

@admin_bp.route("/departments/create", methods=["POST"])
@login_required
@admin_required
def create_department():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    desc = request.form.get("description", "").strip()

    if Department.query.filter((Department.name == name) | (Department.code == code)).first():
        flash("Department name or code already exists.", "danger")
    else:
        dept = Department(name=name, code=code, description=desc)
        db.session.add(dept)
        db.session.commit()
        flash(f"Department {name} ({code}) created.", "success")

    return redirect(url_for("admin.subjects"))

@admin_bp.route("/subjects/create", methods=["POST"])
@login_required
@admin_required
def create_subject():
    name = request.form.get("name", "").strip()
    code = request.form.get("code", "").strip().upper()
    semester = request.form.get("semester", type=int, default=1)
    dept_id = request.form.get("department_id", type=int)
    credits = request.form.get("credits", type=int, default=4)

    if Subject.query.filter_by(code=code).first():
        flash(f"Subject code {code} already exists.", "danger")
    else:
        sub = Subject(name=name, code=code, semester=semester, department_id=dept_id, credits=credits)
        db.session.add(sub)
        db.session.commit()
        flash(f"Subject {name} ({code}) added.", "success")

    return redirect(url_for("admin.subjects"))

@admin_bp.route("/subjects/assign-faculty", methods=["POST"])
@login_required
@admin_required
def assign_faculty_subject():
    faculty_id = request.form.get("faculty_id", type=int)
    subject_id = request.form.get("subject_id", type=int)
    academic_year = request.form.get("academic_year", "2026-2027")

    existing = FacultySubject.query.filter_by(
        faculty_id=faculty_id, subject_id=subject_id, academic_year=academic_year
    ).first()

    if existing:
        flash("Faculty is already assigned to this subject for this academic year.", "warning")
    else:
        sub = db.session.get(Subject, subject_id)
        fs = FacultySubject(
            faculty_id=faculty_id,
            subject_id=subject_id,
            academic_year=academic_year,
            semester=sub.semester if sub else 1
        )
        db.session.add(fs)
        db.session.commit()
        flash("Faculty successfully assigned to subject.", "success")

    return redirect(url_for("admin.subjects"))

# ----------------- Threshold Settings & Alerts -----------------
@admin_bp.route("/settings/thresholds", methods=["POST"])
@login_required
@admin_required
def update_thresholds():
    att = request.form.get("attendance_threshold", type=float, default=75.0)
    pass_mark = request.form.get("academic_pass_threshold", type=float, default=40.0)
    good_mark = request.form.get("academic_good_threshold", type=float, default=75.0)

    analytics_service.update_thresholds(att, pass_mark, good_mark)
    flash(f"Academic risk thresholds updated: Attendance Min={att}%, Pass={pass_mark}%, Good={good_mark}%.", "success")
    return redirect(url_for("admin.dashboard"))

@admin_bp.route("/audit-attendance", methods=["POST"])
@login_required
@admin_required
def audit_attendance():
    thresholds = analytics_service.get_thresholds()
    low_att = attendance_service.get_low_attendance_students(threshold=thresholds["attendance_threshold"])
    count = notification_service.send_bulk_attendance_alerts(low_att)
    flash(f"Attendance audit executed. {count} warning notifications dispatched.", "info")
    return redirect(url_for("admin.dashboard"))
