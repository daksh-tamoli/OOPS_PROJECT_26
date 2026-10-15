from datetime import datetime, timezone
from typing import List, Optional
import uuid

from backend.app.domain.models.enums import IncidentStatus, Priority, Impact, Urgency
from backend.app.domain.models.user import User, Technician
from backend.app.domain.models.service import ITService
from backend.app.domain.models.sla import SLAStatusTracker, SLATarget
from backend.app.domain.models.audit import AuditRecord
from backend.app.domain.states.incident_state import IncidentState, NewState
from backend.app.domain.observers.interface import IIncidentObserver


class Incident:
    """
    Incident Aggregate Root.
    Acts as the Context in the State Pattern and Subject in the Observer Pattern.
    Demonstrates encapsulation, composition, and domain-driven design.
    """
    def __init__(
        self,
        title: str,
        description: str,
        service: ITService,
        reporter: User,
        impact: Impact = Impact.MEDIUM,
        urgency: Urgency = Urgency.MEDIUM,
        priority: Priority = Priority.P3,
        category: str = "General",
        incident_id: Optional[str] = None,
        created_at: Optional[datetime] = None,
        sla_target: Optional[SLATarget] = None
    ):
        self._id = incident_id or f"INC-{uuid.uuid4().hex[:6].upper()}"
        self.title = title
        self.description = description
        self.service = service
        self.reporter = reporter
        self.impact = impact
        self.urgency = urgency
        self.priority = priority
        self.category = category
        self.created_at = created_at or datetime.now(timezone.utc)

        # State Pattern Context
        self._state: IncidentState = NewState()

        # Associated Technician (Aggregation)
        self.assigned_technician: Optional[Technician] = None

        # Investigation and Resolution details
        self.investigation_notes: List[str] = []
        self.resolution_details: str = ""
        self.resolution_feedback: str = ""

        # Composition: Audit trail & SLA tracker
        target = sla_target or service.sla_policy.get_target(priority)
        self.sla_tracker = SLAStatusTracker(created_at=self.created_at, target=target)
        self.audit_logs: List[AuditRecord] = []

        # Observer Pattern: Registered listeners
        self._observers: List[IIncidentObserver] = []

        # Duplicate / Correlation relations
        self.parent_incident_id: Optional[str] = None
        self.is_duplicate: bool = False
        self.duplicate_of_id: Optional[str] = None

        # Initial audit entry
        self.record_action(
            actor=reporter,
            action="REPORTED",
            description=f"Incident '{self.title}' reported by {reporter.full_name} for service {service.name}"
        )

    # ------------------ Encapsulated Properties ------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> IncidentStatus:
        return self._state.status

    @property
    def state(self) -> IncidentState:
        return self._state

    # ------------------ Observer Management ------------------

    def attach_observer(self, observer: IIncidentObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: IIncidentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_state_changed(self, audit_record: AuditRecord) -> None:
        for observer in self._observers:
            observer.on_state_changed(self, audit_record)

    def notify_sla_warning(self, message: str) -> None:
        for observer in self._observers:
            observer.on_sla_warning(self, message)

    def notify_sla_breached(self, message: str) -> None:
        for observer in self._observers:
            observer.on_sla_breached(self, message)

    # ------------------ State Pattern Transitions ------------------

    def transition_to(self, new_state: IncidentState, actor: User, description: str) -> None:
        """Transitions state, records immutable audit record, and notifies observers."""
        prev_status = self.status.value
        self._state = new_state
        new_status = new_state.status.value

        # Record audit log
        record = self.record_action(
            actor=actor,
            action=f"STATE_TRANSITION_{new_status}",
            description=description,
            prev_state=prev_status,
            new_state=new_status
        )

        # Notify observers
        self.notify_state_changed(record)

    def record_action(
        self,
        actor: User,
        action: str,
        description: str,
        prev_state: Optional[str] = None,
        new_state: Optional[str] = None
    ) -> AuditRecord:
        record = AuditRecord(
            incident_id=self._id,
            actor_id=actor.id,
            actor_name=actor.full_name,
            action=action,
            previous_state=prev_state or self.status.value,
            new_state=new_state or self.status.value,
            description=description
        )
        self.audit_logs.append(record)
        return record

    # Delegated domain operations via State Pattern
    def classify(self, category: str, actor: User) -> None:
        self._state.classify(self, category, actor)

    def assign(self, technician: Technician, actor: User) -> None:
        technician.allocate_ticket()
        self._state.assign(self, technician, actor)

    def acknowledge(self, actor: User) -> None:
        self.sla_tracker.mark_responded()
        self._state.acknowledge(self, actor)

    def start_investigation(self, notes: str, actor: User) -> None:
        self._state.start_investigation(self, notes, actor)

    def resolve(self, resolution_details: str, actor: User) -> None:
        self.sla_tracker.mark_resolved()
        if self.assigned_technician:
            self.assigned_technician.release_ticket()
        self._state.resolve(self, resolution_details, actor)

    def verify(self, is_confirmed: bool, actor: User, feedback: str = "") -> None:
        self._state.verify(self, is_confirmed, actor, feedback)

    def close(self, actor: User) -> None:
        self._state.close(self, actor)
