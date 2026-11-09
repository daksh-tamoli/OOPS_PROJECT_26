from datetime import datetime, timezone
from typing import List, Optional
from backend.app.domain.models.incident import Incident
from backend.app.domain.models.enums import IncidentStatus, Priority
from backend.app.domain.models.user import User, Administrator


class EscalationLevel:
    LEVEL_1_TECHNICIAN = "Technician"
    LEVEL_2_TEAM_LEAD = "Team Lead"
    LEVEL_3_SYS_ADMIN = "System Administrator"
    LEVEL_4_IT_MANAGER = "IT Manager"


class AutomaticEscalationEngine:
    """
    Automated Hierarchical Incident Escalation Engine.
    Monitors unacknowledged critical/high tickets and elevates recipient chain.
    """
    def __init__(self, escalation_admin: Optional[User] = None):
        self.escalation_admin = escalation_admin or Administrator(
            email="it-manager@itsm.local",
            full_name="IT Escalation Manager"
        )

    def evaluate_incident(self, incident: Incident, current_time: Optional[datetime] = None) -> Optional[str]:
        """
        Evaluates whether an incident requires automatic escalation.
        Returns the new escalation level if escalated, or None.
        """
        now = current_time or datetime.now(timezone.utc)
        tracker = incident.sla_tracker

        # Only escalate open tickets before resolution
        if incident.status in (IncidentStatus.RESOLVED, IncidentStatus.VERIFIED, IncidentStatus.CLOSED):
            return None

        # Check if response SLA is breached while still unacknowledged
        if incident.status in (IncidentStatus.NEW, IncidentStatus.CLASSIFIED, IncidentStatus.ASSIGNED):
            now_utc = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
            deadline = tracker.response_deadline
            deadline_utc = deadline if (deadline and deadline.tzinfo) else (deadline.replace(tzinfo=timezone.utc) if deadline else None)
            if deadline_utc and now_utc > deadline_utc:
                level = EscalationLevel.LEVEL_2_TEAM_LEAD if incident.priority != Priority.P1 else EscalationLevel.LEVEL_4_IT_MANAGER
                msg = f"Automatic Escalation: Incident unacknowledged past response deadline. Escalated to {level}."
                incident.record_action(
                    actor=self.escalation_admin,
                    action="AUTO_ESCALATED",
                    description=msg
                )
                incident.notify_sla_breached(msg)
                return level

        # Check if resolution SLA is in severe danger (>85% elapsed)
        if tracker.is_resolution_at_risk(now, warning_ratio=0.85):
            msg = f"SLA Critical Risk: Incident resolution elapsed >85%. Alert dispatched to {EscalationLevel.LEVEL_3_SYS_ADMIN}."
            incident.notify_sla_warning(msg)
            return EscalationLevel.LEVEL_3_SYS_ADMIN

        return None
