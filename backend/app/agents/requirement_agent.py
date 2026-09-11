from app.agents.base import get_llm
import json
import re


# ---------------------------------------------------------------------------
# Keyword sets used by the smart fallback parser
# ---------------------------------------------------------------------------
_AUTH_KEYWORDS = {"login", "logout", "register", "signup", "sign up", "sign in",
                  "password", "auth", "authentication", "token", "jwt", "oauth",
                  "session", "credential", "verify", "email"}

_PAYMENT_KEYWORDS = {"payment", "stripe", "checkout", "billing", "invoice", "card",
                     "transaction", "order", "purchase", "pay", "subscription"}

_CART_KEYWORDS = {"cart", "basket", "add to cart", "remove", "quantity", "item",
                  "product", "wishlist"}

_PERFORMANCE_KEYWORDS = {"fast", "speed", "load", "performance", "latency", "timeout",
                         "concurrent", "scalable", "response time", "millisecond"}

_SECURITY_KEYWORDS = {"secure", "ssl", "https", "encrypt", "xss", "csrf", "injection",
                      "sanitize", "validate", "permission", "role", "access control"}

_UI_KEYWORDS = {"button", "form", "input", "page", "navigate", "display", "show",
                "render", "modal", "dropdown", "menu", "screen", "view"}


def _smart_fallback(content: str) -> dict:
    """Parse requirements text without an LLM and produce meaningful structured data."""
    text_lower = content.lower()
    words = set(re.findall(r"\b\w+\b", text_lower))

    # Split into sentences for functional requirement extraction
    sentences = [s.strip() for s in re.split(r"[.\n;]+", content) if len(s.strip()) > 15]

    functional = []
    non_functional = []
    test_objectives = []
    risks = []

    for sentence in sentences:
        sl = sentence.lower()
        # Classify as non-functional if it matches perf/security keywords
        if words & _PERFORMANCE_KEYWORDS and any(k in sl for k in _PERFORMANCE_KEYWORDS):
            non_functional.append(sentence)
        elif words & _SECURITY_KEYWORDS and any(k in sl for k in _SECURITY_KEYWORDS):
            non_functional.append(sentence)
        else:
            functional.append(sentence)

    # Deduplicate and cap
    functional = list(dict.fromkeys(functional))[:8]
    non_functional = list(dict.fromkeys(non_functional))[:4]

    # Derive test objectives from detected domains
    if words & _AUTH_KEYWORDS:
        test_objectives.append("Verify user authentication and session management")
    if words & _PAYMENT_KEYWORDS:
        test_objectives.append("Verify payment processing and order creation")
    if words & _CART_KEYWORDS:
        test_objectives.append("Verify shopping cart add/remove/update operations")
    if words & _UI_KEYWORDS:
        test_objectives.append("Verify UI elements render and respond correctly")
    if not test_objectives:
        test_objectives.append("Verify core application functionality works as expected")

    # Derive risks
    if words & _PAYMENT_KEYWORDS:
        risks.append("Payment failures could cause revenue loss — needs robust error handling")
    if words & _AUTH_KEYWORDS:
        risks.append("Authentication bypass is a critical security risk")
    if words & _SECURITY_KEYWORDS:
        risks.append("Security vulnerabilities may expose user data")
    if not risks:
        risks.append("Untested edge cases may cause unexpected failures in production")

    # Estimate complexity
    total_sentences = len(sentences)
    has_payment = bool(words & _PAYMENT_KEYWORDS)
    has_auth = bool(words & _AUTH_KEYWORDS)
    if total_sentences > 6 or (has_payment and has_auth):
        complexity = "high"
    elif total_sentences > 3 or has_payment or has_auth:
        complexity = "medium"
    else:
        complexity = "low"

    return {
        "functional_requirements": functional if functional else [content[:300]],
        "non_functional_requirements": non_functional,
        "test_objectives": test_objectives,
        "risks": risks,
        "complexity": complexity,
    }


class RequirementAgent:
    def __init__(self):
        try:
            self.llm = get_llm()
            self.ollama_available = True
        except Exception:
            self.ollama_available = False

    def analyze_requirement(self, content: str) -> dict:
        # Always try LLM first
        if self.ollama_available:
            try:
                prompt = f"""Analyze the following software requirements and extract structured information.

Requirements:
{content}

Return ONLY a valid JSON object with exactly these keys:
{{
  "functional_requirements": ["list of specific functional requirements as strings"],
  "non_functional_requirements": ["list of performance/security/usability requirements"],
  "test_objectives": ["list of what should be tested"],
  "risks": ["list of potential risks or failure areas"],
  "complexity": "low|medium|high"
}}

Return ONLY the JSON, no explanation."""

                response = self.llm.invoke(prompt)
                if "{" in response and "}" in response:
                    start = response.index("{")
                    end = response.rindex("}") + 1
                    parsed = json.loads(response[start:end])
                    # Validate required keys
                    required = {"functional_requirements", "non_functional_requirements",
                                "test_objectives", "risks", "complexity"}
                    if required.issubset(parsed.keys()):
                        return parsed
            except Exception as e:
                print(f"Error in RequirementAgent LLM call: {e}")

        # Smart fallback — much better than the old generic template
        return _smart_fallback(content)
