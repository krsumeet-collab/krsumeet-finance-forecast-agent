"""Pre-Execution Security Guardrails & Domain Boundary Enforcement."""
import re
from typing import Tuple
from src.models.schemas import GuardrailVerdictEnum
from src.security.dlp_sanitizer import dlp_sanitizer


class PreExecutionGuardrails:
    """Pre-model execution classifier intercepting adversarial jailbreaks,

    prompt injections, data exfiltration attempts, and out-of-scope requests.
    """

    ADVERSARIAL_PATTERNS = [
        re.compile(r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions", re.IGNORECASE),
        re.compile(r"system\s+override", re.IGNORECASE),
        re.compile(r"drop\s+table", re.IGNORECASE),
        re.compile(r"(?:salary|compensation|equity)\s+packages?", re.IGNORECASE),
        re.compile(r"scrape\s+personal\s+(?:cell\s+)?phone\s+numbers?", re.IGNORECASE),
        re.compile(r"print\s+(?:out\s+)?(?:the\s+)?(?:raw\s+)?(?:api\s+keys|credentials|secrets)", re.IGNORECASE),
        re.compile(r"act\s+as\s+(?:an?\s+)?unrestricted\s+ai", re.IGNORECASE),
        re.compile(r"bypass\s+human\s+approval", re.IGNORECASE),
        re.compile(r"disregard\s+fp&a\s+guidelines", re.IGNORECASE),
        re.compile(r"force\s+forecast\s+simulation\s+with\s+negative\s+revenue", re.IGNORECASE),
        re.compile(r"board\s+minutes", re.IGNORECASE),
    ]

    ALLOWED_FPNA_DOMAINS = [
        "forecast", "revenue", "pipeline", "variance", "ebitda", "arr", "mrr",
        "cogs", "looker", "salesforce", "workday", "bloomberg", "emea", "latam",
        "na", "apac", "q1", "q2", "q3", "q4", "risk", "simulation", "slippage"
    ]

    def evaluate(self, prompt: str) -> Tuple[GuardrailVerdictEnum, str]:
        """Classifies the prompt before dispatching to the LLM or tool execution.

        Returns (verdict, reason).
        """
        if not prompt or not prompt.strip():
            return GuardrailVerdictEnum.BLOCK, "Empty prompt provided."

        # Check for adversarial jailbreak and injection patterns
        for pattern in self.ADVERSARIAL_PATTERNS:
            if pattern.search(prompt):
                return GuardrailVerdictEnum.BLOCK, f"Security Violation: Adversarial injection or exfiltration pattern detected ('{pattern.pattern}')."

        # Check FP&A domain relevance
        lower_prompt = prompt.lower()
        has_domain_term = any(term in lower_prompt for term in self.ALLOWED_FPNA_DOMAINS)
        if not has_domain_term:
            return GuardrailVerdictEnum.BLOCK, "Domain Scope Violation: Query outside FP&A operational and financial forecasting boundaries."

        # Apply DLP sanitization check
        sanitized = dlp_sanitizer.sanitize_text(prompt)
        if sanitized != prompt:
            return GuardrailVerdictEnum.SANITIZE, "Sensitive PII or confidential terms detected and sanitized via Cloud DLP."

        return GuardrailVerdictEnum.PERMIT, "Prompt passed pre-execution security verification."


guardrails = PreExecutionGuardrails()
