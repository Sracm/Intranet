import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mq-professional-intranet-secure-token-2026')
    DATABASE = os.path.join(BASE_DIR, 'intranet.db')
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5080))
    DEBUG = True
