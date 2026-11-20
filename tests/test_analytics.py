import unittest
from app import create_app, db
from app.models import Student
from app.services.analytics_service import analytics_service
from config.config import TestingConfig

class TestAnalyticsModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_risk_classification_rules(self):
        # Verify classification across seeded students
        students = Student.query.all()
        categories_found = set()

        for s in students:
            risk = analytics_service.classify_student_risk(s.id)
            self.assertIn("category", risk)
            self.assertIn("badge_class", risk)
            self.assertIn("recommended_action", risk)
            categories_found.add(risk["category"])

        # Ensure our rich seeded dataset covers the primary academic risk categories
        self.assertTrue(any(c in categories_found for c in ["GOOD", "ATTENDANCE RISK", "ACADEMIC RISK", "HIGH RISK"]))

    def test_college_analytics_summary(self):
        stats = analytics_service.get_college_analytics()
        self.assertGreaterEqual(stats["total_students"], 1)
        self.assertGreaterEqual(stats["total_faculty"], 1)
        self.assertGreaterEqual(stats["total_subjects"], 1)
        self.assertTrue(0.0 <= stats["overall_attendance"] <= 100.0)
        self.assertTrue(0.0 <= stats["overall_performance"] <= 100.0)

if __name__ == "__main__":
    unittest.main()
