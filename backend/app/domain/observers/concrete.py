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
    """Observer dispatching alerts (Real SMTP + Enterprise Outbox) on lifecycle changes."""
    def __init__(self):
        self.dispatched_notifications: List[dict] = []

    def _get_email_service(self):
        try:
            from backend.app.infrastructure.email.smtp_service import EmailService
            return EmailService()
        except Exception:
            return None

    def on_state_changed(self, incident: "Incident", audit_record: AuditRecord) -> None:
        recipients = []
        if incident.reporter and incident.reporter.email:
            recipients.append(incident.reporter.email)
        if incident.assigned_technician and incident.assigned_technician.email:
            recipients.append(incident.assigned_technician.email)

        title = f"Incident {incident.id} Status: {audit_record.new_state}"
        notice = {
            "incident_id": incident.id,
            "type": "STATE_CHANGE",
            "recipients": recipients,
            "title": title,
            "message": audit_record.description
        }
        self.dispatched_notifications.append(notice)

        svc = self._get_email_service()
        if svc and recipients:
            html = f"<div style='font-family:sans-serif;padding:20px;background:#0c0c0c;color:#fff;'><h2>{title}</h2><p>{audit_record.description}</p></div>"
            svc.send_email(recipients, title, html, audit_record.description, "STATE_CHANGE")

    def on_incident_created(self, incident: "Incident") -> None:
        recipients = [incident.reporter.email] if incident.reporter and incident.reporter.email else []
        title = f"Incident {incident.id} Logged Successfully"
        message = f"Your report '{incident.title}' has been logged as {incident.priority.value}."
        notice = {
            "incident_id": incident.id,
            "type": "CREATED",
            "recipients": recipients,
            "title": title,
            "message": message
        }
        self.dispatched_notifications.append(notice)

        svc = self._get_email_service()
        if svc and incident.reporter:
            svc.send_incident_created_email(
                incident_id=incident.id,
                title=incident.title,
                priority=incident.priority.value,
                service_name=incident.service.name if incident.service else "Core Service",
                reporter_email=incident.reporter.email,
                response_deadline=str(incident.sla_tracker.response_deadline) if incident.sla_tracker else "Standard"
            )

    def on_sla_warning(self, incident: "Incident", message: str) -> None:
        recipients = [incident.assigned_technician.email] if incident.assigned_technician and incident.assigned_technician.email else []
        title = f"⚠️ SLA Warning: {incident.id}"
        notice = {
            "incident_id": incident.id,
            "type": "SLA_WARNING",
            "recipients": recipients,
            "title": title,
            "message": message
        }
        self.dispatched_notifications.append(notice)

        svc = self._get_email_service()
        if svc and recipients:
            html = f"<div style='font-family:sans-serif;padding:20px;background:#0c0c0c;color:#f59e0b;'><h2>{title}</h2><p>{message}</p></div>"
            svc.send_email(recipients, title, html, message, "SLA_WARNING")

    def on_sla_breached(self, incident: "Incident", message: str) -> None:
        recipients = ["admin@itsm.local"]
        if incident.assigned_technician and incident.assigned_technician.email:
            recipients.append(incident.assigned_technician.email)
        title = f"🚨 SLA VIOLATION: {incident.id}"
        notice = {
            "incident_id": incident.id,
            "type": "SLA_BREACH",
            "recipients": recipients,
            "title": title,
            "message": message
        }
        self.dispatched_notifications.append(notice)

        svc = self._get_email_service()
        if svc:
            html = f"<div style='font-family:sans-serif;padding:20px;background:#0c0c0c;color:#ef4444;'><h2>{title}</h2><p>{message}</p></div>"
            svc.send_email(recipients, title, html, message, "SLA_BREACH")

