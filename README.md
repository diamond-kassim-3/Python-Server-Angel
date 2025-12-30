# 🛡️ Server Angel v2.01.1

**Standalone Server Automation Agent**

Server Angel monitors your server health and automatically deploys updates from your production Git branch. It sends daily health reports and deployment notifications via email.

## 🎉 What's New in v2.01.1

- 🎨 **HTML Email Reports**: Beautiful, responsive email templates with status badges and progress bars
- 🤖 **Automated Setup**: New `setup_server_angel.sh` script for interactive installation
- 🔧 **Dedicated Services**: Split architecture into `server-angel-health` and `server-angel-git` for better stability
- ✅ **Fixed Critical Bug**: `format_bytes` now shows actual memory/disk values instead of ".1f"
- 🔐 **.env File Support**: Easy configuration with environment files
- 🔄 **Retry Logic**: Automatic retry for transient Git failures (3 attempts)
- 📝 **Enhanced Logging**: Comprehensive logging throughout all operations
- 📧 **Better Emails**: Hostname in subjects, SSL/TLS auto-detection, detailed deployment reports
- 🧪 **Test Suite**: Automated tests to verify functionality
- 📚 **Better Docs**: Deployment guide, changelog, and improved documentation

> **Upgrading from v1.0?** See [CHANGELOG.md](CHANGELOG.md) for full details.

## ✨ Key Features

- **Daily Health Reports**: Automated server status emails at 7 AM and 7 PM (customizable)
- **Auto-Deployment**: Monitors Git branch and deploys changes automatically with retry logic
- **Smart Dependencies**: Updates Python packages only when `requirements.txt` changes
- **Service Management**: Restarts Nginx, Gunicorn, Redis, and Celery safely with verification
- **Email Notifications**: Clean, informative reports for health checks, deployments, and errors
- **Resilient Operations**: Automatic retry for transient failures
- **.env Configuration**: Easy setup with environment files
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 📁 Project Structure

```
server-angel/
│
├── angel.py              # Main orchestrator - Entry point for all operations
├── config.py             # Configuration with .env support and validation
├── health_checks.py      # System and service monitoring (CPU, RAM, Disk, Services)
├── git_watcher.py        # Git branch monitoring and commit detection
├── deployer.py           # Safe deployment with retry logic
├── reporter.py           # Email content builder with templates
├── mailer.py             # SMTP email sender with SSL/TLS auto-detection
│
├── .env.example          # Configuration template
├── requirements.txt      # Python dependencies
├── CHANGELOG.md          # Version history
├── DEPLOYMENT.md         # Deployment guide
│
├── state/
│   └── last_commit.txt   # Tracks deployed commits
├── logs/
│   └── angel.log         # Execution logs
│
├── setup_server_angel.sh   # Automated setup script (New in v2.01)
├── systemd/
│   ├── server-angel-health.service  # Health check service definition
│   ├── server-angel-git.service     # Git watcher service definition
│   ├── server-angel-health.timer    # Health check scheduler (7 AM & 7 PM)
│   └── server-angel-git.timer       # Git watch scheduler (every 5 min)
│
└── README.md
```

## 🏗️ Architecture

**Server Angel** operates in two distinct modes:

### 1. Health Check Mode
```
angel.py --mode=health-check
    ↓
[Health Checker] → Monitors system resources & services
    ↓
[Reporter] → Builds formatted email report
    ↓
[Mailer] → Sends via SMTP
```

**Monitors**:
- CPU usage percentage
- Memory usage (used/total)
- Disk space (used/total)
- Server uptime
- Service statuses (nginx, gunicorn, redis, celery)

### 2. Git Watch Mode
```
angel.py --mode=git-watch
    ↓
[Git Watcher] → Fetches remote & checks for new commits
    ↓
[Deployer] → Pulls changes, updates deps, restarts services
    ↓
[Reporter] → Builds deployment report
    ↓
[Mailer] → Sends notification
```

