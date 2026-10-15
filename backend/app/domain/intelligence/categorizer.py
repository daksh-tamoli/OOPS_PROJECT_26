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
