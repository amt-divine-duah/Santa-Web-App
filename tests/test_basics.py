import unittest
from flask import current_app
from app import create_app, db

class BasicsTestCase(unittest.TestCase):
    # Create setUp and tearDown methods
    def setUp(self):
        self.app = create_app('testing')
        self.app.app_context = self.app.app_context()
        self.app.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app.app_context.pop()
    
    # Define tests
    def test_app_exists(self):
        self.assertFalse(current_app is None)
    
    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
        
    
        