"""
Bug Detection Agent
Analyzes test execution results to automatically identify and classify bugs.
Creates bug reports with severity assessment and categorization.
"""

from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseAgent


class BugDetectionAgent(BaseAgent):
    """
    Agent responsible for detecting bugs from test execution failures.
    Analyzes failure patterns, classifies severity, and creates detailed bug reports.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.agent_name = "bug_detection_agent"

    def detect_bugs(self, executions: List[Dict]) -> List[Dict]:
        """
        Analyze test executions and detect bugs.
        
        Args:
            executions: List of test execution results
            
        Returns:
            List of detected bugs with details
        """
        detected_bugs = []
        
        for execution in executions:
            if execution.get("status") == "failed":
                bug = self._analyze_failure(execution)
                if bug:
                    detected_bugs.append(bug)
        
        # Remove duplicates and merge similar bugs
        unique_bugs = self._deduplicate_bugs(detected_bugs)
        
        return unique_bugs

    def _analyze_failure(self, execution: Dict) -> Optional[Dict]:
        """
        Analyze a single test failure and create a bug report.
        """
        test_case = execution.get("test_case", {})
        logs = execution.get("logs", "")
        
        # Classify the bug
        bug_classification = self._classify_bug(logs, test_case)
        
        # Determine severity
        severity = self._determine_severity(bug_classification, test_case)
        
        # Generate bug description
        description = self._generate_bug_description(
            test_case, 
            execution, 
            bug_classification
        )
        
        # Create bug report
        bug = {
            "title": self._generate_bug_title(test_case, bug_classification),
            "description": description,
            "severity": severity,
            "category": bug_classification["category"],
            "test_case_id": test_case.get("id"),
            "execution_id": execution.get("id"),
            "test_case_title": test_case.get("title"),
            "status": "open",
            "detected_at": datetime.utcnow().isoformat(),
            "logs_snippet": logs[:500],
            "classification": bug_classification
        }
        
        return bug

    def _classify_bug(self, logs: str, test_case: Dict) -> Dict:
        """
        Classify the type of bug based on logs and test case.
        """
        import re
        
        # Bug type classification patterns
        patterns = {
            "functional": {
                "keywords": ["assertion", "expected", "actual", "mismatch"],
                "description": "Functional behavior does not match requirements"
            },
            "ui": {
                "keywords": ["element", "locator", "selector", "not found", "visible"],
                "description": "UI element issue or interaction failure"
            },
            "performance": {
                "keywords": ["timeout", "slow", "performance", "exceeded"],
                "description": "Performance or timing issue"
            },
            "data": {
                "keywords": ["null", "undefined", "empty", "invalid data", "missing"],
                "description": "Data validation or integrity issue"
            },
            "integration": {
                "keywords": ["api", "endpoint", "network", "connection", "service"],
                "description": "Integration or service communication issue"
            },
            "security": {
                "keywords": ["permission", "unauthorized", "403", "401", "forbidden"],
                "description": "Security or authorization issue"
            },
            "crash": {
                "keywords": ["crash", "exception", "error 500", "internal error"],
                "description": "Application crash or critical error"
            }
        }
        
        # Count keyword matches
        scores = {}
        for bug_type, info in patterns.items():
            score = sum(1 for keyword in info["keywords"] 
                       if keyword.lower() in logs.lower())
            if score > 0:
                scores[bug_type] = score
        
        # Determine primary category
        if scores:
            primary_category = max(scores.items(), key=lambda x: x[1])[0]
        else:
            primary_category = "unknown"
        
        return {
            "category": primary_category,
            "description": patterns.get(primary_category, {}).get("description", "Unknown issue"),
            "confidence": "high" if scores.get(primary_category, 0) > 2 else "medium"
        }

    def _determine_severity(self, classification: Dict, test_case: Dict) -> str:
        """
        Determine bug severity based on classification and test importance.
        """
        category = classification.get("category")
        test_tags = test_case.get("tags", [])
        
        # Critical severity conditions
        if category in ["crash", "security"]:
            return "critical"
        
        if "critical" in test_tags or "regression" in test_tags:
            return "high"
        
        # High severity conditions
        if category in ["functional", "integration"]:
            return "high"
        
        # Medium severity conditions
        if category in ["ui", "data"]:
            return "medium"
        
        # Low severity for performance and others
        if category == "performance":
            return "low"
        
        return "medium"

    def _generate_bug_title(self, test_case: Dict, classification: Dict) -> str:
        """
        Generate a concise bug title.
        """
        category = classification.get("category", "Unknown").capitalize()
        test_title = test_case.get("title", "Test Case")
        
        return f"{category} Issue: {test_title[:80]}"

    def _generate_bug_description(
        self, 
        test_case: Dict, 
        execution: Dict, 
        classification: Dict
    ) -> str:
        """
        Generate detailed bug description.
        """
        logs = execution.get("logs", "No logs available")
        
        description = f"""**Bug Type**: {classification.get('category', 'Unknown').capitalize()}
