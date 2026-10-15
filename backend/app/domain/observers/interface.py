from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.app.domain.models.incident import Incident
    from backend.app.domain.models.audit import AuditRecord


class IIncidentObserver(ABC):
    """Observer interface in the Observer Design Pattern."""

    @abstractmethod
    def on_state_changed(self, incident: "Incident", audit_record: "AuditRecord") -> None:
        """Invoked when an incident transitions from one lifecycle state to another."""
        pass

    @abstractmethod
    def on_incident_created(self, incident: "Incident") -> None:
        """Invoked immediately after an incident is registered."""
        pass

    @abstractmethod
    def on_sla_warning(self, incident: "Incident", message: str) -> None:
        """Invoked when an incident is in danger of breaching its SLA."""
        pass

    @abstractmethod
    def on_sla_breached(self, incident: "Incident", message: str) -> None:
        """Invoked when an incident has violated its SLA response/resolution target."""
        pass
