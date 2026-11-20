import unittest
from datetime import date
from app import create_app, db
from app.models import Student, Subject, Mark
from app.utils.validators import validate_marks_entry
from app.services.analytics_service import analytics_service
from config.config import TestingConfig

class TestMarksModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_marks_validation(self):
        # Valid: 45 out of 50
        is_valid, _ = validate_marks_entry(45.0, 50.0)
        self.assertTrue(is_valid)

        # Invalid: Obtained exceeds maximum (55 out of 50)
        is_invalid, msg = validate_marks_entry(55.0, 50.0)
        self.assertFalse(is_invalid)
        self.assertIn("cannot exceed maximum", msg)

        # Invalid: Negative marks
        is_negative, _ = validate_marks_entry(-5.0, 50.0)
        self.assertFalse(is_negative)

        # Invalid: Zero maximum
        is_zero_max, _ = validate_marks_entry(10.0, 0.0)
        self.assertFalse(is_zero_max)

    def test_grade_calculation(self):
        self.assertEqual(analytics_service.calculate_grade(95.0), "A+")
        self.assertEqual(analytics_service.calculate_grade(82.0), "A")
        self.assertEqual(analytics_service.calculate_grade(74.0), "B+")
        self.assertEqual(analytics_service.calculate_grade(65.0), "B")
        self.assertEqual(analytics_service.calculate_grade(52.0), "C")
        self.assertEqual(analytics_service.calculate_grade(45.0), "D")
        self.assertEqual(analytics_service.calculate_grade(32.0), "F")

if __name__ == "__main__":
    unittest.main()
