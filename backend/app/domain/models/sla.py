from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
import uuid
from backend.app.domain.models.enums import Priority


class SLATarget:
    """Encapsulates response and resolution time targets."""
    def __init__(self, response_minutes: int, resolution_minutes: int):
        self.response_minutes = response_minutes
        self.resolution_minutes = resolution_minutes


class SLAPolicy:
    """Defines Service Level Agreement targets per priority tier."""
    def __init__(
        self,
        name: str,
        targets: Optional[Dict[Priority, SLATarget]] = None,
        policy_id: Optional[str] = None
    ):
        self.id = policy_id or str(uuid.uuid4())
        self.name = name
        self.targets: Dict[Priority, SLATarget] = targets or self._default_targets()

    @staticmethod
    def _default_targets() -> Dict[Priority, SLATarget]:
        # Based on project specification page 7:
        # P1: 5 min response / 30 min resolution
        # P2: 15 min response / 2 hr (120m) resolution
        # P3: 1 hr (60m) response / 8 hr (480m) resolution
        # P4: 4 hr (240m) response / 24 hr (1440m) resolution
        return {
            Priority.P1: SLATarget(response_minutes=5, resolution_minutes=30),
            Priority.P2: SLATarget(response_minutes=15, resolution_minutes=120),
            Priority.P3: SLATarget(response_minutes=60, resolution_minutes=480),
            Priority.P4: SLATarget(response_minutes=240, resolution_minutes=1440),
        }

    def get_target(self, priority: Priority) -> SLATarget:
        return self.targets.get(priority, self.targets[Priority.P3])


class SLAStatusTracker:
    """Tracks deadline calculation, compliance, and breach detection for an incident."""
    def __init__(
        self,
        created_at: datetime,
        target: SLATarget,
        response_deadline: Optional[datetime] = None,
        resolution_deadline: Optional[datetime] = None,
        responded_at: Optional[datetime] = None,
        resolved_at: Optional[datetime] = None,
        is_breached: bool = False
    ):
        self.created_at = created_at
        self.target = target
        self.response_deadline = response_deadline or (created_at + timedelta(minutes=target.response_minutes))
        self.resolution_deadline = resolution_deadline or (created_at + timedelta(minutes=target.resolution_minutes))
        self.responded_at = responded_at
        self.resolved_at = resolved_at
        self.is_breached = is_breached

    def mark_responded(self, timestamp: Optional[datetime] = None) -> None:
        self.responded_at = timestamp or datetime.now(timezone.utc)
        if self.responded_at > self.response_deadline:
            self.is_breached = True

    def mark_resolved(self, timestamp: Optional[datetime] = None) -> None:
        self.resolved_at = timestamp or datetime.now(timezone.utc)
        if self.resolved_at > self.resolution_deadline:
            self.is_breached = True

    def check_breach(self, current_time: Optional[datetime] = None) -> bool:
        now = current_time or datetime.now(timezone.utc)
        if self.responded_at is None and now > self.response_deadline:
            self.is_breached = True
        if self.resolved_at is None and now > self.resolution_deadline:
            self.is_breached = True
        return self.is_breached

    def is_resolution_at_risk(self, current_time: Optional[datetime] = None, warning_ratio: float = 0.70) -> bool:
        """Flags incident if elapsed resolution time exceeds warning_ratio (e.g. 70%)."""
        if self.resolved_at is not None:
            return False
        now = current_time or datetime.now(timezone.utc)
        total_duration = (self.resolution_deadline - self.created_at).total_seconds()
        elapsed = (now - self.created_at).total_seconds()
        return (elapsed / total_duration) >= warning_ratio if total_duration > 0 else False
