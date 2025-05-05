import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

STATIC_FOLDER = os.path.join(BASEDIR, 'app', 'static')
TEMPLATE_FOLDER = os.path.join(BASEDIR, 'app', 'templates')


class Config:
    FLASK_DEBUG = 1
    SESSION_TYPE = "filesystem"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///banco.db"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
