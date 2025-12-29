"""
Server Angel Configuration Module
Loads environment variables with placeholders for open-source compatibility.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)



class Config:
    """Configuration class with placeholder values for open-sourcing."""

    # Project paths (REPLACE WITH YOUR ACTUAL PATHS)
    PROJECT_ROOT = os.getenv('PROJECT_ROOT', '<ABSOLUTE_PATH_TO_YOUR_PROJECT>')
    VENV_PATH = os.getenv('VENV_PATH', '<ABSOLUTE_PATH_TO_YOUR_VIRTUALENV>')

    # Git configuration
    GIT_REMOTE = os.getenv('GIT_REMOTE', 'origin')
    GIT_BRANCH = os.getenv('GIT_BRANCH', 'kwari_Production')

    # Service names (REPLACE WITH YOUR SYSTEMD SERVICE NAMES)
    NGINX_SERVICE = os.getenv('NGINX_SERVICE', '<YOUR_NGINX_SERVICE_NAME>')
    GUNICORN_SERVICE = os.getenv('GUNICORN_SERVICE', '<YOUR_GUNICORN_SERVICE_NAME>')
    REDIS_SERVICE = os.getenv('REDIS_SERVICE', '<YOUR_REDIS_SERVICE_NAME>')
    CELERY_SERVICE = os.getenv('CELERY_SERVICE', '<YOUR_CELERY_SERVICE_NAME>')

    # Email configuration
    SMTP_HOST = os.getenv('SMTP_HOST', '<YOUR_SMTP_HOST>')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER', '<YOUR_SMTP_USERNAME>')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '<YOUR_SMTP_PASSWORD>')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '<YOUR_FROM_EMAIL>')
    EMAIL_RECIPIENTS = os.getenv('EMAIL_RECIPIENTS', '<EMAIL1,EMAIL2>').split(',')

    # Reporting times
    MORNING_REPORT = os.getenv('MORNING_REPORT', '07:00')
    EVENING_REPORT = os.getenv('EVENING_REPORT', '19:00')

    # Server Angel paths
    ANGEL_ROOT = Path(__file__).parent
    STATE_DIR = ANGEL_ROOT / 'state'
    LOG_DIR = ANGEL_ROOT / 'logs'
    LAST_COMMIT_FILE = STATE_DIR / 'last_commit.txt'
    LOG_FILE = LOG_DIR / 'angel.log'

    @classmethod
    def validate(cls):
        """Validate that required placeholders have been replaced."""
        # Required configuration
        required = [
            'PROJECT_ROOT', 'VENV_PATH', 'NGINX_SERVICE', 'GUNICORN_SERVICE',
            'SMTP_HOST', 'SMTP_USER', 'SMTP_PASSWORD', 'EMAIL_FROM', 'EMAIL_RECIPIENTS'
        ]

        # Optional configuration (Redis and Celery are optional)
        optional = ['REDIS_SERVICE', 'CELERY_SERVICE']

        missing = []
        for attr in required:
            value = getattr(cls, attr)
            # Handle list values (like EMAIL_RECIPIENTS)
            if isinstance(value, list):
                value = ','.join(value)
            if isinstance(value, str) and value.startswith('<') and value.endswith('>'):
                missing.append(attr)

        if missing:
            raise ValueError(
                f"Required configuration not set: {', '.join(missing)}.\n"
                f"Please create a .env file or set environment variables.\n"
                f"See .env.example for template."
            )

        # Validate paths exist
        if not Path(cls.PROJECT_ROOT).exists():
            raise ValueError(f"PROJECT_ROOT does not exist: {cls.PROJECT_ROOT}")

        if not Path(cls.VENV_PATH).exists():
            raise ValueError(f"VENV_PATH does not exist: {cls.VENV_PATH}")

        # Validate Git repository
        git_dir = Path(cls.PROJECT_ROOT) / '.git'
        if not git_dir.exists():
            raise ValueError(
                f"PROJECT_ROOT is not a Git repository: {cls.PROJECT_ROOT}\n"
                f"Expected .git directory not found."
            )

        return True
