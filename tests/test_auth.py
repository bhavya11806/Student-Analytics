import unittest
from app import create_app, db
from app.models import User, Student, Department
from config.config import TestingConfig

class TestAuthModule(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_user_password_hashing(self):
        u = User(name="Test User", email="test@college.edu", role="student")
        u.set_password("SecurePassword123")
        self.assertNotEqual(u.password_hash, "SecurePassword123")
        self.assertTrue(u.check_password("SecurePassword123"))
        self.assertFalse(u.check_password("WrongPassword"))

    def test_admin_login_success(self):
        # Admin is automatically seeded
        response = self.client.post("/login", data={
            "email": "admin@demo.com",
            "password": "Admin@123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"College Executive Dashboard", response.data)

    def test_faculty_login_success(self):
        response = self.client.post("/login", data={
            "email": "faculty@demo.com",
            "password": "Faculty@123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Faculty Teaching", response.data)

    def test_student_login_success(self):
        response = self.client.post("/login", data={
            "email": "student@demo.com",
            "password": "Student@123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"My Academic Dashboard", response.data)

    def test_invalid_login_failure(self):
        response = self.client.post("/login", data={
            "email": "admin@demo.com",
            "password": "IncorrectPassword"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", response.data)

    def test_unauthorized_access_protection(self):
        # Student cannot access /admin/dashboard
        self.client.post("/login", data={
            "email": "student@demo.com",
            "password": "Student@123"
        }, follow_redirects=True)

        admin_page_response = self.client.get("/admin/dashboard")
        self.assertEqual(admin_page_response.status_code, 403)

if __name__ == "__main__":
    unittest.main()
