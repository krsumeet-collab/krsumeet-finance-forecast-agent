"""Cloud DLP Sanitization and PII/Sensitive Data Redaction Module."""
import re
from typing import Dict, Any


class CloudDLPSanitizer:
    """Simulates Google Cloud Data Loss Prevention (DLP) redaction rules

    for corporate financial and employee data.
    """

    # Regex patterns for sensitive entities
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    PHONE_PATTERN = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")
    SALARY_PATTERN = re.compile(r"(?:salary|compensation|equity|bonus|comp|package)\s*[:=]?\s*\$?\d{2,3}(?:,\d{3})*(?:\.\d{2})?", re.IGNORECASE)
    DISCOUNT_PATTERN = re.compile(r"discount\s*(?:rate|percentage|of|\s)*[:=]?\s*(\d{1,2}%|\d{1,2}\.\d+%)", re.IGNORECASE)
    CREDIT_CARD_PATTERN = re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b")

    def sanitize_text(self, text: str) -> str:
        """Applies DLP transformation templates to redact PII and confidential terms."""
        if not text:
            return ""

        sanitized = text
        sanitized = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", sanitized)
        sanitized = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
        sanitized = self.SALARY_PATTERN.sub("[CONFIDENTIAL_COMPENSATION_REDACTED]", sanitized)
        sanitized = self.DISCOUNT_PATTERN.sub("[REDACTED_DISCOUNT_TERMS]", sanitized)
        sanitized = self.CREDIT_CARD_PATTERN.sub("[REDACTED_PAYMENT_INFO]", sanitized)
        return sanitized

    def sanitize_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitizes dictionary strings."""
        sanitized_dict = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized_dict[key] = self.sanitize_text(value)
            elif isinstance(value, dict):
                sanitized_dict[key] = self.sanitize_payload(value)
            elif isinstance(value, list):
                sanitized_dict[key] = [
                    self.sanitize_text(v) if isinstance(v, str) else v for v in value
                ]
            else:
                sanitized_dict[key] = value
        return sanitized_dict


dlp_sanitizer = CloudDLPSanitizer()
