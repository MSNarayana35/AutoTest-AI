"""
Test Execution Agent
Manages and orchestrates test execution across different test types.
Handles single test runs, bulk execution, and parallel test execution.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from .base import BaseAgent


class TestExecutionAgent(BaseAgent):
    """
    Agent responsible for executing test cases with various strategies.
    Supports single execution, bulk execution, parallel execution, and retry logic.
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.agent_name = "execution_agent"
        self.max_retries = config.get("max_retries", 1) if config else 1
        self.timeout = config.get("timeout", 30000) if config else 30000  # 30 seconds

    def execute_test(self, test_case: Dict, options: Optional[Dict] = None) -> Dict:
        """
        Execute a single test case.
        
        Args:
            test_case: Test case details including script and metadata
            options: Execution options (timeout, retries, etc.)
            
        Returns:
            Execution result with status, logs, and metrics
        """
        options = options or {}
        timeout = options.get("timeout", self.timeout)
        retries = options.get("retries", self.max_retries)
        
        test_id = test_case.get("id")
        test_type = test_case.get("test_type", "functional")
        script = test_case.get("script", "")
        
        self.logger.info(f"Executing test case ID: {test_id}")
        
        # Execute with retry logic
        for attempt in range(retries + 1):
            try:
                result = self._run_test_script(test_case, timeout)
                
                if result["status"] == "passed":
                    return result
                
                # If failed and retries remaining, try again
                if attempt < retries:
                    self.logger.info(f"Test failed, retrying... (Attempt {attempt + 2}/{retries + 1})")
                    continue
                
                return result
                
            except Exception as e:
                self.logger.error(f"Test execution error (attempt {attempt + 1}): {e}")
                if attempt == retries:
                    return {
                        "status": "error",
                        "logs": f"Execution failed after {retries + 1} attempts: {str(e)}",
                        "execution_time": 0,
                        "error": str(e)
                    }

    def _run_test_script(self, test_case: Dict, timeout: int) -> Dict:
        """
        Execute the actual test script (Playwright, API, etc.)
        """
        import subprocess
        import tempfile
        import os
        
        script = test_case.get("script", "")
        test_type = test_case.get("test_type", "functional")
        test_id = test_case.get("id")
        
        if not script:
            return {
                "status": "skipped",
                "logs": "No test script provided",
                "execution_time": 0
            }
        
        start_time = datetime.utcnow()
        
        try:
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                delete=False,
                encoding='utf-8'
            ) as f:
                # Add imports if not present
                if "from playwright" not in script:
                    f.write("from playwright.sync_api import sync_playwright\n")
                    f.write("import sys\n\n")
                
                f.write(script)
                temp_file = f.name
            
            # Execute the script
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout / 1000  # Convert ms to seconds
            )
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            # Calculate execution time
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000  # milliseconds
            
            # Determine status
            status = "passed" if result.returncode == 0 else "failed"
            
            # Combine stdout and stderr for logs
            logs = result.stdout
            if result.stderr:
                logs += f"\n\nErrors:\n{result.stderr}"
            
            return {
                "status": status,
                "logs": logs or "Test executed successfully" if status == "passed" else "Test execution failed",
                "execution_time": int(execution_time),
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "status": "failed",
                "logs": f"Test execution timed out after {timeout}ms",
                "execution_time": timeout,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "logs": f"Execution error: {str(e)}",
                "execution_time": 0,
                "error": str(e)
            }

    def execute_bulk(self, test_cases: List[Dict], options: Optional[Dict] = None) -> Dict:
        """
        Execute multiple test cases sequentially or in parallel.
        
        Args:
            test_cases: List of test cases to execute
            options: Execution options (parallel, timeout, etc.)
            
        Returns:
            Bulk execution results with statistics
        """
        options = options or {}
        parallel = options.get("parallel", False)
        max_workers = options.get("max_workers", 4)
        
        self.logger.info(f"Starting bulk execution of {len(test_cases)} test cases")
        
        if parallel:
            return self._execute_parallel(test_cases, options, max_workers)
        else:
            return self._execute_sequential(test_cases, options)

    def _execute_sequential(self, test_cases: List[Dict], options: Dict) -> Dict:
        """
        Execute test cases one by one.
        """
        results = []
        start_time = datetime.utcnow()
        
        for i, test_case in enumerate(test_cases):
            self.logger.info(f"Executing test {i+1}/{len(test_cases)}: {test_case.get('title')}")
            
            result = self.execute_test(test_case, options)
            results.append({
                "test_case_id": test_case.get("id"),
                "test_title": test_case.get("title"),
                "result": result
            })
        
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        # Calculate statistics
        stats = self._calculate_statistics(results, total_time)
        
        return {
            "success": True,
            "execution_mode": "sequential",
            "total_tests": len(test_cases),
            "statistics": stats,
            "results": results
        }

    def _execute_parallel(self, test_cases: List[Dict], options: Dict, max_workers: int) -> Dict:
        """
        Execute test cases in parallel using thread pool.
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        start_time = datetime.utcnow()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all test executions
            future_to_test = {
                executor.submit(self.execute_test, test_case, options): test_case
                for test_case in test_cases
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    results.append({
                        "test_case_id": test_case.get("id"),
                        "test_title": test_case.get("title"),
                        "result": result
                    })
                except Exception as e:
                    self.logger.error(f"Test execution failed: {e}")
                    results.append({
                        "test_case_id": test_case.get("id"),
                        "test_title": test_case.get("title"),
                        "result": {
                            "status": "error",
                            "logs": str(e),
                            "execution_time": 0
                        }
                    })
        
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds() * 1000
        
        # Calculate statistics
        stats = self._calculate_statistics(results, total_time)
        
        return {
            "success": True,
            "execution_mode": "parallel",
            "max_workers": max_workers,
            "total_tests": len(test_cases),
            "statistics": stats,
            "results": results
        }

    def _calculate_statistics(self, results: List[Dict], total_time: float) -> Dict:
        """
        Calculate execution statistics.
        """
        total = len(results)
        passed = sum(1 for r in results if r["result"]["status"] == "passed")
        failed = sum(1 for r in results if r["result"]["status"] == "failed")
        error = sum(1 for r in results if r["result"]["status"] == "error")
        skipped = sum(1 for r in results if r["result"]["status"] == "skipped")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        avg_time = sum(r["result"].get("execution_time", 0) for r in results) / total if total > 0 else 0
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "error": error,
            "skipped": skipped,
            "pass_rate": round(pass_rate, 2),
            "total_execution_time": int(total_time),
            "average_execution_time": int(avg_time)
        }

    def execute_with_tags(self, test_cases: List[Dict], tags: List[str], options: Optional[Dict] = None) -> Dict:
        """
        Execute test cases filtered by tags.
        
        Args:
            test_cases: All test cases
            tags: Tags to filter by
            options: Execution options
            
        Returns:
            Filtered execution results
        """
        # Filter test cases by tags
        filtered_tests = [
            tc for tc in test_cases
            if any(tag in tc.get("tags", []) for tag in tags)
        ]
        
        self.logger.info(f"Filtered {len(filtered_tests)} tests with tags: {tags}")
        
        if not filtered_tests:
            return {
                "success": True,
                "message": "No tests matched the specified tags",
                "total_tests": 0,
                "statistics": {}
            }
        
        return self.execute_bulk(filtered_tests, options)

    def run(self, input_data: Dict) -> Dict:
        """
        Main execution method for the agent.
        
        Args:
            input_data: Contains test_cases and execution options
            
        Returns:
            Execution results
        """
        mode = input_data.get("mode", "single")  # single, bulk, tags
        test_cases = input_data.get("test_cases", [])
        options = input_data.get("options", {})
        
        if not test_cases:
            return {
                "success": False,
                "error": "No test cases provided"
            }
        
        try:
            if mode == "single":
                result = self.execute_test(test_cases[0], options)
                return {
                    "success": True,
                    "agent": self.agent_name,
                    "mode": "single",
                    "result": result
                }
            
            elif mode == "bulk":
                result = self.execute_bulk(test_cases, options)
                return {
                    **result,
                    "agent": self.agent_name
                }
            
            elif mode == "tags":
                tags = input_data.get("tags", [])
                result = self.execute_with_tags(test_cases, tags, options)
                return {
                    **result,
                    "agent": self.agent_name
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown execution mode: {mode}"
                }
                
        except Exception as e:
            self.logger.error(f"Execution agent failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
