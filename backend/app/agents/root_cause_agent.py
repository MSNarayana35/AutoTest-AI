"""
Root Cause Analysis Agent
Analyzes test failures and provides intelligent explanations for why tests failed.
Uses AI to examine logs, stack traces, and execution context.
"""

import re
from typing import Dict, Optional
from .base import BaseAgent


class RootCauseAnalysisAgent(BaseAgent):
    """
    Agent responsible for analyzing test failures and determining root causes.
    Uses AI to examine error logs, execution traces, and provide actionable insights.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.agent_name = "root_cause_agent"

    def analyze_failure(self, test_case: Dict, execution: Dict) -> Dict:
        """
        Analyze a test failure and determine the root cause.
        
        Args:
            test_case: Test case details
            execution: Execution details including logs and status
            
        Returns:
            Dict with root cause analysis
        """
        logs = execution.get("logs", "")
        status = execution.get("status", "")
        
        if status != "failed":
            return {
                "root_cause": "No failure detected",
                "category": "success",
                "explanation": "Test passed successfully",
                "recommendations": []
            }
        
        # Analyze the logs to determine root cause
        analysis = self._analyze_logs(logs)
        
        # Use AI to get detailed explanation if available
        if self.llm:
            ai_analysis = self._get_ai_analysis(test_case, execution, logs)
            analysis.update(ai_analysis)
        
        return analysis

    def _analyze_logs(self, logs: str) -> Dict:
        """
        Pattern-based log analysis to identify common failure causes.
        """
        root_cause = "Unknown error"
        category = "unknown"
        recommendations = []
        
        # Common error patterns
        patterns = {
            "timeout": {
                "regex": r"timeout|timed out|TimeoutError",
                "category": "timeout",
                "root_cause": "Test execution timeout",
                "recommendations": [
                    "Increase timeout duration",
                    "Optimize slow operations",
                    "Check for infinite loops or blocking operations"
                ]
            },
            "element_not_found": {
                "regex": r"element not found|ElementNotFound|locator.*not found|selector.*failed",
                "category": "locator",
                "root_cause": "Element locator failed - UI element not found",
                "recommendations": [
                    "Verify element selector is correct",
                    "Check if element exists in the page",
                    "Add wait conditions for dynamic elements",
                    "Enable self-healing to auto-fix selectors"
                ]
            },
            "assertion_error": {
                "regex": r"AssertionError|assertion failed|expected.*but got",
                "category": "assertion",
                "root_cause": "Assertion failure - Expected vs Actual mismatch",
                "recommendations": [
                    "Review expected values in test case",
                    "Check if application behavior changed",
                    "Verify test data is correct",
                    "Update test expectations if requirements changed"
                ]
            },
            "network_error": {
                "regex": r"network error|NetworkError|connection refused|ECONNREFUSED|fetch failed",
                "category": "network",
                "root_cause": "Network connectivity issue",
                "recommendations": [
                    "Check if application server is running",
                    "Verify network connectivity",
                    "Check firewall and proxy settings",
                    "Ensure correct API endpoints"
                ]
            },
            "permission_error": {
                "regex": r"PermissionError|permission denied|access denied|403 Forbidden",
                "category": "permission",
                "root_cause": "Permission or authorization error",
                "recommendations": [
                    "Verify authentication credentials",
                    "Check user permissions and roles",
                    "Ensure valid session/token",
                    "Review access control policies"
                ]
            },
            "not_found_error": {
                "regex": r"404|not found|NotFoundError|resource not found",
                "category": "not_found",
                "root_cause": "Resource not found (404)",
                "recommendations": [
                    "Verify resource URL/path is correct",
                    "Check if resource exists in system",
                    "Review routing configuration",
                    "Ensure API endpoints are deployed"
                ]
            },
            "server_error": {
                "regex": r"500|Internal Server Error|server error|backend error",
                "category": "server_error",
                "root_cause": "Server-side error (500)",
                "recommendations": [
                    "Check server logs for details",
                    "Verify backend services are running",
                    "Review database connectivity",
                    "Check for application crashes"
                ]
            },
            "syntax_error": {
                "regex": r"SyntaxError|syntax error|invalid syntax",
                "category": "syntax",
                "root_cause": "Script syntax error",
                "recommendations": [
                    "Review test script for syntax errors",
                    "Validate script against language specification",
                    "Check for missing brackets or quotes",
                    "Regenerate test case if corrupted"
                ]
            },
            "null_pointer": {
                "regex": r"null|undefined|NullPointerException|cannot read property",
                "category": "null_reference",
                "root_cause": "Null or undefined reference error",
                "recommendations": [
                    "Add null checks in test script",
                    "Verify data is loaded before access",
                    "Check API responses for expected data",
                    "Add defensive programming checks"
                ]
            }
        }
        
        # Match patterns in logs
        for key, pattern_info in patterns.items():
            if re.search(pattern_info["regex"], logs, re.IGNORECASE):
                root_cause = pattern_info["root_cause"]
                category = pattern_info["category"]
                recommendations = pattern_info["recommendations"]
                break
        
        return {
            "root_cause": root_cause,
            "category": category,
            "recommendations": recommendations
        }

    def _get_ai_analysis(self, test_case: Dict, execution: Dict, logs: str) -> Dict:
        """
        Use AI to provide detailed root cause analysis.
        """
        test_title = test_case.get("title", "Unknown Test")
        test_description = test_case.get("description", "")
        test_script = test_case.get("script", "")
        
        prompt = f"""You are an expert software testing engineer analyzing a test failure.

