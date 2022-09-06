import jwt
from datetime import datetime, timedelta, timezone
from app import db, login_manager, admin
from flask import redirect, url_for, request, flash, current_app, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, current_user, AnonymousUserMixin
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView


# User loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
# Permission Class
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16 

    
# Role Model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
            
    # Add methods to manage permissions
    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
            
    def reset_permissions(self):
        self.permissions = 0
    
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    # Create a method to add roles to the Role table
    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, 
                          Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, 
                              Permission.MODERATE, Permission.ADMIN]
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            # reset all permissions
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()
    
    def __repr__(self):
        return "<Role %r>" %self.name



# User Model
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(85), nullable=False, unique=True)
    first_name = db.Column(db.String(50))
    middle_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(150))
    confirmed = db.Column(db.Boolean, default=False)
    user_terms = db.Column(db.Boolean, default=False)
    address = db.Column(db.Text)
    job_title = db.Column(db.String(80))
    bio = db.Column(db.Text)
    mobile_no = db.Column(db.String(20))
    country = db.Column(db.String(50))
    image = db.Column(db.String(120), default='default.jpg')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    
    # Role Assignment
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SANTA_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                
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
    
    
    # Role verification
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)
    
    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
    
    # Generating Confirmation tokens
    def generate_confirmation_token(self, expiration=1800):
        confirmation_token = jwt.encode(payload={
                                        'confirm': self.id,
                                        'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=expiration)
                                        }, 
                                        key=current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return confirmation_token
    
    # Confirm token
    def confirm_token(self, token): 
        try:
            data = jwt.decode(token, key=current_app.config['SECRET_KEY'],
                              leeway=timedelta(seconds=10), algorithms=['HS256'])
        except Exception as e:
            return False
        # If token key matches the current user id
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    # Generate Password Reset Token
    def generate_password_reset_token(self, expiration=1800):
        reset_token = jwt.encode(payload={
                                'reset_token': self.id, 
                                'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=expiration)
                                },
                                 key=current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return reset_token
    
    @staticmethod
    def confirm_password_reset_token(token, new_password):
        try:
            data = jwt.decode(token, key=current_app.config['SECRET_KEY'], 
                              leeway=timedelta(seconds=10), algorithms=["HS256"])
        except Exception as e:
            return False
        # Get the user id
        user_id = data.get('reset_token')
        user = User.query.get(int(user_id))
        if user is None:
            return False
        # Reset password
        user.password = new_password
        db.session.add(user)
        return True
    
    # Email change token
    def generate_email_change_token(self, new_email, expiration=1800):
        token = jwt.encode(payload={
                                'email_token': self.id, 
                                'new_email': new_email, 
                                'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=expiration)
                                },
                                 key=current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return token
    
    # Confirm token for email change
    def change_email(self, token):
        try:
            data = jwt.decode(token, key=current_app.config['SECRET_KEY'], 
                              leeway=timedelta(seconds=10), algorithms=["HS256"])
        except Exception as e:
            return False
        if data.get('email_token') != self.id:
            return False
        # Get the new Email
        new_email = data.get('new_email')
        if new_email is None:
            return False
        # Check for existing email
        if User.query.filter_by(email=new_email.lower()).first() is not None:
            return False
        # Add new email
        self.email = new_email
        db.session.add(self)
        return True
    
    def __repr__(self):
        return "<User %r>" %self.email

# Anonymous class to check for Anonymous Permissions
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

# Create a Logout view
class LogoutView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for('auth.logout'))
    
# Protect ModelView
class MyModelView(ModelView):
    
    def is_accessible(self):
        return ((current_user.is_authenticated and current_user.role.name=='Administrator'))
    
    
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                # Deny permission
                abort(403)
            else:        
                flash("Log in to access page", 'warning')
                return redirect(url_for('auth.login', next=request.url))


# Create a login route for adminview
class MyAdminIndexView(AdminIndexView):
    
    def is_accessible(self):
        return ((current_user.is_authenticated and current_user.role.name=='Administrator'))
    
    
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            if current_user.is_authenticated:
                # Deny permission
                abort(403)
            else:        
                flash("Log in to access page", 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

# Register Views
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Post, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))
