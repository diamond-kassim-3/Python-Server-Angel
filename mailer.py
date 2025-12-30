"""
Server Angel Email Mailer Module
Handles SMTP email sending with proper error handling.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config


class EmailMailer:
    """Handles email sending via SMTP."""

    @staticmethod
    def send_email(subject, text_body, html_body=None, recipients=None):
        """Send email with subject, text body, and optional HTML body."""
        if recipients is None:
            recipients = Config.EMAIL_RECIPIENTS

        try:
            # Create message container - 'alternative' ensures clients choose the best display option
            msg = MIMEMultipart('alternative')
            msg['From'] = Config.EMAIL_FROM
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject

            # Attach parts
            # The order matters: text/plain first, then text/html
            msg.attach(MIMEText(text_body, 'plain'))
            
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Create SMTP connection based on port
            if Config.SMTP_PORT == 465:
                # Use SSL
                logging.info(f"Connecting to {Config.SMTP_HOST}:{Config.SMTP_PORT} with SSL")
                server = smtplib.SMTP_SSL(Config.SMTP_HOST, Config.SMTP_PORT)
            else:
                # Use TLS (port 587 or others)
                logging.info(f"Connecting to {Config.SMTP_HOST}:{Config.SMTP_PORT} with STARTTLS")
                server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
                server.starttls()  # Secure connection

            # Login
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            logging.info("SMTP authentication successful")

            # Send email
            server.sendmail(Config.EMAIL_FROM, recipients, msg.as_string())
            logging.info(f"Email sent to {len(recipients)} recipients")

            # Close connection
            server.quit()

            return {'success': True, 'message': f'Email sent to {len(recipients)} recipients'}

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP Authentication failed: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}

        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP Connection failed: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}

        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}

    @staticmethod
    def send_health_report(health_data, report_type="daily"):
        """Send health check report email."""
        from reporter import EmailReporter

        subject, text, html = EmailReporter.build_health_report(health_data, report_type)
        return EmailMailer.send_email(subject, text, html)

    @staticmethod
    def send_deployment_report(deployment_data):
        """Send deployment notification email."""
        from reporter import EmailReporter

        subject, text, html = EmailReporter.build_deployment_report(deployment_data)
        return EmailMailer.send_email(subject, text, html)

    @staticmethod
    def send_error_alert(error_message, context="general"):
        """Send error alert email."""
        from reporter import EmailReporter

        subject, text, html = EmailReporter.build_error_report(error_message, context)
        return EmailMailer.send_email(subject, text, html)

    @staticmethod
    def test_connection():
        """Test SMTP connection without sending email."""
        try:
            server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            server.starttls()
            server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
            server.quit()

            return {'success': True, 'message': 'SMTP connection successful'}

        except Exception as e:
            return {'success': False, 'error': f'SMTP test failed: {str(e)}'}
