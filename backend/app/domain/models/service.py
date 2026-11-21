from typing import Optional, List
import uuid
from backend.app.domain.models.enums import ServiceTier
from backend.app.domain.models.sla import SLAPolicy


class ITService:
    """Represents an IT service within the organization (e.g., Payment, Database, Auth)."""
    def __init__(
        self,
        name: str,
        description: str,
        tier: ServiceTier = ServiceTier.TIER_2,
        sla_policy: Optional[SLAPolicy] = None,
        service_id: Optional[str] = None,
        is_active: bool = True,
        dependencies: Optional[List[str]] = None
    ):
        self.id = service_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.tier = tier
        self.sla_policy = sla_policy or SLAPolicy(name=f"Standard SLA for {name}")
        self.is_active = is_active
        self.dependencies: List[str] = dependencies or []

    @property
    def criticality_multiplier(self) -> float:
        """Returns business criticality weight based on tier."""
        if self.tier == ServiceTier.TIER_1_CRITICAL:
            return 1.5
        elif self.tier == ServiceTier.TIER_2:
            return 1.0
        return 0.7

    def add_dependency(self, service_id: str) -> None:
        """Adds upstream service dependency."""
        if service_id not in self.dependencies and service_id != self.id:
            self.dependencies.append(service_id)

    def __repr__(self) -> str:
        return f"<ITService id={self.id} name='{self.name}' tier={self.tier.value} deps={self.dependencies}>"

