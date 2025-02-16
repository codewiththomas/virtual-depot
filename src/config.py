import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "zYSGWbG9JkpdnAdYd57tgPKxxdSeIxbI"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'depot.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
