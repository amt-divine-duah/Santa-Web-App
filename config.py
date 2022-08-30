import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    pass

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