**Deployment Flow**:
1. Fetch from Git remote
2. Compare commits (remote vs last deployed)
3. If new commits: Pull latest changes
4. Check if requirements.txt changed
5. Update dependencies (if needed)
6. Restart services (nginx, gunicorn)
7. Verify services are running
8. Send email report

## 🎯 Use Cases

### Perfect For:
- **Django/Flask Applications**: Auto-deploy updates from Git
- **API Servers**: Monitor health and uptime
- **Production Environments**: Get notified of issues immediately
- **Small to Medium Teams**: Simple, reliable automation
- **Multi-Server Deployments**: Hostname in emails identifies which server

### Real-World Scenarios:

**Scenario 1: Continuous Deployment**
- Push code to production branch → Server Angel detects → Auto-deploys → Sends confirmation email

**Scenario 2: Server Monitoring**
- Receive health reports twice daily (7 AM & 7 PM)
- Get alerted if services fail or resources are high
- Monitor multiple servers from one email inbox

**Scenario 3: Deployment Tracking**
- Full audit trail of all deployments
- Email history shows when/what was deployed
- Deployment failures are immediately reported

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Create directory
sudo mkdir -p /var/www/server-angel
cd /var/www/server-angel

# Clone or copy files
# ... copy all Server Angel files here

# Create directories
mkdir -p state logs
```

### 2. Configure Environment

Create a `.env` file with your configuration:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
nano .env
```

**Required settings in .env:**
```bash
# Project paths
PROJECT_ROOT=/var/www/your-project
VENV_PATH=/var/www/your-venv

# Git settings
GIT_REMOTE=origin
GIT_BRANCH=main  # or your production branch

# Service names
NGINX_SERVICE=nginx
GUNICORN_SERVICE=gunicorn

# Email settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587  # or 465 for SSL
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=server-angel@yourdomain.com
EMAIL_RECIPIENTS=admin1@example.com,admin2@example.com
```

> **Note**: For Gmail, generate an app password at https://myaccount.google.com/apppasswords

See [.env.example](.env.example) for all available options with detailed comments.

### 3. Install Dependencies

```bash
# Install Python requirements
pip install -r requirements.txt

# Or system-wide
sudo pip3 install -r requirements.txt
```

### 4. Run Setup Script (Recommended)

Server Angel v2.01 comes with an automated setup script that configures everything for you.

```bash
# Make script executable
chmod +x setup_server_angel.sh

# Run setup
./setup_server_angel.sh
```

Follow the interactive prompts to:
1. Enter your project and venv paths
2. Confirm your configuration
3. Automatically install systemd services and timers

### 5. Manual Setup (Alternative)

If you prefer to set up manually, edit the systemd files in `systemd/` directory to replace `<PROJECT_ROOT>`, `<VENV_PATH>`, and `<USER>` placeholders, then copy them to `/etc/systemd/system/`.

```bash
# Example manual command
sudo cp systemd/*.service /etc/systemd/system/
sudo cp systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now server-angel-health.timer
sudo systemctl enable --now server-angel-git.timer
```

### 4. Test Setup

```bash
# Test basic functionality
python3 tests/test_basic.py

# Test configuration validation
python3 -c "from config import Config; Config.validate(); print('✅ Config OK')"

# Test health check
python3 angel.py --mode=health-check --report-type=daily

# Test git watch
python3 angel.py --mode=git-watch

# Check status
sudo systemctl status server-angel-health.timer
sudo systemctl status server-angel-git.timer

# Trigger manual run via service
sudo systemctl start server-angel-health.service
sudo systemctl start server-angel-git.service
```

## 📧 Email Reports

### Health Report Example

