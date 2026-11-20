import unittest
from app import create_app
from config.config import TestingConfig

class TestSmoke(unittest.TestCase):
    def test_app_initialization(self):
        app = create_app(TestingConfig)
        self.assertIsNotNone(app)
        self.assertTrue(app.config["TESTING"])
        self.assertTrue(app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"))

if __name__ == "__main__":
    unittest.main()
