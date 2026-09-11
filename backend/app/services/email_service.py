"""
Email Service for sending notifications via SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from app.core.timezone import format_ist_datetime


def send_email(
    to_emails: List[str],
    subject: str,
    html_body: str,
    text_body: Optional[str] = None
) -> bool:
    """
    Send an email using SMTP
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text alternative (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    
    # Check if email is enabled
    if not settings.SMTP_ENABLED:
        print(f"Email sending disabled. Would have sent: {subject} to {to_emails}")
        return False
    
    # Validate SMTP configuration
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP credentials not configured. Set SMTP_USER and SMTP_PASSWORD in .env")
        return False
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.SMTP_FROM
        message["To"] = ", ".join(to_emails)
        message["Subject"] = subject
        
        # Add plain text version if provided
        if text_body:
            part1 = MIMEText(text_body, "plain")
            message.attach(part1)
        
        # Add HTML version
        part2 = MIMEText(html_body, "html")
        message.attach(part2)
        
        # Connect to SMTP server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email sent successfully to {to_emails}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed. Check SMTP_USER and SMTP_PASSWORD.")
        print("For Gmail: Use App Password from https://myaccount.google.com/apppasswords")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error occurred: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def create_test_failure_email(
    user_name: str,
    project_name: str,
    failed_count: int,
    total_count: int,
    failed_tests: List[str],
    dashboard_url: str = "http://localhost:3000/dashboard"
) -> str:
    """
    Create HTML email for test failure notification
    
    Args:
        user_name: Recipient's name
        project_name: Name of the project
        failed_count: Number of failed tests
        total_count: Total number of tests
        failed_tests: List of failed test names
        dashboard_url: URL to dashboard
    
    Returns:
        HTML string for email body
    """
    
    timestamp = format_ist_datetime(datetime.now())
    success_count = total_count - failed_count
    failure_rate = round((failed_count / total_count) * 100, 1) if total_count > 0 else 0
    
    # Determine severity color
    if failure_rate >= 50:
        severity_color = "#ef4444"  # red
        severity_text = "Critical"
    elif failure_rate >= 25:
        severity_color = "#f59e0b"  # orange
        severity_text = "High"
    else:
        severity_color = "#eab308"  # yellow
        severity_text = "Medium"
    
    # Build failed tests list
    failed_tests_html = ""
    for test in failed_tests[:10]:  # Show max 10
        failed_tests_html += f'<li style="margin: 5px 0; color: #94a3b8;">{test}</li>'
    
    if len(failed_tests) > 10:
        failed_tests_html += f'<li style="margin: 5px 0; color: #64748b;">... and {len(failed_tests) - 10} more</li>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Failure Alert</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #0f172a; color: #e2e8f0;">
        
        <!-- Container -->
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
            <tr>
                <td align="center">
                    
                    <!-- Main Card -->
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, {severity_color} 0%, #dc2626 100%); padding: 30px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700;">
                                    ⚠️ Test Failure Alert
                                </h1>
                                <p style="margin: 10px 0 0 0; color: #fef2f2; font-size: 14px; opacity: 0.95;">
                                    {severity_text} Priority • {timestamp}
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding: 35px 30px;">
                                
                                <!-- Greeting -->
                                <p style="margin: 0 0 20px 0; font-size: 16px; color: #e2e8f0;">
                                    Hi {user_name},
                                </p>
                                
                                <p style="margin: 0 0 25px 0; font-size: 16px; color: #cbd5e1; line-height: 1.6;">
                                    Your test run for <strong style="color: #60a5fa;">{project_name}</strong> has completed with failures.
                                </p>
                                
                                <!-- Stats Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; border-radius: 8px; border: 1px solid #334155; margin: 25px 0;">
                                    <tr>
                                        <td style="padding: 20px;">
                                            <table width="100%" cellpadding="0" cellspacing="0">
                                                <tr>
                                                    <td width="50%" style="padding: 10px; text-align: center; border-right: 1px solid #334155;">
                                                        <div style="font-size: 32px; font-weight: 700; color: #ef4444; margin-bottom: 5px;">
                                                            {failed_count}
                                                        </div>
                                                        <div style="font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                                                            Failed
                                                        </div>
                                                    </td>
                                                    <td width="50%" style="padding: 10px; text-align: center;">
                                                        <div style="font-size: 32px; font-weight: 700; color: #10b981; margin-bottom: 5px;">
                                                            {success_count}
                                                        </div>
                                                        <div style="font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">
                                                            Passed
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <td colspan="2" style="padding: 15px 10px 10px 10px; text-align: center; border-top: 1px solid #334155;">
                                                        <div style="font-size: 14px; color: #cbd5e1; margin-bottom: 8px;">
                                                            Success Rate
                                                        </div>
                                                        <div style="background-color: #1e293b; border-radius: 10px; height: 20px; overflow: hidden;">
                                                            <div style="background: linear-gradient(90deg, #10b981 0%, #059669 100%); height: 100%; width: {100 - failure_rate}%; transition: width 0.3s ease;"></div>
                                                        </div>
                                                        <div style="font-size: 18px; font-weight: 600; color: #e2e8f0; margin-top: 8px;">
                                                            {100 - failure_rate}%
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Failed Tests List -->
                                <div style="margin: 25px 0;">
                                    <h3 style="margin: 0 0 15px 0; font-size: 16px; color: #f87171; font-weight: 600;">
                                        Failed Tests:
                                    </h3>
                                    <ul style="margin: 0; padding-left: 20px; list-style: none;">
                                        {failed_tests_html}
                                    </ul>
                                </div>
                                
                                <!-- Call to Action -->
                                <div style="margin: 30px 0; text-align: center;">
                                    <a href="{dashboard_url}" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);">
                                        View Dashboard →
                                    </a>
                                </div>
                                
                                <p style="margin: 25px 0 0 0; font-size: 14px; color: #94a3b8; line-height: 1.6;">
                                    Review the failed tests, check logs, and create bug reports from the dashboard.
                                </p>
                                
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background-color: #0f172a; padding: 25px 30px; border-top: 1px solid #334155;">
                                <p style="margin: 0 0 10px 0; font-size: 13px; color: #64748b; text-align: center;">
                                    This is an automated notification from AutoTest AI
                                </p>
                                <p style="margin: 0; font-size: 12px; color: #475569; text-align: center;">
                                    To disable email notifications, update your preferences in the dashboard
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                    
                </td>
            </tr>
        </table>
        
    </body>
    </html>
    """
    
    return html


def create_welcome_email(user_name: str, user_email: str) -> str:
    """Create welcome email for new users"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Welcome to AutoTest AI</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #e2e8f0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #0f172a; padding: 40px 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #1e293b; border-radius: 12px; overflow: hidden;">
                        
                        <tr>
                            <td style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 40px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700;">
                                    🛡️ Welcome to AutoTest AI!
                                </h1>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="padding: 40px 30px;">
                                <p style="margin: 0 0 20px 0; font-size: 18px; color: #e2e8f0;">
                                    Hi {user_name},
                                </p>
                                <p style="margin: 0 0 20px 0; font-size: 16px; color: #cbd5e1; line-height: 1.6;">
                                    Welcome to <strong>AutoTest AI</strong> - your intelligent QA automation platform! 🚀
                                </p>
                                <p style="margin: 0 0 20px 0; font-size: 16px; color: #cbd5e1; line-height: 1.6;">
                                    You're all set up and ready to start automating your testing workflow.
                                </p>
                                
                                <div style="background-color: #0f172a; border-radius: 8px; padding: 20px; margin: 25px 0;">
                                    <h3 style="margin: 0 0 15px 0; color: #60a5fa;">✨ What you can do:</h3>
                                    <ul style="margin: 0; padding-left: 20px; color: #94a3b8; line-height: 2;">
                                        <li>Upload requirements & generate test cases with AI</li>
                                        <li>Run tests and track execution history</li>
                                        <li>Report bugs with one-click from failures</li>
                                        <li>Generate professional PDF reports</li>
                                        <li>Get notified of test failures (like this email!)</li>
                                    </ul>
                                </div>
                                
                                <div style="margin: 30px 0; text-align: center;">
                                    <a href="http://localhost:3000/dashboard" style="display: inline-block; padding: 14px 32px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px;">
                                        Go to Dashboard →
                                    </a>
                                </div>
                            </td>
                        </tr>
                        
                        <tr>
                            <td style="background-color: #0f172a; padding: 20px; text-align: center; border-top: 1px solid #334155;">
                                <p style="margin: 0; font-size: 13px; color: #64748b;">
                                    Happy Testing! 🎉
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html
