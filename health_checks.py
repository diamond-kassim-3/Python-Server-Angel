"""
Server Angel Health Checks Module
Monitors system resources and service statuses.
"""

import subprocess
import psutil
from datetime import datetime, timedelta
from config import Config


class HealthChecker:
    """Handles all health monitoring tasks."""

    @staticmethod
    def get_system_health():
        """Get system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            def format_bytes(bytes_value):
                """Format bytes to human readable format."""
                for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                    if bytes_value < 1024.0:
                        return f"{bytes_value:.1f} {unit}"
                    bytes_value /= 1024.0
                return f"{bytes_value:.1f} TB"

            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            return {
                'cpu_usage': f"{cpu_percent:.1f}%",
                'memory_usage': f"{memory_percent:.1f}% ({format_bytes(memory.used)} / {format_bytes(memory.total)})",
                'disk_usage': f"{disk_percent:.1f}% ({format_bytes(disk.used)} / {format_bytes(disk.total)})",
                'uptime': str(uptime).split('.')[0],  # Remove microseconds
                'status': 'OK'
            }
        except Exception as e:
            return {
                'error': f"System health check failed: {str(e)}",
                'status': 'ERROR'
            }

    @staticmethod
    def get_service_status(service_name):
        """Check systemd service status."""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            status = result.stdout.strip()

            if status == 'active':
                return {'name': service_name, 'status': 'RUNNING', 'details': 'Active'}
            elif status == 'inactive':
                return {'name': service_name, 'status': 'STOPPED', 'details': 'Inactive'}
            elif status == 'failed':
                return {'name': service_name, 'status': 'FAILED', 'details': 'Failed'}
            else:
                return {'name': service_name, 'status': 'UNKNOWN', 'details': status}

        except subprocess.TimeoutExpired:
            return {'name': service_name, 'status': 'TIMEOUT', 'details': 'Check timed out'}
        except Exception as e:
            return {'name': service_name, 'status': 'ERROR', 'details': str(e)}

    @staticmethod
    def check_all_services():
        """Check status of all configured services."""
        services = [
            Config.NGINX_SERVICE,
            Config.GUNICORN_SERVICE,
            Config.REDIS_SERVICE,
            Config.CELERY_SERVICE
        ]

        results = []
        for service in services:
            if service and not service.startswith('<'):  # Skip if placeholder
                results.append(HealthChecker.get_service_status(service))
            else:
                results.append({
                    'name': service or 'Unknown Service',
                    'status': 'NOT_CONFIGURED',
                    'details': 'Service name not set'
                })

        return results

    @staticmethod
    def run_full_health_check():
        """Run complete health check."""
        return {
            'timestamp': datetime.now().isoformat(),
            'system': HealthChecker.get_system_health(),
            'services': HealthChecker.check_all_services()
        }
