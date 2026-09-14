from app.core.config import settings
from app.agents.base import BaseAgent, get_llm


class SelfHealingAgent(BaseAgent):
    def __init__(self, config=None):
        super().__init__(config)
        self.ollama_available = self.llm is not None
        self.playwright_available = False

        # Lazy import — avoids DLL crash at startup if playwright/greenlet is broken
        try:
            from playwright.sync_api import sync_playwright  # noqa: F401
            self._playwright_import = sync_playwright
            self.playwright_available = True
        except Exception as e:
            self.logger.warning(f"Playwright not available: {e}")
            self.playwright_available = False

    def heal_selector(self, html_snippet: str, failed_selector: str) -> str:
        if not self.ollama_available or not self.llm:
            return "body"

        try:
            prompt = (
                f"Test failed with selector: {failed_selector}\n"
                f"Current HTML snippet (partial): {html_snippet[:2000]}\n\n"
                "Find the correct new selector for what the test probably intended to click.\n"
                "Return ONLY a single CSS selector string (no explanation, just selector)"
            )
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            new_selector = content.strip().strip('"').strip("'")
            return new_selector or "body"
        except Exception as e:
            self.logger.warning(f"Self healing error: {e}")
            return "body"

    def execute_test(self, url: str, selector: str) -> dict:
        if not self.playwright_available:
            return {
                "status": "error",
                "message": "Playwright not available — please install dependencies and run: playwright install chromium",
            }

        try:
            with self._playwright_import() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                try:
                    page.goto(url, timeout=30000)
                    page.click(selector, timeout=5000)
                    result = {
                        "status": "success",
                        "selector": selector,
                        "message": "Test passed successfully",
                    }
                except Exception as e1:
                    result = {
                        "status": "error",
                        "selector": selector,
                        "message": str(e1),
                    }
                finally:
                    browser.close()
                return result
        except Exception as e2:
            return {"status": "error", "message": str(e2)}
