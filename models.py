from app import db, login_manager, admin
from flask import redirect, url_for, request, flash
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, current_user
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView


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
 
# Create a Logout view
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('auth.logout'))
    
# Protect ModelView
class MyModelView(ModelView):
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        flash("Log in to access the page", 'warning')
        return redirect(url_for('auth.login', next=request.url))


# Create a login route for adminview
class MyAdminIndexView(AdminIndexView):
    
    def is_accessible(self):
        return current_user.is_authenticated
    
    
    def inaccessible_callback(self, name, **kwargs):
        flash("Log in to access page", 'warning')
        return redirect(url_for('auth.login', next=request.url))

# Register Views
admin.add_view(MyModelView(User, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))
