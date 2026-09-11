"""
Third-party Integration Service
Slack, Discord, Microsoft Teams notifications
"""

import requests
import json
from typing import Dict, Optional, List
from datetime import datetime


class IntegrationService:
    """Service for third-party integrations"""
    
    @staticmethod
    def send_slack_notification(webhook_url: str, message: Dict) -> Dict:
        """
        Send notification to Slack
        
        Args:
            webhook_url: Slack webhook URL
            message: Message data with blocks
            
        Returns:
            Response data
        """
        try:
            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            return {
                'status': 'sent',
                'status_code': response.status_code,
                'response': response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def send_discord_notification(webhook_url: str, message: Dict) -> Dict:
        """
        Send notification to Discord
        
        Args:
            webhook_url: Discord webhook URL
            message: Message data with embeds
            
        Returns:
            Response data
        """
        try:
            response = requests.post(
                webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            return {
                'status': 'sent',
                'status_code': response.status_code,
                'response': response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def format_test_complete_slack(test_name: str, status: str, stats: Dict) -> Dict:
        """Format test completion message for Slack"""
        color = "#36a64f" if status == "passed" else "#ff0000"
        emoji = "✅" if status == "passed" else "❌"
        
        return {
            "text": f"{emoji} Test Execution Complete",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} Test Execution Complete"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Test:*\n{test_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status:*\n{status.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Tests:*\n{stats.get('total', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Passed:*\n{stats.get('passed', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Failed:*\n{stats.get('failed', 0)}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Success Rate:*\n{stats.get('success_rate', 0)}%"
                        }
                    ]
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Executed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    ]
                }
            ],
            "attachments": [
                {
                    "color": color,
                    "text": ""
                }
            ]
        }
    
    @staticmethod
    def format_test_complete_discord(test_name: str, status: str, stats: Dict) -> Dict:
        """Format test completion message for Discord"""
        color = 0x00ff00 if status == "passed" else 0xff0000
        emoji = "✅" if status == "passed" else "❌"
        
        return {
            "content": f"{emoji} **Test Execution Complete**",
            "embeds": [
                {
                    "title": test_name,
                    "color": color,
                    "fields": [
                        {
                            "name": "Status",
                            "value": status.upper(),
                            "inline": True
                        },
                        {
                            "name": "Total Tests",
                            "value": str(stats.get('total', 0)),
                            "inline": True
                        },
                        {
                            "name": "Passed",
                            "value": str(stats.get('passed', 0)),
                            "inline": True
                        },
                        {
                            "name": "Failed",
                            "value": str(stats.get('failed', 0)),
                            "inline": True
                        },
                        {
                            "name": "Success Rate",
                            "value": f"{stats.get('success_rate', 0)}%",
                            "inline": True
                        }
                    ],
                    "timestamp": datetime.now().isoformat(),
                    "footer": {
                        "text": "AutoTest AI"
                    }
                }
            ]
        }
    
    @staticmethod
    def format_bug_created_slack(bug_title: str, severity: str, project: str) -> Dict:
        """Format bug creation message for Slack"""
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        
        emoji = severity_emoji.get(severity.lower(), '🔵')
        
        return {
            "text": f"{emoji} New Bug Reported",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{emoji} New Bug Reported"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Title:*\n{bug_title}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Severity:*\n{severity.upper()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Project:*\n{project}"
                        }
                    ]
                }
            ]
        }
    
    @staticmethod
    def format_bug_created_discord(bug_title: str, severity: str, project: str) -> Dict:
        """Format bug creation message for Discord"""
        severity_colors = {
            'critical': 0xff0000,
            'high': 0xff6600,
            'medium': 0xffff00,
            'low': 0x00ff00
        }
        
        color = severity_colors.get(severity.lower(), 0x0099ff)
        
        return {
            "content": "🐛 **New Bug Reported**",
            "embeds": [
                {
                    "title": bug_title,
                    "color": color,
                    "fields": [
                        {
                            "name": "Severity",
                            "value": severity.upper(),
                            "inline": True
                        },
                        {
                            "name": "Project",
                            "value": project,
                            "inline": True
                        }
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    @staticmethod
    def format_regression_failure_slack(suite_name: str, failed_count: int, total: int) -> Dict:
        """Format regression failure message for Slack"""
        return {
            "text": "⚠️ Regression Suite Failed",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "⚠️ Regression Suite Failed"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Suite:*\n{suite_name}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Failed Tests:*\n{failed_count}/{total}"
                        }
                    ]
                }
            ],
            "attachments": [
                {
                    "color": "#ff9900",
                    "text": "Please review the failed tests immediately."
                }
            ]
        }
    
    @staticmethod
    def format_regression_failure_discord(suite_name: str, failed_count: int, total: int) -> Dict:
        """Format regression failure message for Discord"""
        return {
            "content": "⚠️ **Regression Suite Failed**",
            "embeds": [
                {
                    "title": suite_name,
                    "color": 0xff9900,
                    "fields": [
                        {
                            "name": "Failed Tests",
                            "value": f"{failed_count}/{total}",
                            "inline": True
                        }
                    ],
                    "description": "Please review the failed tests immediately.",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    @staticmethod
    def send_notification(
        integration_type: str,
        webhook_url: str,
        event_type: str,
        data: Dict
    ) -> Dict:
        """
        Send notification based on integration type and event
        
        Args:
            integration_type: slack, discord, teams
            webhook_url: Webhook URL
            event_type: test_complete, bug_created, regression_failure
            data: Event data
            
        Returns:
            Result dictionary
        """
        message = None
        
        # Format message based on integration and event type
        if integration_type == "slack":
            if event_type == "test_complete":
                message = IntegrationService.format_test_complete_slack(
                    data.get('test_name', 'Unknown Test'),
                    data.get('status', 'unknown'),
                    data.get('stats', {})
                )
            elif event_type == "bug_created":
                message = IntegrationService.format_bug_created_slack(
                    data.get('title', 'Unknown Bug'),
                    data.get('severity', 'medium'),
                    data.get('project', 'Unknown Project')
                )
            elif event_type == "regression_failure":
                message = IntegrationService.format_regression_failure_slack(
                    data.get('suite_name', 'Unknown Suite'),
                    data.get('failed_count', 0),
                    data.get('total', 0)
                )
        
        elif integration_type == "discord":
            if event_type == "test_complete":
                message = IntegrationService.format_test_complete_discord(
                    data.get('test_name', 'Unknown Test'),
                    data.get('status', 'unknown'),
                    data.get('stats', {})
                )
            elif event_type == "bug_created":
                message = IntegrationService.format_bug_created_discord(
                    data.get('title', 'Unknown Bug'),
                    data.get('severity', 'medium'),
                    data.get('project', 'Unknown Project')
                )
            elif event_type == "regression_failure":
                message = IntegrationService.format_regression_failure_discord(
                    data.get('suite_name', 'Unknown Suite'),
                    data.get('failed_count', 0),
                    data.get('total', 0)
                )
        
        if not message:
            return {
                'status': 'failed',
                'error': f'Unsupported integration type or event: {integration_type}/{event_type}'
            }
        
        # Send notification
        if integration_type == "slack":
            return IntegrationService.send_slack_notification(webhook_url, message)
        elif integration_type == "discord":
            return IntegrationService.send_discord_notification(webhook_url, message)
        
        return {
            'status': 'failed',
            'error': 'Integration type not implemented'
        }
