
import os

from dotenv import load_dotenv
load_dotenv()

from .base import *

COVERAGE_MODULE_EXCLUDES = [
    'tests$', 'settings$', 'urls$', 'locale$',
    'migrations', 'fixtures', 'admin$',
]

COVERAGE_REPORT_HTML_OUTPUT_DIR = "coverage"

SECRET_KEY = os.getenv("SECRET_KEY")