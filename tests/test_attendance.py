import unittest
from datetime import date, timedelta
from app import create_app, db
from app.models import Student, Subject, Attendance
from app.services.attendance_service import attendance_service
from config.config import TestingConfig

class TestAttendanceModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_duplicate_attendance_prevention_and_update(self):
        student = Student.query.first()
        subject = Subject.query.first()
        today = date.today()

        # 1. First record: Present
        record1, created1 = attendance_service.mark_attendance(
            student_id=student.id,
            subject_id=subject.id,
            att_date=today,
            session="Regular",
            status="Present",
            marked_by=1
        )
        self.assertEqual(record1.status, "Present")

        # 2. Second record on exact same (student, subject, date, session) should UPDATE, not create duplicate
        record2, created2 = attendance_service.mark_attendance(
            student_id=student.id,
            subject_id=subject.id,
            att_date=today,
            session="Regular",
            status="Absent",
            marked_by=1
        )
        self.assertFalse(created2)
        self.assertEqual(record2.id, record1.id)
        self.assertEqual(record2.status, "Absent")

    def test_attendance_percentage_calculation(self):
        student = Student.query.first()
        summary = attendance_service.get_student_attendance_summary(student.id)

        self.assertIn("overall_percentage", summary)
        self.assertIn("total_conducted", summary)
        self.assertIn("total_present", summary)

        if summary["total_conducted"] > 0:
            expected = round((summary["total_present"] / summary["total_conducted"]) * 100, 2)
            self.assertEqual(summary["overall_percentage"], expected)

if __name__ == "__main__":
    unittest.main()