Test Case: {test_title}
Description: {test_description}

Test Script:
{test_script[:1000]}

Execution Logs:
{logs[:2000]}

Based on the logs and test details, provide:
1. The most likely root cause of the failure
2. A detailed explanation of what went wrong
3. Specific recommendations to fix the issue
4. Whether this is likely a test issue, application bug, or environment issue

Respond in JSON format:
{{
    "ai_root_cause": "detailed root cause",
    "explanation": "technical explanation of what went wrong",
    "ai_recommendations": ["recommendation 1", "recommendation 2"],
    "issue_type": "test_issue|application_bug|environment_issue",
    "confidence": "high|medium|low"
}}
"""
        
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            import json
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "ai_root_cause": ai_data.get("ai_root_cause", ""),
                    "explanation": ai_data.get("explanation", ""),
                    "ai_recommendations": ai_data.get("ai_recommendations", []),
                    "issue_type": ai_data.get("issue_type", "unknown"),
                    "confidence": ai_data.get("confidence", "low")
                }
        except Exception as e:
            self.logger.error(f"AI analysis failed: {e}")
        
        return {}

    def run(self, input_data: Dict) -> Dict:
        """
        Main execution method for the agent.
        
        Args:
            input_data: Should contain 'test_case' and 'execution' details
            
        Returns:
            Root cause analysis results
        """
        test_case = input_data.get("test_case", {})
        execution = input_data.get("execution", {})
        
        if not test_case or not execution:
            return {
                "success": False,
                "error": "Missing test_case or execution data"
            }
        
        try:
            analysis = self.analyze_failure(test_case, execution)
            
            return {
                "success": True,
                "agent": self.agent_name,
                "test_case_id": test_case.get("id"),
                "execution_id": execution.get("id"),
                "analysis": analysis
            }
        except Exception as e:
            self.logger.error(f"Root cause analysis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def batch_analyze(self, failed_executions: list) -> Dict:
        """
        Analyze multiple test failures and identify patterns.
        
        Args:
            failed_executions: List of failed test executions with details
            
        Returns:
            Batch analysis with common patterns
        """
        analyses = []
        categories = {}
        
        for exec_data in failed_executions:
            test_case = exec_data.get("test_case", {})
            execution = exec_data.get("execution", {})
            
            analysis = self.analyze_failure(test_case, execution)
            analyses.append({
                "test_id": test_case.get("id"),
                "test_title": test_case.get("title"),
                "analysis": analysis
            })
            
            # Track failure categories
            category = analysis.get("category", "unknown")
            categories[category] = categories.get(category, 0) + 1
        
        # Identify most common failure type
        most_common = max(categories.items(), key=lambda x: x[1]) if categories else ("unknown", 0)
        
        return {
            "success": True,
            "total_failures": len(failed_executions),
            "analyses": analyses,
            "failure_categories": categories,
            "most_common_failure": {
                "category": most_common[0],
                "count": most_common[1]
            },
            "recommendations": self._get_batch_recommendations(categories)
        }

    def _get_batch_recommendations(self, categories: Dict) -> list:
        """
        Provide recommendations based on failure patterns.
        """
        recommendations = []
        
        if categories.get("locator", 0) > 2:
            recommendations.append("Multiple locator failures detected - Enable self-healing to auto-fix selectors")
        
        if categories.get("timeout", 0) > 2:
            recommendations.append("Multiple timeout failures - Consider increasing timeout values or optimizing test performance")
        
        if categories.get("assertion", 0) > 2:
            recommendations.append("Multiple assertion failures - Review if application requirements have changed")
        
        if categories.get("network", 0) > 1:
            recommendations.append("Network errors detected - Verify all services are running and network is stable")
        
        if len(categories) > 5:
            recommendations.append("Diverse failure types detected - Consider environmental issues or recent code changes")
        
        return recommendations