**Classification**: {classification.get('description', 'N/A')}
**Confidence**: {classification.get('confidence', 'N/A')}

**Test Case**: {test_case.get('title', 'N/A')}
**Test Type**: {test_case.get('test_type', 'N/A')}
**Execution Date**: {execution.get('created_at', 'N/A')}

**Description**:
{classification.get('description', 'Test execution failed.')}

**Failure Logs**:
```
{logs[:800]}
```

**Expected Behavior**:
{test_case.get('description', 'Test should pass successfully.')}

**Actual Behavior**:
Test failed during execution. Review logs above for details.

**Reproducibility**:
Re-run test case ID: {test_case.get('id')} to reproduce the issue.
"""
        
        return description

    def _deduplicate_bugs(self, bugs: List[Dict]) -> List[Dict]:
        """
        Remove duplicate bugs and merge similar ones.
        """
        if not bugs:
            return []
        
        # Group by category and test case
        unique_map = {}
        for bug in bugs:
            key = f"{bug['category']}_{bug['test_case_id']}"
            if key not in unique_map:
                unique_map[key] = bug
            else:
                # Merge logs if same bug detected multiple times
                existing = unique_map[key]
                existing['logs_snippet'] += f"\n\n--- Additional Failure ---\n{bug['logs_snippet']}"
        
        return list(unique_map.values())

    def run(self, input_data: Dict) -> Dict:
        """
        Main execution method for the agent.
        
        Args:
            input_data: Should contain 'executions' list
            
        Returns:
            Detected bugs and analysis
        """
        executions = input_data.get("executions", [])
        
        if not executions:
            return {
                "success": False,
                "error": "No execution data provided"
            }
        
        try:
            # Detect bugs
            bugs = self.detect_bugs(executions)
            
            # Statistics
            total_executions = len(executions)
            failed_executions = len([e for e in executions if e.get("status") == "failed"])
            bugs_detected = len(bugs)
            
            # Severity breakdown
            severity_counts = {}
            for bug in bugs:
                severity = bug.get("severity", "unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            return {
                "success": True,
                "agent": self.agent_name,
                "statistics": {
                    "total_executions": total_executions,
                    "failed_executions": failed_executions,
                    "bugs_detected": bugs_detected,
                    "detection_rate": f"{(bugs_detected/failed_executions*100):.1f}%" if failed_executions > 0 else "0%"
                },
                "severity_breakdown": severity_counts,
                "bugs": bugs
            }
        except Exception as e:
            self.logger.error(f"Bug detection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_bug_patterns(self, bugs: List[Dict]) -> Dict:
        """
        Analyze patterns in detected bugs to identify systemic issues.
        """
        if not bugs:
            return {
                "total_bugs": 0,
                "patterns": [],
                "recommendations": []
            }
        
        # Category distribution
        categories = {}
        severities = {}
        
        for bug in bugs:
            cat = bug.get("category", "unknown")
            sev = bug.get("severity", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
            severities[sev] = severities.get(sev, 0) + 1
        
        # Identify patterns
        patterns = []
        if categories.get("ui", 0) > 3:
            patterns.append("Multiple UI-related bugs detected - possible UI instability")
        
        if categories.get("functional", 0) > 3:
            patterns.append("Multiple functional bugs - core features may be broken")
        
        if severities.get("critical", 0) > 0:
            patterns.append("Critical bugs detected - immediate attention required")
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categories, severities)
        
        return {
            "total_bugs": len(bugs),
            "category_distribution": categories,
            "severity_distribution": severities,
            "patterns": patterns,
            "recommendations": recommendations
        }

    def _generate_recommendations(self, categories: Dict, severities: Dict) -> List[str]:
        """
        Generate recommendations based on bug patterns.
        """
        recommendations = []
        
        if severities.get("critical", 0) > 0:
            recommendations.append("🚨 Stop deployment - critical bugs found")
        
        if severities.get("high", 0) > 2:
            recommendations.append("⚠️ Review high-severity bugs before release")
        
        if categories.get("ui", 0) > 3:
            recommendations.append("🔧 Enable self-healing for UI selector issues")
        
        if categories.get("performance", 0) > 2:
            recommendations.append("⚡ Investigate performance bottlenecks")
        
        if categories.get("security", 0) > 0:
            recommendations.append("🔒 Conduct security review immediately")
        
        return recommendations
