# Server Angel v2.0 - Deployment Guide

## Quick Deployment Checklist

### 1. Prerequisites
- [ ] Linux server with systemd
- [ ] Python 3.8 or higher
- [ ] Git installed
- [ ] Sudo privileges for systemd service management
- [ ] SMTP credentials (Gmail, SendGrid, etc.)

### 2. Installation

```bash
# 1. Clone or upload Server Angel to your server
sudo mkdir -p /var/www/server-angel
cd /var/www/server-angel

# Upload all files here

# 2. Install dependencies
pip3 install -r requirements.txt

# Or install system-wide:
sudo pip3 install -r requirements.txt
```

### 3. Configuration

```bash
# 1. Create .env file from example
cp .env.example .env

# 2. Edit .env with your settings
nano .env
```

**Required Settings in .env:**
```bash
# Your application paths
PROJECT_ROOT=/var/www/your-django-app
VENV_PATH=/var/www/your-venv

# Your systemd services
NGINX_SERVICE=nginx
GUNICORN_SERVICE=gunicorn

# Your email settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Generate at: https://myaccount.google.com/apppasswords
EMAIL_FROM=server-angel@yourdomain.com
EMAIL_RECIPIENTS=admin1@example.com,admin2@example.com
```

### 4. Test Configuration

```bash
# Test that configuration loads correctly
python3 -c "from config import Config; Config.validate(); print('✅ Config OK')"

# Test health check (without sending email)
python3 tests/test_basic.py
```

### 5. Manual Testing

```bash
# Test health check with email
python3 angel.py --mode=health-check --report-type=daily

# Test git watch (won't deploy without new commits)
python3 angel.py --mode=git-watch
```

### 6. Install Systemd Services

```bash
# 1. Update systemd service files
cd systemd

# Edit server-angel.service and replace placeholders:
# - <SERVER_ANGEL_ROOT> → /var/www/server-angel
# - <PYTHON_PATH> → /usr/bin/python3

# 2. Copy to systemd
sudo cp *.service /etc/systemd/system/
sudo cp *.timer /etc/systemd/system/

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable timers
sudo systemctl enable server-angel-health.timer
sudo systemctl enable server-angel-git.timer

# 5. Start timers
sudo systemctl start server-angel-health.timer
sudo systemctl start server-angel-git.timer
```

### 7. Verify Installation

```bash
# Check timer status
sudo systemctl status server-angel-health.timer
sudo systemctl status server-angel-git.timer

# View recent logs
sudo journalctl -u server-angel.service -n 50

# Monitor logs in real-time
sudo journalctl -u server-angel.service -f
```

## Troubleshooting

### Configuration Issues

**Problem**: "Required configuration not set"
```bash
# Solution: Check .env file exists and has all required values
cat .env
python3 -c "from config import Config; Config.validate()"
```

**Problem**: "PROJECT_ROOT does not exist"
```bash
# Solution: Verify path is correct and accessible
ls -la /var/www/your-project
```

### Email Issues

**Problem**: "SMTP Authentication failed"
```bash
# For Gmail users:
# 1. Enable 2-Step Verification
# 2. Generate App Password at: https://myaccount.google.com/apppasswords
# 3. Use the app password (not your regular password) in .env

# Test SMTP connection
python3 -c "from mailer import EmailMailer; print(EmailMailer.test_connection())"
```

**Problem**: Email not received
```bash
# Check logs for errors
sudo journalctl -u server-angel.service | grep -i smtp

# Verify recipients are correct
python3 -c "from config import Config; print(Config.EMAIL_RECIPIENTS)"
```

### Git Issues

**Problem**: "Git fetch failed"
```bash
# Ensure Git is configured
cd /var/www/your-project
git status
git remote -v

# Test Git operations
git fetch origin
```

**Problem**: "Failed to pull changes"
```bash
# Check for uncommitted changes
cd /var/www/your-project
git status

# Ensure branch tracking is set
git branch -vv
```

### Service Issues

**Problem**: "Service restart failed"
```bash
# Verify service names
systemctl list-units | grep gunicorn
systemctl list-units | grep nginx

# Check service status
sudo systemctl status gunicorn
sudo systemctl status nginx

# Verify sudo permissions
sudo systemctl restart nginx  # Should work without password prompt
```

## Advanced Configuration

### Custom Report Times

Edit `.env`:
```bash
MORNING_REPORT=06:00
EVENING_REPORT=22:00
```

Update systemd timer:
```bash
sudo nano /etc/systemd/system/server-angel-health.timer

# Change OnCalendar values:
OnCalendar=*-*-* 06:00:00
OnCalendar=*-*-* 22:00:00

sudo systemctl daemon-reload
sudo systemctl restart server-angel-health.timer
```

### Custom Git Watch Interval

Edit `/etc/systemd/system/server-angel-git.timer`:
```ini
# Change from 5min to 10min
OnUnitActiveSec=10min
```

Then reload:
```bash
sudo systemctl daemon-reload
sudo systemctl restart server-angel-git.timer
```

### Multiple Recipients

In `.env`:
```bash
EMAIL_RECIPIENTS=admin1@example.com,admin2@example.com,ops@example.com
```

## Security Best Practices

1. **Protect .env file**:
   ```bash
   chmod 600 .env
   chown www-data:www-data .env
   ```

2. **Use App Passwords** (not your main password)

3. **Limit sudo permissions** (optional):
   Create `/etc/sudoers.d/server-angel`:
   ```
   www-data ALL= NOPASSWD: /bin/systemctl restart nginx
   www-data ALL= NOPASSWD: /bin/systemctl restart gunicorn
   ```

4. **Monitor logs regularly**:
   ```bash
   sudo journalctl -u server-angel.service --since today
   ```

## Maintenance

### View Logs
```bash
# Today's logs
cat /var/www/server-angel/logs/angel.log

# Last deployment
sudo journalctl -u server-angel.service | grep deployment
```

### Force Manual Deployment
```bash
# Trigger manually
cd /var/www/server-angel
python3 angel.py --mode=git-watch
```

### Update Server Angel
```bash
cd /var/www/server-angel
# Back up current version
cp -r . ../server-angel-backup

# Pull updates or upload new files
# Then restart services
sudo systemctl restart server-angel-health.timer
sudo systemctl restart server-angel-git.timer
```

## Support

- **GitHub Issues**: https://github.com/diamond-kassim-3
- **Documentation**: See README.md
- **Changelog**: See CHANGELOG.md
