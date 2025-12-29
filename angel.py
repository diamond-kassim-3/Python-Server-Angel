#!/usr/bin/env python3
"""
Server Angel - Main Orchestrator
Standalone server automation agent for health monitoring and deployment.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Import our modules
from config import Config
from health_checks import HealthChecker
from git_watcher import GitWatcher
from deployer import Deployer
from mailer import EmailMailer


def setup_logging():
    """Setup logging to file and console."""
    Config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def validate_configuration():
    """Validate configuration and exit if invalid."""
    try:
        Config.validate()
        logging.info("Configuration validated successfully")
        return True
    except Exception as e:
        logging.error(f"Configuration validation failed: {str(e)}")
        print(f"❌ Configuration Error: {str(e)}")
        print("\nPlease set your actual values in the environment variables or .env file.")
        print("All placeholder values (starting with '<') must be replaced.")
        sys.exit(1)


def run_health_check(report_type="daily"):
    """Run health check and send report."""
    logging.info(f"Starting {report_type} health check")

    try:
        # Run health checks
        health_data = HealthChecker.run_full_health_check()
        logging.info("Health check completed")

        # Send email report
        email_result = EmailMailer.send_health_report(health_data, report_type)

        if email_result.get('success'):
            logging.info(f"Health report sent successfully: {email_result.get('message')}")
            print(f"✅ {report_type.title()} health report sent successfully")
        else:
            logging.error(f"Failed to send health report: {email_result.get('error')}")
            print(f"❌ Failed to send health report: {email_result.get('error')}")

    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")

        # Send error alert
        try:
            EmailMailer.send_error_alert(error_msg, "health_check")
            logging.info("Error alert sent")
        except Exception as email_error:
            logging.error(f"Failed to send error alert: {str(email_error)}")


def run_git_watch():
    """Run git monitoring and deployment if needed."""
    logging.info("Starting git watch cycle")

    try:
        # Check for new commits
        watch_result = GitWatcher.run_watch_cycle()

        if watch_result.get('trigger_deployment'):
            logging.info(f"New commits detected: {watch_result['commit_hash'][:8]}")
            print(f"🚀 New commits detected, starting deployment...")

            # Run deployment
            deployment_result = Deployer.run_deployment(
                watch_result['commit_hash'],
                watch_result.get('requirements_changed', False)
            )

            # Update last deployed commit if successful
            if deployment_result.get('success'):
                GitWatcher.save_last_deployed_commit(watch_result['commit_hash'])
                logging.info("Last deployed commit updated")

            # Send deployment report
            email_result = EmailMailer.send_deployment_report(deployment_result)

            if email_result.get('success'):
                logging.info(f"Deployment report sent: {email_result.get('message')}")
                if deployment_result.get('success'):
                    print("✅ Deployment completed and report sent")
                else:
                    print("❌ Deployment failed - check email for details")
            else:
                logging.error(f"Failed to send deployment report: {email_result.get('error')}")

        else:
            logging.info("No new commits detected")
            print("ℹ️  No new commits detected")

    except Exception as e:
        error_msg = f"Git watch cycle failed: {str(e)}"
        logging.error(error_msg)
        print(f"❌ {error_msg}")

        # Send error alert
        try:
            EmailMailer.send_error_alert(error_msg, "git_watch")
            logging.info("Error alert sent")
        except Exception as email_error:
            logging.error(f"Failed to send error alert: {str(email_error)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Server Angel - Server Automation Agent')
    parser.add_argument(
        '--mode',
        choices=['health-check', 'git-watch'],
        required=True,
        help='Operation mode'
    )
    parser.add_argument(
        '--report-type',
        choices=['morning', 'evening', 'daily'],
        default='daily',
        help='Type of health report (for health-check mode)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()
    logging.info(f"Server Angel started with mode: {args.mode}")

    # Validate configuration
    validate_configuration()

    # Run requested mode
    if args.mode == 'health-check':
        run_health_check(args.report_type)
    elif args.mode == 'git-watch':
        run_git_watch()

    logging.info("Server Angel completed")


if __name__ == '__main__':
    main()
