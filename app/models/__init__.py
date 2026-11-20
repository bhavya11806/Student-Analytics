from app.models.user import User, load_user
from app.models.department import Department, Course, Semester
from app.models.subject import Subject
from app.models.faculty import Faculty, FacultySubject
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.marks import Mark
from app.models.settings import Notification, AcademicReport, SystemSetting

__all__ = [
    "User",
    "load_user",
    "Department",
    "Course",
    "Semester",
    "Subject",
    "Faculty",
    "FacultySubject",
    "Student",
    "Attendance",
    "Mark",
    "Notification",
    "AcademicReport",
    "SystemSetting"
]