```
🛡️ SERVER ANGEL - DAILY HEALTH REPORT
===========================================

Report Time: 2025-12-29 19:00:00
Report Type: Daily

🖥️  SYSTEM STATUS
------------------

CPU Usage: 15.2%
Memory Usage: 45.8% (1.2GB / 2.6GB)
Disk Usage: 67.3% (45.2GB / 67.1GB)
Server Uptime: 15 days, 4:23:15

🔧 SERVICES STATUS
------------------

✅ nginx: RUNNING (Active)
✅ gunicorn: RUNNING (Active)
✅ redis: RUNNING (Active)
✅ celery: RUNNING (Active)

📊 SUMMARY
----------

✅ All systems operational

Next report: 07:00 (server time)

Generated by Server Angel 🤖
```

### Deployment Report Example

```
🚀 SERVER ANGEL - DEPLOYMENT REPORT
====================================

Report Time: 2025-12-29 14:30:00
Commit: a1b2c3d4e5f6
Status: SUCCESS

📋 DEPLOYMENT DETAILS
---------------------

Changes Detected: Yes
Dependencies Updated: Yes
Services Restarted: nginx, gunicorn

✅ Deployment completed successfully!
All services have been updated and restarted.

🤖 Generated by Server Angel
```

## 🚀 Advanced Features

### Smart Deployment
- **Intelligent Dependency Management**: Only updates Python packages when `requirements.txt` changes
- **Service Health Verification**: Verifies services are actually running after restart
- **Atomic Operations**: Tracks deployment state to avoid duplicate deployments
- **Rollback Safety**: Preserves last known good commit hash

### Resilient Operations
- **Automatic Retry**: Git operations retry 3 times with 5-second delays
- **Timeout Protection**: All subprocess calls have timeouts to prevent hanging
- **Comprehensive Logging**: Every operation logged for debugging
- **Error Notifications**: Failed operations trigger email alerts

### Multi-Server Support
- **Hostname Identification**: Email subjects include server hostname
- **Centralized Monitoring**: Monitor multiple servers from one inbox
- **Per-Server Configuration**: Each server has its own .env file

### Email Intelligence
- **SSL/TLS Auto-Detection**: Automatically uses correct protocol based on port
- **Rich Formatting**: Emoji indicators for quick status scanning
- **Detailed Reports**: Service counts, step-by-step deployment tracking
- **Professional Signatures**: Developer attribution and license info

## ⚙️ Configuration Reference

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PROJECT_ROOT` | Path to your Django project | `/var/www/kwari-core-api` |
| `VENV_PATH` | Path to Python virtualenv | `/var/www/Kwari_core_env` |
| `NGINX_SERVICE` | Systemd service name for Nginx | `nginx` |
| `GUNICORN_SERVICE` | Systemd service name for Gunicorn | `gunicorn` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_USER` | SMTP username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password/app password | `your-password` |
| `EMAIL_FROM` | From email address | `server@example.com` |
| `EMAIL_RECIPIENTS` | Comma-separated email list | `admin1@example.com,admin2@example.com` |

### Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GIT_REMOTE` | `origin` | Git remote name |
| `GIT_BRANCH` | `kwari_Production` | Branch to monitor |
| `REDIS_SERVICE` | - | Redis service name |
| `CELERY_SERVICE` | - | Celery service name |
| `MORNING_REPORT` | `07:00` | Morning report time |
| `EVENING_REPORT` | `19:00` | Evening report time |

## 🛠️ Troubleshooting

### Common Issues

**Configuration validation fails:**
- Check that all required environment variables are set
- Ensure paths exist and are accessible
- Verify service names match your systemd services

**Email not sending:**
- Test SMTP credentials manually
- Check firewall settings
- Verify email provider settings (Gmail requires app passwords)

**Git operations fail:**
- Ensure Git repository is properly initialized
- Check SSH keys for private repositories
- Verify branch name and remote configuration

**Services not restarting:**
- Check sudo permissions for the service user
- Verify service names in configuration
- Review systemd service configurations

### Logs

Check logs at `logs/angel.log` or systemd journal:

