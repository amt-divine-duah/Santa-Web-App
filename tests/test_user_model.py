import unittest
from app import create_app, db
from models import User
import time

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
        
    # valid account confirmation token tests
    def test_valid_confirmation_token(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm_token(token))
        
    # Invalid account confirmation token tests
    def test_invalid_confirmation_token(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        u2 = User(password='cat', username='def', email='def@email.com')
        db.session.add(u)
        db.session.add(u2)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertFalse(u2.confirm_token(token))
        
    # Expired account confirmation token
    def test_expired_confirmation_token(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(expiration=1)
        # sleep for 15 secs because of leeway of 10s in jwt
        time.sleep(15)
        self.assertFalse(u.confirm_token(token))
        
    # valid password reset toke
    def test_valid_password_reset_token(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_password_reset_token()
        self.assertTrue(u.confirm_password_reset_token(token, 'dog'))
        self.assertTrue(u.verify_password('dog'))
    
    def test_invalid_password_reset_token(self):
        u = User(password='cat', username='abc', email='abc@email.com')
        db.session.add(u)
        db.session.commit()
        token = u.generate_password_reset_token()
        self.assertFalse(u.confirm_password_reset_token(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))
        