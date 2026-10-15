from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from backend.app.domain.models.enums import IncidentStatus
from backend.app.domain.exceptions import InvalidStateTransitionException

if TYPE_CHECKING:
    from backend.app.domain.models.incident import Incident
    from backend.app.domain.models.user import User, Technician


class IncidentState(ABC):
    """Abstract State in the State Design Pattern for Incident Lifecycle."""

    @property
    @abstractmethod
    def status(self) -> IncidentStatus:
        """Returns the domain enum status corresponding to this state."""
        pass

    def classify(self, incident: "Incident", category: str, actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.CLASSIFIED.value, "Cannot classify from current state.")

    def assign(self, incident: "Incident", technician: "Technician", actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.ASSIGNED.value, "Cannot assign from current state.")

    def acknowledge(self, incident: "Incident", actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.ACKNOWLEDGED.value, "Cannot acknowledge from current state.")

    def start_investigation(self, incident: "Incident", notes: str, actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.IN_PROGRESS.value, "Cannot start investigation from current state.")

    def resolve(self, incident: "Incident", resolution_details: str, actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.RESOLVED.value, "Cannot resolve an incident from current state.")

    def verify(self, incident: "Incident", is_confirmed: bool, actor: "User", feedback: str = "") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.VERIFIED.value, "Cannot verify an incident from current state.")

    def close(self, incident: "Incident", actor: "User") -> None:
        raise InvalidStateTransitionException(self.status.value, IncidentStatus.CLOSED.value, "Cannot close an incident from current state.")


class NewState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.NEW

    def classify(self, incident: "Incident", category: str, actor: "User") -> None:
        incident.category = category
        incident.transition_to(ClassifiedState(), actor, f"Incident classified as {category}")

    def assign(self, incident: "Incident", technician: "Technician", actor: "User") -> None:
        # Direct auto-assign after auto-classification
        incident.assigned_technician = technician
        incident.transition_to(AssignedState(), actor, f"Incident directly assigned to {technician.full_name}")


class ClassifiedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.CLASSIFIED

    def assign(self, incident: "Incident", technician: "Technician", actor: "User") -> None:
        incident.assigned_technician = technician
        incident.transition_to(AssignedState(), actor, f"Assigned to Technician {technician.full_name} ({technician.id})")


class AssignedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.ASSIGNED

    def acknowledge(self, incident: "Incident", actor: "User") -> None:
        incident.transition_to(AcknowledgedState(), actor, f"Incident acknowledged by {actor.full_name}")

    def assign(self, incident: "Incident", technician: "Technician", actor: "User") -> None:
        # Re-assignment before acknowledgment
        prev_tech = incident.assigned_technician.full_name if incident.assigned_technician else "None"
        incident.assigned_technician = technician
        incident.record_action(actor, "REASSIGNED", f"Reassigned from {prev_tech} to {technician.full_name}")


class AcknowledgedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.ACKNOWLEDGED

    def start_investigation(self, incident: "Incident", notes: str, actor: "User") -> None:
        incident.investigation_notes.append(notes)
        incident.transition_to(InProgressState(), actor, f"Investigation started: {notes}")


class InProgressState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.IN_PROGRESS

    def start_investigation(self, incident: "Incident", notes: str, actor: "User") -> None:
        # Append additional investigation notes
        incident.investigation_notes.append(notes)
        incident.record_action(actor, "INVESTIGATION_UPDATE", notes)

    def resolve(self, incident: "Incident", resolution_details: str, actor: "User") -> None:
        incident.resolution_details = resolution_details
        incident.transition_to(ResolvedState(), actor, f"Incident marked resolved: {resolution_details}")


class ResolvedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.RESOLVED

    def verify(self, incident: "Incident", is_confirmed: bool, actor: "User", feedback: str = "") -> None:
        if is_confirmed:
            incident.resolution_feedback = feedback
            incident.transition_to(VerifiedState(), actor, f"Resolution verified by {actor.full_name}. Feedback: {feedback}")
        else:
            # Reopen to InProgress
            incident.resolution_feedback = f"Verification failed: {feedback}"
            incident.transition_to(InProgressState(), actor, f"Resolution rejected by {actor.full_name}. Re-opened.")


class VerifiedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.VERIFIED

    def close(self, incident: "Incident", actor: "User") -> None:
        incident.transition_to(ClosedState(), actor, f"Incident officially closed by {actor.full_name}")


class ClosedState(IncidentState):
    @property
    def status(self) -> IncidentStatus:
        return IncidentStatus.CLOSED
    # Terminal state - no further transitions permitted
