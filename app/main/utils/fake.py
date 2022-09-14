from random import randint
from faker import Faker
from models import User, Post
from app import db

# Function to create multiple users
def users(count=20):
    fake = Faker()
    i = 0
    while i < count:
        user = User(email=fake.email(), username=fake.user_name(), password='123456', 
                    confirmed=True, first_name=fake.name(), last_name=fake.name(), 
                    address=fake.city(), bio=fake.text())
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except Exception as e:
            print(e)
            db.session.rollback()
            
#Function to create multiple posts
def create_posts(count=25):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        user = User.query.offset(randint(0, user_count-1)).first()
        post = Post(title=fake.name(), body_html=fake.text(), 
                    timestamp=fake.past_date(), author=user)
        db.session.add(post)
    db.session.commit()