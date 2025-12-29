"""
Server Angel Deployer Module
Handles safe deployment: git pull, dependency updates, and service restarts.
"""

import subprocess
import os
import time
import logging
from config import Config


class Deployer:
    """Handles deployment operations safely."""

    @staticmethod
    def pull_latest_changes():
        """Pull latest changes from production branch."""
        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                os.chdir(Config.PROJECT_ROOT)
                logging.info(f"Pulling changes (attempt {attempt + 1}/{max_retries})")

                result = subprocess.run(
                    ['git', 'pull', Config.GIT_REMOTE, Config.GIT_BRANCH],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

                if result.returncode == 0:
                    logging.info(f"Successfully pulled changes: {result.stdout.strip()[:100]}")
                    return {'success': True, 'output': result.stdout.strip()}
                else:
                    error_msg = result.stderr.strip()
                    logging.warning(f"Git pull failed on attempt {attempt + 1}: {error_msg}")

                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise Exception(f"Git pull failed after {max_retries} attempts: {error_msg}")

            except subprocess.TimeoutExpired:
                logging.warning(f"Git pull timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Git pull timed out after {max_retries} attempts")

            except Exception as e:
                if attempt < max_retries - 1:
                    logging.warning(f"Error on attempt {attempt + 1}: {str(e)}")
                    time.sleep(retry_delay)
                    continue
                else:
                    raise Exception(f"Failed to pull changes: {str(e)}")

    @staticmethod
    def update_dependencies():
        """Update Python dependencies if requirements.txt changed."""
        try:
            os.chdir(Config.PROJECT_ROOT)

            # Activate virtual environment
            activate_cmd = f"source {Config.VENV_PATH}/bin/activate && pip install -r requirements.txt"

            result = subprocess.run(
                ['bash', '-c', activate_cmd],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                return {'success': True, 'output': result.stdout.strip()}
            else:
                raise Exception(f"Dependency update failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to update dependencies: {str(e)}")

    @staticmethod
    def restart_service(service_name):
        """Restart a systemd service."""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Verify service is running
                verify_result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if verify_result.returncode == 0 and verify_result.stdout.strip() == 'active':
                    return {'success': True, 'status': 'restarted and verified'}
                else:
                    return {'success': False, 'error': 'Service restart failed verification'}
            else:
                raise Exception(f"Service restart failed: {result.stderr}")

        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def restart_services():
        """Restart all configured services."""
        services = [
            Config.GUNICORN_SERVICE,
            Config.NGINX_SERVICE
        ]

        results = []
        failed_services = []

        for service in services:
            if service and not service.startswith('<'):  # Skip if placeholder
                result = Deployer.restart_service(service)
                results.append({'name': service, 'result': result})

                if not result.get('success', False):
                    failed_services.append(service)
            else:
                results.append({
                    'name': service or 'Unknown Service',
                    'result': {'success': False, 'error': 'Service name not configured'}
                })

        return {
            'results': results,
            'failed_services': failed_services,
            'all_success': len(failed_services) == 0
        }

    @staticmethod
    def verify_deployment():
        """Verify that deployment was successful."""
        try:
            # Check if services are running
            services_ok = True
            service_statuses = []

            services_to_check = [Config.GUNICORN_SERVICE, Config.NGINX_SERVICE]
            for service in services_to_check:
                if service and not service.startswith('<'):
                    result = subprocess.run(
                        ['systemctl', 'is-active', service],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    is_active = result.returncode == 0 and result.stdout.strip() == 'active'
                    service_statuses.append({'name': service, 'active': is_active})
                    if not is_active:
                        services_ok = False

            # Basic health check - try to access the application
            # This is optional and depends on your setup
            app_check = {'performed': False, 'success': False}

            return {
                'services_ok': services_ok,
                'service_statuses': service_statuses,
                'app_check': app_check,
                'overall_success': services_ok
            }

        except Exception as e:
            return {
                'services_ok': False,
                'error': f"Verification failed: {str(e)}",
                'overall_success': False
            }

    @staticmethod
    def run_deployment(commit_hash, requirements_changed):
        """Run complete deployment process."""
        deployment_log = {
            'commit_hash': commit_hash,
            'requirements_changed': requirements_changed,
            'steps': []
        }

        try:
            # Step 1: Pull changes
            deployment_log['steps'].append({'step': 'pull_changes', 'status': 'running'})
            pull_result = Deployer.pull_latest_changes()
            deployment_log['steps'][-1]['status'] = 'success'
            deployment_log['steps'][-1]['details'] = pull_result

            # Step 2: Update dependencies if needed
            if requirements_changed:
                deployment_log['steps'].append({'step': 'update_dependencies', 'status': 'running'})
                dep_result = Deployer.update_dependencies()
                deployment_log['steps'][-1]['status'] = 'success'
                deployment_log['steps'][-1]['details'] = dep_result

            # Step 3: Restart services
            deployment_log['steps'].append({'step': 'restart_services', 'status': 'running'})
            restart_result = Deployer.restart_services()
            deployment_log['steps'][-1]['status'] = 'success'
            deployment_log['steps'][-1]['details'] = restart_result

            if not restart_result.get('all_success', False):
                failed_services = restart_result.get('failed_services', [])
                raise Exception(f"Service restart failed for: {', '.join(failed_services)}")

            # Step 4: Verify deployment
            deployment_log['steps'].append({'step': 'verify_deployment', 'status': 'running'})
            verify_result = Deployer.verify_deployment()
            deployment_log['steps'][-1]['status'] = 'success'
            deployment_log['steps'][-1]['details'] = verify_result

            if not verify_result.get('overall_success', False):
                raise Exception("Deployment verification failed")

            # Success
            deployment_log['success'] = True
            deployment_log['message'] = 'Deployment completed successfully'

            return deployment_log

        except Exception as e:
            # Mark failed step
            if deployment_log['steps']:
                deployment_log['steps'][-1]['status'] = 'failed'
                deployment_log['steps'][-1]['error'] = str(e)

            deployment_log['success'] = False
            deployment_log['error'] = str(e)

            return deployment_log
