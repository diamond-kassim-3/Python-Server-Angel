# 💡 Server Angel - Best Practices Guide

## Security Best Practices

### 1. Protect Credentials
```bash
# Secure your .env file
chmod 600 .env
chown www-data:www-data .env
```

### 2. Use App Passwords
Never use your main email password in production:
- **Gmail**: Generate at https://myaccount.google.com/apppasswords
- **Outlook**: Generate at https://account.live.com/proofs/AppPassword

### 3. Limit Sudo Access
Create specific sudoers rules instead of blanket sudo access:
```bash
# /etc/sudoers.d/server-angel
www-data ALL= NOPASSWD: /bin/systemctl restart nginx
www-data ALL= NOPASSWD: /bin/systemctl restart gunicorn
```

### 4. Git Authentication
Use SSH keys or deploy tokens, never passwords in configuration.

## Monitoring Best Practices

### 1. Regular Log Review
```bash
# Check today's activity
sudo journalctl -u server-angel.service --since today

# Monitor in real-time
tail -f /var/www/server-angel/logs/angel.log
```

### 2. Email Folder Organization
Create email filters to organize reports:
- Health reports → "Server Angel/Health"
- Deployment reports → "Server Angel/Deployments"
- Error alerts → "Server Angel/Errors" (with notifications enabled)

### 3. Health Report Analysis
- Watch for increasing CPU/memory usage trends
- Monitor disk space when approaching 80%
- Track service restart patterns for issues

## Deployment Strategy

### 1. Testing First
Always test changes on staging environment before production deployment.

### 2. Off-Peak Deployments
Schedule major updates during low-traffic periods to minimize user impact.

### 3. Gradual Rollout
For multi-server setups, deploy to one server at a time and verify before proceeding.

### 4. Backup Before Deploy
Ensure database and critical data backups are current before any deployment.

## Maintenance Schedule

###  Weekly Tasks
- Review health reports for performance trends
- Check log file sizes (rotate if necessary)
- Verify email delivery is working

### Monthly Tasks
- Review deployed commits vs Git history for audit trail
- Update Server Angel if new version is available
- Rotate logs if they're growing large

### Quarterly Tasks
- Test disaster recovery procedures (manual deployment)
- Update SMTP credentials if rotated
- Review and update monitored service list
