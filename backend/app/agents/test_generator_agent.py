from app.agents.base import get_llm
import json
import re


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", text.lower().strip())[:60]


def _smart_fallback_tests(requirements: dict) -> list:
    """
    Generate varied, context-aware test cases from structured requirements
    without needing an LLM.  Produces different tests based on the actual
    content rather than a single generic template.
    """
    func_reqs = requirements.get("functional_requirements", [])
    objectives = requirements.get("test_objectives", [])
    complexity = requirements.get("complexity", "medium")
    all_text = " ".join(func_reqs + objectives).lower()

    tests = []

    # ---- Auth tests -------------------------------------------------------
    auth_words = {"login", "logout", "register", "signup", "sign in", "password",
                  "auth", "credential", "token", "session"}
    if any(w in all_text for w in auth_words):
        tests.append({
            "title": "Valid User Login",
            "description": "Verify a registered user can log in with correct credentials",
            "test_type": "functional",
            "preconditions": "User account exists in the system",
            "steps": [
                "Navigate to the login page",
                "Enter valid email and password",
                "Click the Login button",
            ],
            "expected_result": "User is redirected to dashboard and session token is issued",
        })
        tests.append({
            "title": "Invalid Login Credentials",
            "description": "Verify login fails gracefully with wrong password",
            "test_type": "negative",
            "preconditions": "Login page is accessible",
            "steps": [
                "Navigate to the login page",
                "Enter valid email with incorrect password",
                "Click the Login button",
            ],
            "expected_result": "Error message shown; user is NOT authenticated",
        })

    # ---- Cart tests -------------------------------------------------------
    cart_words = {"cart", "basket", "add to cart", "item", "quantity", "product", "remove"}
    if any(w in all_text for w in cart_words):
        tests.append({
            "title": "Add Item to Cart",
            "description": "Verify a product can be added to the shopping cart",
            "test_type": "functional",
            "preconditions": "User is logged in; at least one product exists",
            "steps": [
                "Navigate to a product page",
                "Click 'Add to Cart'",
                "Open the cart",
            ],
            "expected_result": "Product appears in cart with correct quantity and price",
        })
        tests.append({
            "title": "Cart Persistence Across Sessions",
            "description": "Verify cart items persist after logout and login",
            "test_type": "functional",
            "preconditions": "User has items in cart",
            "steps": [
                "Add items to cart",
                "Log out",
                "Log back in",
                "Open the cart",
            ],
            "expected_result": "Cart still contains the previously added items",
        })

    # ---- Payment tests ----------------------------------------------------
    payment_words = {"payment", "stripe", "checkout", "billing", "card", "order", "pay"}
    if any(w in all_text for w in payment_words):
        tests.append({
            "title": "Successful Payment Flow",
            "description": "Verify end-to-end checkout with a valid card",
            "test_type": "functional",
            "preconditions": "User has items in cart; test Stripe card available",
            "steps": [
                "Proceed to checkout",
                "Enter shipping address",
                "Enter valid test card number",
                "Click 'Place Order'",
            ],
            "expected_result": "Order confirmation shown; confirmation email triggered",
        })
        tests.append({
            "title": "Failed Payment Handling",
            "description": "Verify system handles a declined card gracefully",
            "test_type": "negative",
            "preconditions": "User is on checkout page",
            "steps": [
                "Enter a declined test card number",
                "Submit payment",
            ],
            "expected_result": "Error message shown; no order created; cart is preserved",
        })

    # ---- Generic functional test from first requirement -------------------
    if func_reqs and len(tests) < 2:
        first_req = func_reqs[0][:120]
        tests.append({
            "title": f"Core Feature: {first_req[:50]}",
            "description": f"Verify the following requirement works correctly: {first_req}",
            "test_type": "functional",
            "preconditions": "Application is running and accessible",
            "steps": [
                "Open the application",
                f"Exercise the feature: {first_req[:80]}",
                "Verify the outcome",
            ],
            "expected_result": "Feature behaves as described in the requirement",
        })

    # ---- Always include a boundary / edge-case test -----------------------
    complexity_steps = {
        "high": [
            "Test with maximum allowed input length",
            "Test with special characters in all fields",
            "Submit form with all optional fields empty",
        ],
        "medium": [
            "Test with empty required fields",
            "Test with maximum allowed input",
        ],
        "low": [
            "Test with empty input",
            "Test with valid minimum input",
        ],
    }
    tests.append({
        "title": "Input Boundary & Edge Cases",
        "description": "Verify the application handles boundary values and edge cases",
        "test_type": "boundary",
        "preconditions": "Application is running",
        "steps": complexity_steps.get(complexity, complexity_steps["medium"]),
        "expected_result": "Application validates input and shows meaningful error messages",
    })

    return tests[:5]  # cap at 5


class TestGeneratorAgent:
    def __init__(self):
        try:
            self.llm = get_llm()
            self.ollama_available = True
        except Exception:
            self.ollama_available = False

    def generate_test_cases(self, requirements: dict) -> list:
        if self.ollama_available:
            try:
                req_content = json.dumps(requirements, indent=2)
                prompt = f"""Generate 4-5 comprehensive, specific test cases for the following requirements.

Requirements:
{req_content}

Return ONLY a JSON array. Each element must have:
{{
  "title": "Specific descriptive test title (not generic)",
  "description": "What this test verifies",
  "test_type": "functional|boundary|negative|edge_case|security|performance",
  "preconditions": "Setup needed before running",
  "steps": ["Step 1", "Step 2", "Step 3"],
  "expected_result": "Exact expected outcome"
}}

IMPORTANT: Make titles specific to the actual requirements, not generic. Return ONLY the JSON array."""

                response = self.llm.invoke(prompt)
                if "[" in response and "]" in response:
                    start = response.index("[")
                    end = response.rindex("]") + 1
                    tests = json.loads(response[start:end])
                    if isinstance(tests, list) and len(tests) > 0:
                        return tests
            except Exception as e:
                print(f"TestGeneratorAgent error: {e}")

        return _smart_fallback_tests(requirements)

    def generate_playwright_script(self, test_case: dict) -> str:
        title = test_case.get("title", "Test Case")
        fn_name = f"test_{_slugify(title)}"
        steps = test_case.get("steps", [])
        description = test_case.get("description", "")
        expected = test_case.get("expected_result", "")
        preconditions = test_case.get("preconditions", "")

        step_comments = "\n        ".join(f"# {s}" for s in steps)

        return f'''import pytest
from playwright.sync_api import Page, expect


def {fn_name}(page: Page):
    """
    {description}

    Preconditions: {preconditions}
    Expected:      {expected}
    """
    # TODO: Set your base URL
    base_url = "http://localhost:3000"
    page.goto(base_url)

    {step_comments}

    # Add your assertions here
    # expect(page.locator("...")).to_be_visible()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''.strip()
