import os
from datetime import date, datetime, timedelta
import random
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from dotenv import load_dotenv

from config.config import Config, DevelopmentConfig, ProductionConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access the Student Analytics Cloud platform."
login_manager.login_message_category = "warning"

def create_app(config_class=None):
    if config_class is None:
        config_class = DevelopmentConfig if os.getenv("FLASK_ENV") == "development" else Config

    flask_app = Flask(__name__)
    flask_app.config.from_object(config_class)

    # Ensure reports directory exists
    os.makedirs(flask_app.config.get("REPORTS_DIR", "reports"), exist_ok=True)

    db.init_app(flask_app)
    login_manager.init_app(flask_app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.faculty import faculty_bp
    from app.routes.student import student_bp
    from app.routes.attendance import attendance_bp
    from app.routes.marks import marks_bp
    from app.routes.analytics import analytics_bp
    from app.routes.reports import reports_bp

    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(faculty_bp)
    flask_app.register_blueprint(student_bp)
    flask_app.register_blueprint(attendance_bp)
    flask_app.register_blueprint(marks_bp)
    flask_app.register_blueprint(analytics_bp)
    flask_app.register_blueprint(reports_bp)

    @flask_app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "faculty":
                return redirect(url_for("faculty.dashboard"))
            else:
                return redirect(url_for("student.dashboard"))
        return redirect(url_for("auth.login"))

    with flask_app.app_context():
        from app import models as _models  # ensure models are discovered
        db.create_all()
        seed_comprehensive_demo_data()

    return flask_app

def seed_comprehensive_demo_data():
    from app.models import User, Department, Course, Semester, Subject, Faculty, FacultySubject, Student, Attendance, Mark, SystemSetting

    # If database is already populated, skip
    if User.query.first():
        return

    print("Seeding comprehensive college dataset...")

    # 1. System Settings
    SystemSetting.set_value("ATTENDANCE_THRESHOLD", "75.0", "Minimum attendance required (%)")
    SystemSetting.set_value("ACADEMIC_PASS_THRESHOLD", "40.0", "Academic passing threshold (%)")
    SystemSetting.set_value("ACADEMIC_GOOD_THRESHOLD", "75.0", "Academic distinction threshold (%)")

    # 2. Departments
    dept_cse = Department(name="Computer Science & Engineering", code="CSE", description="Department of Computer Science and Engineering")
    dept_it = Department(name="Information Technology", code="IT", description="Department of Information Technology")
    db.session.add_all([dept_cse, dept_it])
    db.session.flush()

    # 3. Courses & Semesters
    course_btech_cse = Course(name="B.Tech Computer Science & Engineering", code="BTECH-CSE", department_id=dept_cse.id, duration_years=4)
    db.session.add(course_btech_cse)
    db.session.flush()

    for s_num in range(1, 9):
        sem = Semester(course_id=course_btech_cse.id, semester_number=s_num, academic_year="2026-2027")
        db.session.add(sem)

    # 4. Subjects
    sub1 = Subject(name="Cloud Computing & Distributed Systems", code="CS501", semester=5, department_id=dept_cse.id, credits=4)
    sub2 = Subject(name="Database Management Systems", code="CS502", semester=5, department_id=dept_cse.id, credits=4)
    sub3 = Subject(name="Machine Learning & Data Mining", code="CS503", semester=5, department_id=dept_cse.id, credits=4)
    sub4 = Subject(name="Computer Networks & Security", code="CS504", semester=5, department_id=dept_cse.id, credits=3)
    sub5 = Subject(name="Software Engineering & Agile", code="CS505", semester=5, department_id=dept_cse.id, credits=3)
    db.session.add_all([sub1, sub2, sub3, sub4, sub5])
    db.session.flush()

    # 5. Admin User
    admin_user = User(name="Dr. Arthur Vance (Dean/Admin)", email="admin@demo.com", role="admin", phone="+91 98765 43210")
    admin_user.set_password("Admin@123")
    db.session.add(admin_user)
    db.session.flush()

    # 6. Faculty Members
    faculty_list = [
        {"name": "Prof. Marcus Thorne", "email": "faculty@demo.com", "emp_id": "FAC101", "desig": "Professor & Head", "subject": sub1},
        {"name": "Dr. Elena Rostova", "email": "elena@demo.com", "emp_id": "FAC102", "desig": "Associate Professor", "subject": sub2},
        {"name": "Prof. David Chen", "email": "david@demo.com", "emp_id": "FAC103", "desig": "Assistant Professor", "subject": sub3},
    ]

    fac_objs = []
    for f_info in faculty_list:
        u = User(name=f_info["name"], email=f_info["email"], role="faculty", phone="+91 98765 00001")
        u.set_password("Faculty@123")
        db.session.add(u)
        db.session.flush()

        fac = Faculty(
            user_id=u.id,
            employee_id=f_info["emp_id"],
            department_id=dept_cse.id,
            designation=f_info["desig"],
            qualification="Ph.D. in Computer Science",
            status="Active"
        )
        db.session.add(fac)
        db.session.flush()
        fac_objs.append(fac)

        # Assign subject
        fs = FacultySubject(
            faculty_id=fac.id,
            subject_id=f_info["subject"].id,
            academic_year="2026-2027",
            semester=5
        )
        db.session.add(fs)

    # 7. Students (Diverse profiles to represent all risk profiles)
    students_info = [
        # GOOD: High attendance (>=75%) + High marks (>=75%)
        {"name": "Demo Student", "email": "student@demo.com", "roll": "CSE2024001", "phone": "+91 91234 56701", "att_rate": 0.90, "marks_rate": 0.88},
        {"name": "Emma Watson", "email": "emma@demo.com", "roll": "CSE2024002", "phone": "+91 91234 56702", "att_rate": 0.95, "marks_rate": 0.92},
        {"name": "Liam Nelson", "email": "liam@demo.com", "roll": "CSE2024003", "phone": "+91 91234 56703", "att_rate": 0.85, "marks_rate": 0.81},

        # ATTENDANCE RISK: Low attendance (<75%) + High marks (>=75%)
        {"name": "Rahul Sharma", "email": "rahul@demo.com", "roll": "CSE2024004", "phone": "+91 91234 56704", "att_rate": 0.60, "marks_rate": 0.84},
        {"name": "Priya Nair", "email": "priya@demo.com", "roll": "CSE2024005", "phone": "+91 91234 56705", "att_rate": 0.65, "marks_rate": 0.78},

        # ACADEMIC RISK: High attendance (>=75%) + Low marks (<40%)
        {"name": "John Doe", "email": "john@demo.com", "roll": "CSE2024006", "phone": "+91 91234 56706", "att_rate": 0.88, "marks_rate": 0.35},
        {"name": "Aarav Patel", "email": "aarav@demo.com", "roll": "CSE2024007", "phone": "+91 91234 56707", "att_rate": 0.82, "marks_rate": 0.38},

        # HIGH RISK: Low attendance (<75%) + Low marks (<40%)
        {"name": "Vikram Singh", "email": "vikram@demo.com", "roll": "CSE2024008", "phone": "+91 91234 56708", "att_rate": 0.45, "marks_rate": 0.32},
        {"name": "Chloe Bennett", "email": "chloe@demo.com", "roll": "CSE2024009", "phone": "+91 91234 56709", "att_rate": 0.50, "marks_rate": 0.28},

        # MODERATE PROGRESS: High attendance (>=75%) + Moderate marks (40% - 74%)
        {"name": "Carlos Gomez", "email": "carlos@demo.com", "roll": "CSE2024010", "phone": "+91 91234 56710", "att_rate": 0.80, "marks_rate": 0.62},
        {"name": "Ananya Roy", "email": "ananya@demo.com", "roll": "CSE2024011", "phone": "+91 91234 56711", "att_rate": 0.78, "marks_rate": 0.68},
    ]

    all_subjects = [sub1, sub2, sub3, sub4, sub5]
    created_students = []

    for s_info in students_info:
        u = User(name=s_info["name"], email=s_info["email"], role="student", phone=s_info["phone"])
        u.set_password("Student@123")
        db.session.add(u)
        db.session.flush()

        st = Student(
            user_id=u.id,
            roll_no=s_info["roll"],
            department_id=dept_cse.id,
            course="B.Tech Computer Science",
            semester=5,
            phone=s_info["phone"],
            admission_year=2024,
            account_status="Active"
        )
        db.session.add(st)
        db.session.flush()
        created_students.append((st, s_info))

    # 8. Multi-date Attendance Records (past 20 weekdays)
    base_date = date.today() - timedelta(days=35)
    attendance_dates = []
    curr = base_date
    while len(attendance_dates) < 20:
        if curr.weekday() < 5:  # Monday to Friday
            attendance_dates.append(curr)
        curr += timedelta(days=1)

    random.seed(42)
    for a_date in attendance_dates:
        for sub in all_subjects[:3]:  # Generate records for 3 core subjects
            for st, s_info in created_students:
                is_present = random.random() < s_info["att_rate"]
                status = "Present" if is_present else "Absent"
                att = Attendance(
                    student_id=st.id,
                    subject_id=sub.id,
                    date=a_date,
                    session="Regular",
                    status=status,
                    marked_by=fac_objs[0].user_id
                )
                db.session.add(att)

    # 9. Academic Marks (Midterm 1, Midterm 2, Internal Exam)
    exam_types = [
        {"type": "Midterm 1", "max": 50.0, "date": date.today() - timedelta(days=25)},
        {"type": "Midterm 2", "max": 50.0, "date": date.today() - timedelta(days=10)},
        {"type": "Internal Assignment", "max": 25.0, "date": date.today() - timedelta(days=5)},
    ]

    for exam in exam_types:
        for sub in all_subjects[:3]:
            for st, s_info in created_students:
                # Calculate marks proportional to rate + small random variance
                target_ratio = s_info["marks_rate"] + random.uniform(-0.05, 0.05)
                target_ratio = max(0.15, min(0.98, target_ratio))
                obtained = round(target_ratio * exam["max"], 1)

                m = Mark(
                    student_id=st.id,
                    subject_id=sub.id,
                    exam_type=exam["type"],
                    marks_obtained=obtained,
                    max_marks=exam["max"],
                    exam_date=exam["date"],
                    entered_by=fac_objs[0].user_id
                )
                db.session.add(m)

    db.session.commit()
    print("Database seeding completed with 11 students across all risk levels and 20 attendance sessions!")
