import jwt
from datetime import datetime, timedelta, timezone
from app import db, login_manager, admin
from flask import redirect, url_for, request, flash, current_app, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin, current_user, AnonymousUserMixin
from flask_admin import AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import event
from slugify import slugify
from app.exceptions import ValidationError
import bleach


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

# Follows association table as a model
class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    date_followed = db.Column(db.DateTime, default=datetime.utcnow)


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
    header = db.Column(db.String(120), default='header.jpg')
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], 
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    # Role Assignment
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['SANTA_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
                
        # making users their own followers when they are created
        self.follow(self)
                
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
    
    # token based authentication support
    def generate_auth_token(self, expiration):
        token = jwt.encode(payload={
            'token_id': self.id,
            'exp': datetime.now(tz=timezone.utc) + timedelta(seconds=expiration)
        },
        key=current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return token
    
    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(jwt=token, key=current_app.config['SECRET_KEY'], 
                              algorithms=["HS256"])
        except Exception as e:
            return None
        return User.query.get(data.get('token_id'))
    
    """Followers helpers method"""
    # Check whether a user is following another user
    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    # Follow a user
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            
    # Unfollow a user
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            
    # Check for followers
    def is_followed_by(self, user):
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).\
                filter(Follow.follower_id==self.id)
    
    # making users their own followers
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    
    # Convert a user to a serializable dictionary
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'posts_url': url_for('api.get_posts', id=self.id),
            'followed_posts_url': url_for('api.get_user_followed_posts', id=self.id),
            'post_count': self.posts.count()
        }
        
        return json_user
    
    def __repr__(self):
        return "<User %r>" %self.email

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    slug = db.Column(db.String(180))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Slugify posts
    @staticmethod
    def generate_slug(target, value, oldvalue, initiator):
        if value and (not target.slug or value != oldvalue):
            target.slug = slugify(value)
    
    # Converting post to json serializable dictionary
    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id),
            'body': self.body,
            'slug': self.slug,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_post_comments', id=self.id),
            'comment_count': self.comments.count()
        }
        
        return json_post
    
    # Creating a blog post from a json (deserialization)
    @staticmethod
    def from_json(json_post):
        title = json_post.get('title')
        body = json_post.get('body')
        if (body is None or body == "") or (title is None or title == ""):
            raise ValidationError('post does have a body or title')
        return Post(title=title, body=body)
    
    # Cleaning HTML posts
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        target.body = bleach.linkify(bleach.clean(value, strip=True))
        
    
    def __repr__(self):
        return "<Post %r>" %self.title

db.event.listen(Post.title, 'set', Post.generate_slug, retval=False)
db.event.listen(Post.body_html, 'set', Post.on_changed_body, retval=False)

# Comments model
class Comment(db.Model):
    __tablename__ = "comments" 
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    comment_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

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

# Register Views
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Post, db.session))
admin.add_view(MyModelView(Follow, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))
