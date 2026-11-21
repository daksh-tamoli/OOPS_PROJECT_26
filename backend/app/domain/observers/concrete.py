from typing import List, Optional, TYPE_CHECKING
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


class InAppNotificationObserver(IIncidentObserver):
    """
    Second Distinct Notification Channel (Observer Pattern):
    Dispatches live In-App / Dashboard notifications to target users with unread tracking.
    """
    def __init__(self):
        import uuid
        self.notifications: List[dict] = []

    def _add_notification(self, user_id: str, incident_id: str, title: str, message: str, notif_type: str) -> None:
        import uuid
        from datetime import datetime, timezone
        self.notifications.insert(0, {
            "id": f"NOTIF-{uuid.uuid4().hex[:8].upper()}",
            "user_id": user_id,
            "incident_id": incident_id,
            "title": title,
            "message": message,
            "type": notif_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_read": False
        })

    def on_state_changed(self, incident: "Incident", audit_record: AuditRecord) -> None:
        title = f"Ticket {incident.id} Updated"
        msg = f"Status changed to {audit_record.new_state}: {audit_record.description}"
        if incident.reporter:
            self._add_notification(incident.reporter.id, incident.id, title, msg, "STATUS_UPDATE")
        if incident.assigned_technician and (not incident.reporter or incident.reporter.id != incident.assigned_technician.id):
            self._add_notification(incident.assigned_technician.id, incident.id, title, msg, "STATUS_UPDATE")

    def on_incident_created(self, incident: "Incident") -> None:
        if incident.reporter:
            self._add_notification(
                incident.reporter.id,
                incident.id,
                f"Ticket {incident.id} Created",
                f"Your incident '{incident.title}' has been logged ({incident.priority.value}).",
                "TICKET_CREATED"
            )
        if incident.assigned_technician:
            self._add_notification(
                incident.assigned_technician.id,
                incident.id,
                f"New Assignment: {incident.id}",
                f"You have been assigned to '{incident.title}' ({incident.priority.value}).",
                "TICKET_ASSIGNED"
            )

    def on_sla_warning(self, incident: "Incident", message: str) -> None:
        if incident.assigned_technician:
            self._add_notification(
                incident.assigned_technician.id,
                incident.id,
                f"⚠️ SLA Warning: {incident.id}",
                message,
                "SLA_WARNING"
            )

    def on_sla_breached(self, incident: "Incident", message: str) -> None:
        # Notify admin and technician
        self._add_notification(
            "user-admin-1",
            incident.id,
            f"🚨 SLA Breach: {incident.id}",
            message,
            "SLA_BREACH"
        )
        if incident.assigned_technician:
            self._add_notification(
                incident.assigned_technician.id,
                incident.id,
                f"🚨 SLA Breach: {incident.id}",
                message,
                "SLA_BREACH"
            )

    def get_user_notifications(self, user_id: Optional[str] = None, unread_only: bool = False) -> List[dict]:
        res = self.notifications
        if user_id:
            res = [n for n in res if n["user_id"] == user_id or n["user_id"] == "user-admin-1"]
        if unread_only:
            res = [n for n in res if not n["is_read"]]
        return res

    def mark_as_read(self, notification_id: str) -> bool:
        for n in self.notifications:
            if n["id"] == notification_id:
                n["is_read"] = True
                return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        count = 0
        for n in self.notifications:
            if n["user_id"] == user_id and not n["is_read"]:
                n["is_read"] = True
                count += 1
        return count

