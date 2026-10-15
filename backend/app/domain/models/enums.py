from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE = "EMPLOYEE"
    TECHNICIAN = "TECHNICIAN"
    ADMIN = "ADMIN"


class IncidentStatus(str, Enum):
    NEW = "NEW"
    CLASSIFIED = "CLASSIFIED"
    ASSIGNED = "ASSIGNED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


class Priority(str, Enum):
    P1 = "P1"  # Critical (e.g., 5m response / 30m resolution)
    P2 = "P2"  # High (e.g., 15m response / 2h resolution)
    P3 = "P3"  # Medium (e.g., 1h response / 8h resolution)
    P4 = "P4"  # Low (e.g., 4h response / 24h resolution)


class Impact(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Urgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentCategory(str, Enum):
    HARDWARE = "Hardware"
    SOFTWARE = "Software"
    NETWORK = "Network"
    DATABASE = "Database"
    CLOUD = "Cloud"
    SECURITY = "Security"
    AUTHENTICATION = "Authentication"
    APPLICATION = "Application"
    STORAGE = "Storage"
    PAYMENT = "Payment"


class ServiceTier(str, Enum):
    TIER_1_CRITICAL = "TIER_1_CRITICAL"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"
