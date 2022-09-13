import unittest
from app import create_app, db
from models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.app_context = self.app.app_context()
        self.app.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app.app_context.pop()
        
    """Define Tests"""
    
    # password setter test
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)
    
    #password getter test 
    def test_no_password_getter(self):
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password
            
    # password verification
    def test_verify_password(self):
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))
    
    # random salts password
    def test_password_salts_are_random(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        u2 = User(password='cat', username='def', email='def@email.com')
        self.assertTrue(u.password_hash != u2.password_hash)