"""
Server Angel Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application Configuration."""

    # ============================
    # PROJECT SETTINGS
    # ============================
    # Root directory of the Server Angel project
    PROJECT_ROOT = os.getenv('PROJECT_ROOT', '<ABSOLUTE_PATH_TO_PROJECT_ROOT>')
    
    # Path to the Python Virtual Environment
    VENV_PATH = os.getenv('VENV_PATH', '<ABSOLUTE_PATH_TO_VENV>')

    # ============================
    # SERVICES TO MONITOR
    # ============================
    # Systemd service names to monitor and restart
    NGINX_SERVICE = os.getenv('NGINX_SERVICE', 'nginx')
    GUNICORN_SERVICE = os.getenv('GUNICORN_SERVICE', 'gunicorn')
    REDIS_SERVICE = os.getenv('REDIS_SERVICE', 'redis')
    CELERY_SERVICE = os.getenv('CELERY_SERVICE', 'celery')

    # ============================
    # EXTERNAL SERVICES
    # ============================
    DATABASE_URL = os.getenv('DATABASE_URL', '<YOUR_DATABASE_URL>')
    REDIS_URL = os.getenv('REDIS_URL', '<YOUR_REDIS_URL>')
    
    # ============================
    # EMAIL ALERTS
    # ============================
    # SMTP Configuration for sending reports
    SMTP_HOST = os.getenv('SMTP_HOST', '<YOUR_SMTP_HOST>')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '<YOUR_SMTP_USER>')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '<YOUR_SMTP_PASSWORD>')
    
    # Email Headers
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'server-angel@example.com')
    # Comma separated list of recipients
    EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', 'admin@example.com').split(',')

    # ============================
    # GIT WATCHER
    # ============================
    GIT_REMOTE = os.getenv('GIT_REMOTE', 'origin')
    GIT_BRANCH = os.getenv('GIT_BRANCH', 'main')

    # ============================
    # REPORTING SCHEDULE
    # ============================
    MORNING_REPORT = os.getenv('MORNING_REPORT', '08:00')
    EVENING_REPORT = os.getenv('EVENING_REPORT', '20:00')

    @classmethod
    def validate(cls):
        """Validate that required configuration is set."""
        required = [
            'PROJECT_ROOT', 'VENV_PATH', 'SMTP_HOST', 'SMTP_USER', 
            'SMTP_PASSWORD', 'EMAIL_RECIPIENTS'
        ]

        missing = []
        for attr in required:
            value = getattr(cls, attr)
            if isinstance(value, str) and value.startswith('<') and value.endswith('>'):
                missing.append(attr)

        if missing:
            raise ValueError(
                f"Required configuration not set: {', '.join(missing)}.\n"
                f"Please create a .env file or set environment variables."
            )
        return True
