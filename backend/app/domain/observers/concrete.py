from typing import List, TYPE_CHECKING
from backend.app.domain.observers.interface import IIncidentObserver
from backend.app.domain.models.audit import AuditRecord

if TYPE_CHECKING:
    from backend.app.domain.models.incident import Incident


class AuditObserver(IIncidentObserver):
    """Observer that persists every incident lifecycle transition into an immutable audit trail."""
    def __init__(self):
        self.recorded_events: List[dict] = []

    def on_state_changed(self, incident: "Incident", audit_record: AuditRecord) -> None:
        self.recorded_events.append(audit_record.to_dict())

    def on_incident_created(self, incident: "Incident") -> None:
        pass

    def on_sla_warning(self, incident: "Incident", message: str) -> None:
        pass

    def on_sla_breached(self, incident: "Incident", message: str) -> None:
        pass


class NotificationObserver(IIncidentObserver):
    """Observer dispatching simulated alerts (In-App, Email, Dashboard) on lifecycle changes."""
    def __init__(self):
        self.dispatched_notifications: List[dict] = []

    def on_state_changed(self, incident: "Incident", audit_record: AuditRecord) -> None:
        recipients = []
        if incident.reporter:
            recipients.append(incident.reporter.email)
        if incident.assigned_technician:
            recipients.append(incident.assigned_technician.email)

        notice = {
            "incident_id": incident.id,
            "type": "STATE_CHANGE",
            "recipients": recipients,
            "title": f"Incident {incident.id} Status: {audit_record.new_state}",
            "message": audit_record.description
        }
        self.dispatched_notifications.append(notice)

    def on_incident_created(self, incident: "Incident") -> None:
        notice = {
            "incident_id": incident.id,
            "type": "CREATED",
            "recipients": [incident.reporter.email],
            "title": f"Incident {incident.id} Logged Successfully",
            "message": f"Your report '{incident.title}' has been logged as {incident.priority.value}."
        }
        self.dispatched_notifications.append(notice)

    def on_sla_warning(self, incident: "Incident", message: str) -> None:
        recipients = [incident.assigned_technician.email] if incident.assigned_technician else []
        notice = {
            "incident_id": incident.id,
            "type": "SLA_WARNING",
            "recipients": recipients,
            "title": f"⚠️ SLA Warning: {incident.id}",
            "message": message
        }
        self.dispatched_notifications.append(notice)

    def on_sla_breached(self, incident: "Incident", message: str) -> None:
        recipients = ["admin@itsm.local"]
        if incident.assigned_technician:
            recipients.append(incident.assigned_technician.email)
        notice = {
            "incident_id": incident.id,
            "type": "SLA_BREACH",
            "recipients": recipients,
            "title": f"🚨 SLA VIOLATION: {incident.id}",
            "message": message
        }
        self.dispatched_notifications.append(notice)
