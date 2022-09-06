import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SERVER_NAME = 'localhost:5000'
    
    # Email Config
    MAIL_PORT = 587
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SANTA_ADMIN = os.environ.get('SANTA_ADMIN')
    MAIL_SUBJECT_PREFIX = '[Santa-Blog]'
    MAIL_SENDER = 'Santa-Blog Admin <sblog@gmail.com>'
    
    # Posts per page
    BLOG_POSTS_PER_PAGE = 9
    
    # Celery Config
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:pg1234@localhost/myprojectdb"

class TestingConfig(Config):
    pass

class ProductionConfig(Config):
    pass

# Create a dictionary for config values
config = {
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    
}