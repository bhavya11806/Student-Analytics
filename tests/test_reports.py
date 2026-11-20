import os
import unittest
from app import create_app, db
from app.models import Student
from app.services.report_service import report_service
from config.config import TestingConfig

class TestReportsModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_student_attendance_pdf_generation(self):
        student = Student.query.first()
        filepath, report_rec = report_service.generate_student_attendance_pdf(student.id, 1)

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".pdf"))
        self.assertGreater(os.path.getsize(filepath), 1000)
        self.assertEqual(report_rec.report_type, "attendance_pdf")

    def test_student_performance_pdf_generation(self):
        student = Student.query.first()
        filepath, report_rec = report_service.generate_student_performance_pdf(student.id, 1)

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".pdf"))
        self.assertGreater(os.path.getsize(filepath), 1000)
        self.assertEqual(report_rec.report_type, "performance_pdf")

    def test_master_attendance_excel_generation(self):
        filepath, report_rec = report_service.generate_attendance_excel(generated_by_user_id=1)

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".xlsx"))
        self.assertGreater(os.path.getsize(filepath), 1000)
        self.assertEqual(report_rec.report_type, "attendance_excel")

    def test_academic_performance_excel_generation(self):
        filepath, report_rec = report_service.generate_performance_excel(generated_by_user_id=1)

        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".xlsx"))
        self.assertGreater(os.path.getsize(filepath), 1000)
        self.assertEqual(report_rec.report_type, "performance_excel")

if __name__ == "__main__":
    unittest.main()
