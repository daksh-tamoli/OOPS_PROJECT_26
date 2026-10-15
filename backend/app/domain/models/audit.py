from datetime import datetime, timezone
from typing import Optional
import uuid


class AuditRecord:
    """Immutable audit record documenting lifecycle state transitions and actions."""
    def __init__(
        self,
        incident_id: str,
        actor_id: str,
        actor_name: str,
        action: str,
        previous_state: str,
        new_state: str,
        description: str,
        record_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        self.id = record_id or str(uuid.uuid4())
        self.incident_id = incident_id
        self.actor_id = actor_id
        self.actor_name = actor_name
        self.action = action
        self.previous_state = previous_state
        self.new_state = new_state
        self.description = description
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "incident_id": self.incident_id,
            "timestamp": self.timestamp.isoformat(),
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "action": self.action,
            "previous_state": self.previous_state,
            "new_state": self.new_state,
            "description": self.description,
        }
