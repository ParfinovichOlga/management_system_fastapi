import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
SECRET_KEY = os.environ.get('SECRET_KEY')
ALGORITM = os.environ.get('ALGORITM')
ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY')

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')
ADMIN_NAME = os.environ.get('ADMIN_NAME')

MODE = os.environ.get('MODE')
