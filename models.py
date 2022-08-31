from app import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    



# User Model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(85), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(150))
    user_terms = db.Column(db.Boolean, default=False)
    
    # Define property for password. Make it write only to prevent password from being read
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    # Set password
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    # Verify password
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    
    def __repr__(self):
        return "<User %r>" %self.email