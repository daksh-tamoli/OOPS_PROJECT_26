from abc import ABC, abstractmethod
from backend.app.domain.models.enums import Priority, Impact, Urgency, ServiceTier
from backend.app.domain.models.service import ITService


class IPriorityStrategy(ABC):
    """Abstract Strategy interface for calculating incident priority."""

    @abstractmethod
    def calculate_priority(self, impact: Impact, urgency: Urgency, service: ITService) -> Priority:
        """Determines the Priority tier (P1, P2, P3, P4)."""
        pass


class MatrixPriorityStrategy(IPriorityStrategy):
    """
    Standard ITIL 3x3 / 4x4 Risk Matrix:
    Maps Impact and Urgency directly to Priority levels.
    """
    def calculate_priority(self, impact: Impact, urgency: Urgency, service: ITService) -> Priority:
        # If service is Tier 1 Critical and impact is Critical, elevate to P1 immediately
        if service.tier == ServiceTier.TIER_1_CRITICAL and impact in (Impact.CRITICAL, Impact.HIGH):
            return Priority.P1

        if impact == Impact.CRITICAL or urgency == Impact.CRITICAL:
            if impact == Impact.CRITICAL and urgency == Urgency.CRITICAL:
                return Priority.P1
            elif urgency in (Urgency.HIGH, Urgency.CRITICAL) or impact in (Impact.HIGH, Impact.CRITICAL):
                return Priority.P1
            return Priority.P2

        if impact == Impact.HIGH and urgency == Urgency.HIGH:
            return Priority.P2
        elif impact == Impact.HIGH or urgency == Urgency.HIGH:
            return Priority.P3

        if impact == Impact.MEDIUM and urgency == Urgency.MEDIUM:
            return Priority.P3

        return Priority.P4


class WeightedCriticalityStrategy(IPriorityStrategy):
    """
    Mathematical weighted formula as specified in PDF page 6:
    Priority Score = (ImpactWeight * 0.4) + (UrgencyWeight * 0.3) + (BusinessCriticality * 0.3)
    """
    _WEIGHT_MAP = {
        Impact.LOW: 1.0,
        Impact.MEDIUM: 2.0,
        Impact.HIGH: 3.0,
        Impact.CRITICAL: 4.0,
        Urgency.LOW: 1.0,
        Urgency.MEDIUM: 2.0,
        Urgency.HIGH: 3.0,
        Urgency.CRITICAL: 4.0,
    }

    def calculate_priority(self, impact: Impact, urgency: Urgency, service: ITService) -> Priority:
        imp_val = self._WEIGHT_MAP.get(impact, 2.0)
        urg_val = self._WEIGHT_MAP.get(urgency, 2.0)
        crit_multiplier = service.criticality_multiplier  # 1.5, 1.0, 0.7

        score = (imp_val * 0.40) + (urg_val * 0.30) + (crit_multiplier * 2.5 * 0.30)

        if score >= 3.3:
            return Priority.P1
        elif score >= 2.5:
            return Priority.P2
        elif score >= 1.8:
            return Priority.P3
        else:
            return Priority.P4
