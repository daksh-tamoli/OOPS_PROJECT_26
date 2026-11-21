from typing import Dict, List
from backend.app.domain.models.enums import IncidentCategory


class IntelligentCategorizer:
    """Automated NLP/Rule-based Incident Categorizer."""

    _CATEGORY_KEYWORDS: Dict[IncidentCategory, List[str]] = {
        IncidentCategory.DATABASE: ["database", "postgres", "mysql", "deadlock", "query", "sql", "table", "db"],
        IncidentCategory.NETWORK: ["network", "dns", "latency", "packet", "vpn", "router", "switch", "firewall", "wifi", "bandwidth"],
        IncidentCategory.AUTHENTICATION: ["login", "sso", "password", "token", "jwt", "auth", "mfa", "unauthorized", "credentials"],
        IncidentCategory.PAYMENT: ["payment", "transaction", "checkout", "stripe", "billing", "invoice", "credit card"],
        IncidentCategory.CLOUD: ["aws", "azure", "gcp", "s3", "ec2", "cluster", "kubernetes", "cloud", "pod"],
        IncidentCategory.SECURITY: ["breach", "malware", "phishing", "vulnerability", "attack", "ddos", "ransomware", "leak"],
        IncidentCategory.HARDWARE: ["printer", "laptop", "monitor", "cpu", "disk failure", "hardware", "server fan"],
        IncidentCategory.APPLICATION: ["crash", "ui", "bug", "frontend", "500 internal", "blank page", "error code"],
    }

    def suggest_category(self, title: str, description: str) -> IncidentCategory:
        text = f"{title} {description}".lower()
        best_category = IncidentCategory.APPLICATION
        max_matches = 0

        for category, keywords in self._CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in text)
            if matches > max_matches:
                max_matches = matches
                best_category = category

        return best_category

    @classmethod
    def get_all_categories(cls) -> Dict[str, List[str]]:
        """Returns all configured categories and their NLP detection keywords."""
        return {
            (cat.value if hasattr(cat, "value") else str(cat)): keywords
            for cat, keywords in cls._CATEGORY_KEYWORDS.items()
        }

    @classmethod
    def add_or_update_category(cls, category_name: str, keywords: List[str]) -> None:
        """Dynamically register or update a custom category and its keywords."""
        cat_key = category_name.upper().replace(" ", "_")
        cls._CATEGORY_KEYWORDS[cat_key] = [k.strip().lower() for k in keywords if k.strip()]
