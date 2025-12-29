# Server Angel Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-29

### 🎉 Major Upgrade - Production Ready Release

### Added
- **.env file support** using python-dotenv for easier configuration management
- **.env.example** template with comprehensive documentation for all settings
- **requirements.txt** file with all project dependencies
- **Retry logic** for Git operations (3 attempts with 5-second delays)
- **Enhanced logging** throughout all modules for better debugging
- **Comprehensive test suite** in `tests/test_basic.py`
- **SSL/TLS auto-detection** for SMTP based on port (465 vs 587)
- **Server hostname** in email reports for multi-server deployments
- **Git repository validation** during config validation
- **Service count statistics** in health reports
- **Detailed deployment step tracking** in deployment reports

### Fixed
- **CRITICAL**: Fixed `format_bytes` function in `health_checks.py` that was returning ".1f" string instead of actual formatted byte values
- **Configuration validation** now provides clearer error messages with instructions
- **SMTP connection** now properly handles both SSL (port 465) and TLS (port 587)
- **Git operations** now have proper timeout handling
- **Email reports** now show server hostname for easier identification

### Changed
- Configuration now automatically loads `.env` file if present
- Validation errors now reference `.env.example` for guidance
- Health reports now skip unconfigured services in the service list
- Deployment reports now include detailed step-by-step execution status
- All Git and deployment operations now include comprehensive logging
- Email subjects now include server hostname for multi-server setups

### Improved
- **Error handling**: Added retry mechanisms for transient failures
- **Logging**: Added logging.info/warning/error throughout codebase
- **Validation**: Configuration validation now checks Git repository exists
- **Documentation**: Enhanced inline comments and docstrings
- **Email formatting**: Better structured email reports with service counts
- **Deployment resilience**: 3-attempt retry for Git operations

### Technical Changes
- Added `python-dotenv>=1.0.0` dependency
- Added `psutil>=5.9.0` dependency (documented)
- Requires Python 3.8+
- All subprocess calls now have proper timeout handling
- Added comprehensive logging to deployer and git_watcher

## [1.0.0] - 2025-12-XX

### Initial Release
- Basic health monitoring (CPU, memory, disk, uptime)
- Service status checking (Nginx, Gunicorn, Redis, Celery)
- Git repository monitoring
- Auto-deployment on new commits
- Email notifications via SMTP
- Systemd service and timer configurations
