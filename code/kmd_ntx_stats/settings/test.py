
import os

from dotenv import load_dotenv
load_dotenv()

from .base import *

COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$',
]
MIGRATE = False
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
COVERAGE_REPORT_HTML_OUTPUT_DIR = "coverage"

SECRET_KEY = os.getenv("SECRET_KEY")