```bash
# View recent logs for specific services
sudo journalctl -u server-angel-health.service -n 50
sudo journalctl -u server-angel-git.service -n 50

# Follow logs
sudo journalctl -u server-angel-health.service -f
```

## 💡 Best Practices\n\n### Security\n1. **Protect Credentials**:\n   ```bash\n   chmod 600 .env\n   chown www-data:www-data .env\n   ```\n\n2. **Use App Passwords**: Never use your main email password\n   - Gmail: https://myaccount.google.com/apppasswords\n   - Outlook: https://account.live.com/proofs/AppPassword\n\n3. **Limit Sudo Access**: Create specific sudoers rules for service restarts\n   ```bash\n   # /etc/sudoers.d/server-angel\n   www-data ALL= NOPASSWD: /bin/systemctl restart nginx\n   www-data ALL= NOPASSWD: /bin/systemctl restart gunicorn\n   ```\n\n4. **Git Authentication**: Use SSH keys or deploy tokens (not passwords)\n\n### Monitoring\n1. **Regular Log Review**:\n   ```bash\n   # Check today's activity\n   sudo journalctl -u server-angel.service --since today\n   \n   # Monitor in real-time\n   tail -f /var/www/server-angel/logs/angel.log\n   ```\n\n2. **Email Folder Organization**: Create email filters for:\n   - Health reports → \"Server Angel/Health\"\n   - Deployment reports → \"Server Angel/Deployments\"\n   - Error alerts → \"Server Angel/Errors\" (with notifications)\n\n3. **Health Report Analysis**:\n   - Watch for increasing CPU/memory trends\n   - Monitor disk space approaching 80%\n   - Track service restart patterns\n\n### Deployment Strategy\n1. **Testing Branch First**: Test on staging before production\n2. **Off-Peak Deployments**: Schedule major updates during low traffic\n3. **Gradual Rollout**: For multiple servers, deploy one at a time\n4. **Backup Before Deploy**: Ensure database backups are current\n\n### Maintenance\n1. **Weekly**:\n   - Review health reports for trends\n   - Check log file sizes\n   - Verify email delivery\n\n2. **Monthly**:\n   - Review deployed commits vs Git history\n   - Update Server Angel if new version available\n   - Rotate logs if needed\n\n3. **Quarterly**:\n   - Test disaster recovery (manual deployment)\n   - Update SMTP credentials if rotated\n   - Review and update service list\n\n## 🔒 Security Notes

- Store SMTP passwords securely (use app passwords for Gmail)
- Run Server Angel with minimal required permissions
- Keep the server-angel directory secure (chmod 700)
- Regularly update dependencies
- Monitor logs for suspicious activity

## 👨‍💻 About the Developer

**Kassim Muhammad Atiku** is a passionate software engineer and technology enthusiast specializing in backend development, DevOps, and automation solutions. With expertise in Python, Django, and cloud infrastructure, Kassim focuses on building robust, scalable systems that solve real-world problems.

**GitHub:** [https://github.com/diamond-kassim-3](https://github.com/diamond-kassim-3)

**Professional Background:**
- Backend Developer with expertise in Django and REST APIs
- DevOps enthusiast focusing on automation and monitoring
- Open source contributor committed to sharing knowledge
- Technology innovator in the African tech ecosystem

## 📝 License

**Copyright © 2025 NHT Corporations Limited**

This project is licensed under the MIT License - see the LICENSE file for details.

**Open Source by Kassim Muhammad Atiku** - Brought to you by NHT Corporations Limited

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## 🤝 Contributing

1. Fork the repository
2. Replace placeholders with your configuration
3. Test thoroughly in a staging environment
4. Deploy to production
5. Contribute back to the community!

## 🙏 Acknowledgments

- Built with ❤️ by **Kassim Muhammad Atiku**
- Powered by **NHT Corporations Limited**
- Thanks to the open source community for inspiration

---

**Server Angel - Automate Your Server, Monitor Your World** 🚀
